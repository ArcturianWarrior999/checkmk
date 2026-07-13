/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { ref } from 'vue'

import useDragging from '@/lib/useDragging'

function stubRect(element: Element, top: number, height: number): void {
  element.getBoundingClientRect = () =>
    ({
      top,
      height,
      bottom: top + height,
      left: 0,
      right: 100,
      width: 100,
      x: 0,
      y: top,
      toJSON: () => ({})
    }) as DOMRect
}

// useDragging reads the cursor from window dragover events (Firefox reports
// clientY=0 on drag events); only dragStart seeds it from the event itself.
function dragEventAt(target: Element, clientY = 0): DragEvent {
  return { target, clientY } as unknown as DragEvent
}

function moveCursor(clientY: number): void {
  window.dispatchEvent(new MouseEvent('dragover', { clientY }))
}

function makeRow(handleClass: string): HTMLTableRowElement {
  const row = document.createElement('tr')
  const cell = document.createElement('td')
  const handle = document.createElement('div')
  handle.className = handleClass
  cell.appendChild(handle)
  row.appendChild(cell)
  return row
}

function makeGroupedTable(): { table: HTMLTableElement; handles: HTMLElement[] } {
  const table = document.createElement('table')
  const thead = document.createElement('thead')
  thead.appendChild(makeRow('head-handle'))
  table.appendChild(thead)

  const tops = [0, 40, 180]
  const heights = [40, 140, 40]
  const handles: HTMLElement[] = []
  for (let index = 0; index < 3; index++) {
    const group = document.createElement('tbody')
    group.className = 'group'
    group.appendChild(makeRow('handle'))
    stubRect(group, tops[index]!, heights[index]!)
    table.appendChild(group)
    handles.push(group.querySelector('.handle')!)
  }
  return { table, handles }
}

describe('with an itemSelector', () => {
  function mountGroupedDragging() {
    const { table, handles } = makeGroupedTable()
    return { handles, ...useDragging(ref(table), { itemSelector: 'tbody.group' }) }
  }

  test('indices ignore non-matching children like the thead', () => {
    const { handles, dragStart, dragging, dragEnd } = mountGroupedDragging()

    expect(dragStart(dragEventAt(handles[0]!, 20))).toBe(0)
    moveCursor(120)

    expect(dragging(dragEventAt(handles[0]!))).toEqual({ draggedIndex: 0, targetIndex: 1 })
    dragEnd(dragEventAt(handles[0]!))
  })

  test('dragging down past a tall unit requires crossing its midpoint', () => {
    const { handles, dragStart, dragging, dragEnd } = mountGroupedDragging()

    dragStart(dragEventAt(handles[0]!, 20))
    moveCursor(100)
    expect(dragging(dragEventAt(handles[0]!))).toBeNull()

    moveCursor(120)
    expect(dragging(dragEventAt(handles[0]!))).toEqual({ draggedIndex: 0, targetIndex: 1 })
    dragEnd(dragEventAt(handles[0]!))
  })

  test('dragging up past a tall unit targets its index', () => {
    const { handles, dragStart, dragging, dragEnd } = mountGroupedDragging()

    dragStart(dragEventAt(handles[2]!, 200))
    moveCursor(100)

    expect(dragging(dragEventAt(handles[2]!))).toEqual({ draggedIndex: 2, targetIndex: 1 })
    dragEnd(dragEventAt(handles[2]!))
  })

  test('the tall unit itself can be dragged past a neighbor', () => {
    const { handles, dragStart, dragging, dragEnd } = mountGroupedDragging()

    dragStart(dragEventAt(handles[1]!, 110))
    moveCursor(210)

    expect(dragging(dragEventAt(handles[1]!))).toEqual({ draggedIndex: 1, targetIndex: 2 })
    dragEnd(dragEventAt(handles[1]!))
  })

  test('returns null while the cursor stays within the dragged unit', () => {
    const { handles, dragStart, dragging, dragEnd } = mountGroupedDragging()

    dragStart(dragEventAt(handles[1]!, 110))
    moveCursor(130)

    expect(dragging(dragEventAt(handles[1]!))).toBeNull()
    dragEnd(dragEventAt(handles[1]!))
  })

  test('returns null until a dragover reports the cursor position', () => {
    const { handles, dragStart, dragging, dragEnd } = mountGroupedDragging()

    dragStart(dragEventAt(handles[2]!, 0))
    expect(dragging(dragEventAt(handles[2]!))).toBeNull()

    moveCursor(100)
    expect(dragging(dragEventAt(handles[2]!))).toEqual({ draggedIndex: 2, targetIndex: 1 })
    dragEnd(dragEventAt(handles[2]!))
  })

  test('returns null for a drag source outside any item', () => {
    const { table } = makeGroupedTable()
    const { dragStart, dragging, dragEnd } = useDragging(ref(table), {
      itemSelector: 'tbody.group'
    })
    const headHandle = table.querySelector('.head-handle')!

    expect(dragStart(dragEventAt(headHandle, 20))).toBeNull()
    moveCursor(120)

    expect(dragging(dragEventAt(headHandle))).toBeNull()
    dragEnd(dragEventAt(headHandle))
  })
})

describe('without an itemSelector (CmkList / GraphDesigner regression pin)', () => {
  test('tr children are the items and the dragged row gets the dragging class', () => {
    const tbody = document.createElement('tbody')
    const handles: HTMLElement[] = []
    for (let index = 0; index < 3; index++) {
      const row = makeRow('handle')
      stubRect(row, index * 40, 40)
      tbody.appendChild(row)
      handles.push(row.querySelector('.handle')!)
    }
    const { dragStart, dragging, dragEnd } = useDragging(ref(tbody))

    expect(dragStart(dragEventAt(handles[0]!, 20))).toBe(0)
    expect(handles[0]!.closest('tr')!.classList.contains('dragging')).toBe(true)

    moveCursor(110) // past the midpoints of rows 1 (60) and 2 (100)
    expect(dragging(dragEventAt(handles[0]!))).toEqual({ draggedIndex: 0, targetIndex: 2 })

    dragEnd(dragEventAt(handles[0]!))
    expect(handles[0]!.closest('tr')!.classList.contains('dragging')).toBe(false)
  })
})
