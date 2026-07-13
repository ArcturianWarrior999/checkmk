/**
 * Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { type Ref, ref } from 'vue'

export default function useDragging<ContainerElement extends HTMLElement>(
  containerRef: Ref<ContainerElement | null>,
  options: {
    itemSelector?: string
  } = {}
): {
  /** Dragged item's index, or null if the drag source is outside any item. */
  dragStart: (event: DragEvent) => number | null
  dragEnd: (event: DragEvent) => void
  dragging: (event: DragEvent) => { draggedIndex: number; targetIndex: number } | null
} {
  const itemSelector = options.itemSelector ?? 'tr'

  /**
   * This is a workaround for the fact that a bug in Firefox prevents us from
   * using the clientX/clientY values from a drag event to get the mouse
   * position
   *
   * ref: https://bugzilla.mozilla.org/show_bug.cgi?id=505521
   */
  const clientY = ref(0)

  function update(event: MouseEvent) {
    clientY.value = event.clientY
  }

  function draggedItemOf(event: DragEvent): Element | null {
    return (event.target as Element | null)?.closest(itemSelector) ?? null
  }

  function itemsOf(container: ContainerElement): Element[] {
    return [...container.children].filter((child) => child.matches(itemSelector))
  }

  function dragStart(event: DragEvent): number | null {
    const draggedItem = draggedItemOf(event)
    draggedItem?.classList.add('dragging')
    update(event)
    window.addEventListener('dragover', update)
    if (draggedItem === null || containerRef.value === null) {
      return null
    }
    const draggedIndex = itemsOf(containerRef.value).indexOf(draggedItem)
    return draggedIndex === -1 ? null : draggedIndex
  }

  function dragEnd(event: DragEvent) {
    draggedItemOf(event)?.classList.remove('dragging')
    window.removeEventListener('dragover', update)
  }

  function dragging(event: DragEvent): { draggedIndex: number; targetIndex: number } | null {
    if (containerRef.value === null || clientY.value === 0) {
      return null
    }
    const items = itemsOf(containerRef.value)
    const draggedItem = draggedItemOf(event)
    const draggedIndex = draggedItem ? items.indexOf(draggedItem) : -1
    if (draggedIndex === -1) {
      return null
    }

    function itemMiddlePoint(item: Element) {
      const itemRect = item.getBoundingClientRect()
      return itemRect.top + itemRect.height / 2
    }

    let targetIndex = -1
    for (let index = draggedIndex - 1; index >= 0; index--) {
      if (clientY.value >= itemMiddlePoint(items[index]!)) {
        break
      }
      targetIndex = index
    }
    for (let index = draggedIndex + 1; index < items.length; index++) {
      if (clientY.value <= itemMiddlePoint(items[index]!)) {
        break
      }
      targetIndex = index
    }

    if (draggedIndex === targetIndex || targetIndex === -1) {
      return null
    }
    return { draggedIndex, targetIndex }
  }

  return { dragStart, dragEnd, dragging }
}
