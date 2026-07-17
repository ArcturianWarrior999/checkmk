/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render } from '@testing-library/vue'
import { vi } from 'vitest'
import { type MaybeRefOrGetter, defineComponent, nextTick, ref } from 'vue'

import { useFormulaEditor } from '@/graphing/designer/calculation/composables/useFormulaEditor'
import type { GraphItem, ItemId } from '@/graphing/designer/types'

import { formulaItem, rrdMetricItem } from '../../fixtures'

const items: GraphItem[] = [rrdMetricItem('A'), rrdMetricItem('B')]

function mountEditor(
  editorItems: MaybeRefOrGetter<GraphItem[]> = () => items,
  editedItemId: ItemId | null = null
) {
  let api!: ReturnType<typeof useFormulaEditor>
  render(
    defineComponent({
      setup() {
        api = useFormulaEditor(editorItems, 'rrd', editedItemId)
        return () => null
      }
    })
  )
  return api
}

test('appendOperator appends the spaced symbol at the end', () => {
  const editor = mountEditor()
  editor.text.value = 'A'
  editor.appendOperator('*')
  expect(editor.text.value).toBe('A * ')
})

test('wrapFunction wraps the whole expression', () => {
  const editor = mountEditor()
  editor.text.value = 'A * B'
  editor.wrapFunction('avg')
  expect(editor.text.value).toBe('avg(A * B)')

  editor.reset()
  editor.wrapFunction('min')
  expect(editor.text.value).toBe('min()')
})

test('appendRef reuses the last operator, defaulting to +', () => {
  const editor = mountEditor()
  editor.text.value = 'A + B'
  editor.appendRef('C')
  expect(editor.text.value).toBe('A + B + C')

  editor.text.value = 'A * B'
  editor.appendRef('C')
  expect(editor.text.value).toBe('A * B * C')

  editor.reset()
  editor.appendRef('C')
  expect(editor.text.value).toBe('C')

  editor.text.value = 'A + '
  editor.appendRef('C')
  expect(editor.text.value).toBe('A + C')
})

test('appendRef inserts directly after an opening parenthesis', () => {
  const editor = mountEditor()
  editor.text.value = 'avg('
  editor.appendRef('C')
  expect(editor.text.value).toBe('avg(C')
})

test('commit returns the AST for a valid formula and errors otherwise', () => {
  const editor = mountEditor()
  editor.text.value = 'A'
  expect(editor.commit()).toEqual({ ast: { op: 'ref', id: 'A' } })

  editor.text.value = 'A +'
  const bad = editor.commit()
  expect('errors' in bad).toBe(true)
  if ('errors' in bad) {
    expect(bad.errors.length).toBeGreaterThan(0)
  }
})

test('isEmpty tracks whether the formula has committable input', () => {
  const editor = mountEditor()
  expect(editor.isEmpty.value).toBe(true)
  editor.text.value = 'A'
  expect(editor.isEmpty.value).toBe(false)
  editor.text.value = '   '
  expect(editor.isEmpty.value).toBe(true)
})

test('commit reports an error for an empty formula', () => {
  const editor = mountEditor()
  const result = editor.commit()
  expect('errors' in result && result.errors).toEqual([
    'The formula is empty; add a metric id (e.g. A) or a number.'
  ])
  expect(editor.errors.value).toEqual([
    'The formula is empty; add a metric id (e.g. A) or a number.'
  ])

  editor.text.value = '   '
  const blank = editor.commit()
  expect('errors' in blank && blank.errors.length).toBeGreaterThan(0)
})

test('commit rejects a formula referencing the edited item itself', () => {
  const editor = mountEditor(() => [...items, formulaItem('F')], 'F')
  editor.text.value = 'F + 1'
  const result = editor.commit()
  expect('errors' in result && result.errors[0]).toContain('cannot reference itself')
})

test('commit rejects a reference cycle through another formula', () => {
  const cyclic = [...items, formulaItem('F'), formulaItem('G', { ast: { op: 'ref', id: 'F' } })]
  const editor = mountEditor(() => cyclic, 'F')
  editor.text.value = 'G + 1'
  const result = editor.commit()
  expect('errors' in result && result.errors[0]).toContain('circular reference')
})

test('shows debounced errors and clears them when the missing item appears', async () => {
  vi.useFakeTimers()
  try {
    const editorItems = ref<GraphItem[]>([rrdMetricItem('A')])
    const editor = mountEditor(() => editorItems.value)

    editor.text.value = 'A + Z'
    await nextTick()
    expect(editor.errors.value).toEqual([]) // debounce still pending
    vi.advanceTimersByTime(300)
    expect(editor.errors.value).toEqual(['Unknown metric or formula "Z".'])

    editorItems.value = [...editorItems.value, rrdMetricItem('Z')]
    await nextTick()
    vi.advanceTimersByTime(300)
    expect(editor.errors.value).toEqual([])
  } finally {
    vi.useRealTimers()
  }
})
