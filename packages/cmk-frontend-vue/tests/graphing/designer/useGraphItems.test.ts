/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import {
  DEFAULT_TITLE_MACRO,
  type FormulaDraft,
  type GraphItem,
  type ItemId,
  isSingleLine
} from '@/graphing/designer/types'
import { type GraphItemsStore, useGraphItems } from '@/graphing/designer/useGraphItems'

import { formulaItem, rrdMetricItem, rrdQueryItem } from './fixtures'

const PALETTE: readonly string[] = ['#28a2f3', '#ff8400', '#ec48b6', '#ffd703']
const PALETTE_SIZE = PALETTE.length

function numberDraft(value: number, color = '#123456'): FormulaDraft {
  return { type: 'rrd_formula', ast: { op: 'num', value }, title: DEFAULT_TITLE_MACRO, color }
}

/** Adds the way the UI does: with the store's suggested default color. */
function addWithNextColor(store: GraphItemsStore, value: number): ItemId {
  return store.add(numberDraft(value, store.nextColor.value))
}

function colorOf(item: GraphItem): string | undefined {
  return isSingleLine(item) ? item.color : undefined
}

test('allocates spreadsheet-style ids, wrapping past Z, and returns them', () => {
  const store = useGraphItems(PALETTE)
  const returned: string[] = []
  for (let i = 0; i < 28; i++) {
    returned.push(store.add(numberDraft(i)))
  }
  const ids = store.items.value.map((item) => item.id)
  expect(ids).toEqual(returned)
  expect(ids[0]).toBe('A')
  expect(ids[25]).toBe('Z')
  expect(ids[26]).toBe('AA')
  expect(ids[27]).toBe('AB')
})

test('fills the smallest unused id around a seed', () => {
  const store = useGraphItems(PALETTE, [rrdMetricItem('A', { color: PALETTE[0]! })])
  expect(store.add(numberDraft(1))).toBe('B')
})

test('assigns distinct palette colours and cycles once exhausted', () => {
  const store = useGraphItems(PALETTE)
  for (let i = 0; i < PALETTE_SIZE + 1; i++) {
    addWithNextColor(store, i)
  }
  const colors = store.items.value.map(colorOf)
  expect(new Set(colors.slice(0, PALETTE_SIZE)).size).toBe(PALETTE_SIZE)
  expect(colors[PALETTE_SIZE]).toBe(colors[0]) // wraps to the first palette entry
  expect(colors.every((color) => color !== undefined && PALETTE.includes(color))).toBe(true)
})

test('picks the least-used colour when the palette is exhausted unevenly', () => {
  const seed: GraphItem[] = [
    rrdMetricItem('A', { color: PALETTE[0]! }),
    rrdMetricItem('B', { color: PALETTE[1]! }),
    rrdMetricItem('C', { color: PALETTE[1]! }),
    rrdMetricItem('D', { color: PALETTE[2]! }),
    rrdMetricItem('E', { color: PALETTE[3]! })
  ]
  const store = useGraphItems(PALETTE, seed)
  addWithNextColor(store, 0)
  expect(colorOf(store.items.value[5]!)).toBe(PALETTE[0])
})

test('the counter skips a colour already used by a single-line item', () => {
  const store = useGraphItems(PALETTE, [rrdMetricItem('A', { color: PALETTE[0]! })])
  addWithNextColor(store, 0)
  expect(colorOf(store.items.value[1]!)).toBe(PALETTE[1])
})

test('ignores N-line items (no colour) when countering', () => {
  const store = useGraphItems(PALETTE, [rrdQueryItem('A')])
  addWithNextColor(store, 0)
  expect(store.items.value[0]).not.toHaveProperty('color')
  expect(colorOf(store.items.value[1]!)).toBe(PALETTE[0])
})

