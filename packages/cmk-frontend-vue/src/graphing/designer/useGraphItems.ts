/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { type ComputedRef, computed, ref } from 'vue'

import { collectDirectRefs } from './calculation/formula'
import { type FormulaDraft, type GraphItem, type ItemId, isFormula, isSingleLine } from './types'

const CHAR_CODE_A = 'A'.charCodeAt(0)

/** Spreadsheet-style id for a 0-based index: 0 -> A, 25 -> Z, 26 -> AA, ... */
function idFromIndex(index: number): ItemId {
  let n = index
  let id = ''
  do {
    id = String.fromCharCode(CHAR_CODE_A + (n % 26)) + id
    n = Math.floor(n / 26) - 1
  } while (n >= 0)
  return id
}

function nextId(items: GraphItem[]): ItemId {
  const used = new Set(items.map((item) => item.id))
  for (let i = 0; ; i++) {
    const candidate = idFromIndex(i)
    if (!used.has(candidate)) {
      return candidate
    }
  }
}

/** Picks the least-used palette color, preferring earlier entries on ties (unused counts as zero). */
function nextColor(items: GraphItem[], palette: readonly string[]): string {
  if (palette.length === 0) {
    return '#000000'
  }
  const counts = new Map<string, number>(palette.map((color) => [color, 0]))
  for (const item of items.filter(isSingleLine)) {
    const count = counts.get(item.color)
    if (count !== undefined) {
      counts.set(item.color, count + 1)
    }
  }
  return palette.reduce((best, color) => (counts.get(color)! < counts.get(best)! ? color : best))
}

export interface GraphItemsStore {
  items: ComputedRef<readonly GraphItem[]>
  /** Id the next added item will get. */
  nextId: ComputedRef<ItemId>
  /** Default color for the next added item. */
  nextColor: ComputedRef<string>
  /** Add a new formula item; returns its assigned id. */
  add: (draft: FormulaDraft) => ItemId
  /** Replace an existing formula item's AST, title and color, keeping line style/visibility. */
  update: (id: ItemId, draft: FormulaDraft) => void
  remove: (id: ItemId) => void
  setVisibility: (ids: ItemId[], visible: boolean) => void
  /** Formula items whose refs (transitively) reach `id` — they break if `id` is deleted. */
  dependentsOf: (id: ItemId) => GraphItem[]
}

/**
 * @param palette Default metric colors to use.
 * @param seed Pre-existing items (e.g. when editing an existing graph).
 */
export function useGraphItems(palette: readonly string[], seed: GraphItem[] = []): GraphItemsStore {
  const items = ref<GraphItem[]>([...seed])

  function requireFormula(id: ItemId): GraphItem {
    const item = items.value.find((candidate) => candidate.id === id)
    if (item === undefined || !isFormula(item)) {
      throw new Error(`No formula item with id "${id}"`)
    }
    return item
  }

  function add(draft: FormulaDraft): ItemId {
    const id = nextId(items.value)
    items.value = [
      ...items.value,
      { id, line_type: 'line', mirrored: false, visible: true, ...draft }
    ]
    return id
  }

  function update(id: ItemId, draft: FormulaDraft): void {
    const existing = requireFormula(id)
    items.value = items.value.map((item) =>
      item.id === id
        ? { ...existing, ast: draft.ast, title: draft.title, color: draft.color }
        : item
    )
  }

  function remove(id: ItemId): void {
    if (!items.value.some((item) => item.id === id)) {
      throw new Error(`No item with id "${id}"`)
    }
    items.value = items.value.filter((item) => item.id !== id)
  }

  function setVisibility(ids: ItemId[], visible: boolean): void {
    const idSet = new Set(ids)
    items.value = items.value.map((item) => (idSet.has(item.id) ? { ...item, visible } : item))
  }

  function dependentsOf(id: ItemId): GraphItem[] {
    const reached = new Set<ItemId>([id])
    let grew = true
    while (grew) {
      grew = false
      for (const item of items.value) {
        if (reached.has(item.id) || !isFormula(item)) {
          continue
        }
        if (collectDirectRefs(item.ast).some((ref) => reached.has(ref))) {
          reached.add(item.id)
          grew = true
        }
      }
    }
    reached.delete(id)
    return items.value.filter((item) => reached.has(item.id))
  }

  return {
    items: computed(() => Object.freeze([...items.value])),
    nextId: computed(() => nextId(items.value)),
    nextColor: computed(() => nextColor(items.value, palette)),
    add,
    update,
    remove,
    setVisibility,
    dependentsOf
  }
}