test('persists the draft title and color and sets display defaults', () => {
  const store = useGraphItems(PALETTE)
  store.add({
    type: 'rrd_formula',
    ast: { op: 'num', value: 1 },
    title: 'My calculation',
    color: '#ec48b6'
  })
  const item = store.items.value[0]!
  expect(item.title).toBe('My calculation')
  expect(item).toMatchObject({
    type: 'rrd_formula',
    color: '#ec48b6',
    line_type: 'line',
    mirrored: false,
    visible: true
  })
})

test('nextId and nextColor preview what the next add assigns', () => {
  const store = useGraphItems(PALETTE, [rrdMetricItem('A', { color: PALETTE[0]! })])
  expect(store.nextId.value).toBe('B')
  expect(store.nextColor.value).toBe(PALETTE[1])
  expect(addWithNextColor(store, 1)).toBe('B')
  expect(store.nextId.value).toBe('C')
  expect(store.nextColor.value).toBe(PALETTE[2])
})

test('suggests black for an empty palette', () => {
  const store = useGraphItems([])
  expect(store.nextColor.value).toBe('#000000')
})

test('does not mutate the seed array', () => {
  const seed = [rrdMetricItem('A')]
  const store = useGraphItems(['#111111'], seed)
  store.add(numberDraft(1))
  expect(seed).toHaveLength(1)
  expect(store.items.value).toHaveLength(2)
})

test('update replaces AST, title and color but keeps id and line style', () => {
  const store = useGraphItems(PALETTE)
  const id = addWithNextColor(store, 1)
  const before = store.items.value[0]!
  store.update(id, {
    type: 'rrd_formula',
    ast: { op: 'num', value: 2 },
    title: 'Renamed',
    color: '#654321'
  })
  const after = store.items.value[0]!
  expect(after).toMatchObject({
    id,
    title: 'Renamed',
    ast: { op: 'num', value: 2 },
    color: '#654321',
    line_type: before.line_type,
    mirrored: before.mirrored,
    visible: before.visible
  })
})

test('update throws for unknown or non-formula targets', () => {
  const store = useGraphItems(PALETTE, [rrdMetricItem('A')])
  const draft = numberDraft(1)
  expect(() => store.update('Z', draft)).toThrow()
  expect(() => store.update('A', draft)).toThrow()
})

test('remove deletes the item and throws for unknown ids', () => {
  const store = useGraphItems(PALETTE)
  const id = store.add(numberDraft(1))
  store.remove(id)
  expect(store.items.value).toHaveLength(0)
  expect(() => store.remove(id)).toThrow()
})

test('setVisibility toggles exactly the given items', () => {
  const store = useGraphItems(PALETTE, [rrdMetricItem('A'), rrdMetricItem('B')])
  store.setVisibility(['A'], false)
  expect(store.items.value.map((item) => item.visible)).toEqual([false, true])
  store.setVisibility(['A', 'B'], true)
  expect(store.items.value.map((item) => item.visible)).toEqual([true, true])
})

test('dependentsOf follows references transitively', () => {
  const store = useGraphItems(PALETTE, [
    rrdMetricItem('A'),
    formulaItem('D', { ast: { op: 'ref', id: 'A' } }),
    formulaItem('F', { ast: { op: 'ref', id: 'D' } }),
    formulaItem('G', {
      ast: { op: 'percentile', percentile: 95, operand: { op: 'ref', id: 'F' } }
    }),
    formulaItem('H', { ast: { op: 'num', value: 1 } })
  ])
  expect(store.dependentsOf('A').map((item) => item.id)).toEqual(['D', 'F', 'G'])
  expect(store.dependentsOf('H')).toEqual([])
})

test('items cannot be mutated past the store', () => {
  const store = useGraphItems(PALETTE, [rrdMetricItem('A')])
  // @ts-expect-error the readonly type forbids push; assert the runtime freeze too
  expect(() => store.items.value.push(rrdMetricItem('B'))).toThrow(TypeError)
  expect(store.items.value).toHaveLength(1)
})
