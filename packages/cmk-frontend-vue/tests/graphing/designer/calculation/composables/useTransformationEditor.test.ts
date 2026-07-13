/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render } from '@testing-library/vue'
import { defineComponent } from 'vue'

import { Response } from '@/components/CmkSuggestions'

import {
  type TransformationEditor,
  useTransformationEditor
} from '@/graphing/designer/calculation/composables/useTransformationEditor'
import type { GraphItem, ItemId } from '@/graphing/designer/types'

import { formulaItem, items } from '../../fixtures'

function mountEditor(
  editorItems: GraphItem[] = items,
  editedItemId: ItemId | null = null
): ReturnType<typeof useTransformationEditor> {
  let api!: ReturnType<typeof useTransformationEditor>
  render(
    defineComponent({
      setup() {
        api = useTransformationEditor(() => editorItems, 'rrd', editedItemId)
        return () => null
      }
    })
  )
  return api
}

function optionNames(editor: TransformationEditor): string[] {
  const options = editor.metricOptions.value
  return options.type === 'fixed'
    ? options.suggestions.flatMap((s) => ('name' in s && s.name !== null ? [s.name] : []))
    : []
}

test('offers only non-dynamic items in the active domain', () => {
  const editor = mountEditor()
  expect(editor.metricOptions.value.type).toBe('fixed')
  expect(optionNames(editor)).toEqual(['A', 'B', 'D'])
})

test('excludes the edited item and items referring back to it', () => {
  const editorItems = [
    ...items,
    formulaItem('F'),
    formulaItem('G', { ast: { op: 'ref', id: 'F' } })
  ]
  const editor = mountEditor(editorItems, 'F')
  expect(optionNames(editor)).toEqual(['A', 'B', 'D'])
})

test('selectItem accepts only eligible ids', () => {
  const editor = mountEditor()
  editor.selectItem('A')
  expect(editor.selectedId.value).toBe('A')

  editor.selectItem('C') // dynamic
  editor.selectItem('E') // other domain
  editor.selectItem('Z') // unknown
  expect(editor.selectedId.value).toBe('A')
})

function errorsOf(result: ReturnType<TransformationEditor['commit']>): string[] {
  return 'errors' in result ? result.errors : []
}

test('commit builds a percentile AST when valid, explains the problem otherwise', () => {
  const editor = mountEditor()
  expect(errorsOf(editor.commit())).toEqual(['Select the metric to transform.'])

  editor.selectItem('A')
  editor.percentile.value = '90'
  expect(editor.commit()).toEqual({
    ast: { op: 'percentile', percentile: 90, operand: { op: 'ref', id: 'A' } }
  })

  editor.percentile.value = '150'
  expect(errorsOf(editor.commit())).toEqual(['Enter a percentile between 0 and 100.'])
  expect(editor.errors.value).toEqual(['Enter a percentile between 0 and 100.'])

  editor.percentile.value = null
  expect(errorsOf(editor.commit())).toEqual(['Enter a percentile between 0 and 100.'])

  editor.reset()
  expect(editor.errors.value).toEqual([])
})

test('commit reports both problems when nothing is selected and the percentile is invalid', () => {
  const editor = mountEditor()
  editor.percentile.value = 'abc'
  expect(errorsOf(editor.commit())).toEqual([
    'Select the metric to transform.',
    'Enter a percentile between 0 and 100.'
  ])
})

test('accepts the inclusive percentile boundaries 0 and 100', () => {
  const editor = mountEditor()
  editor.selectItem('A')

  editor.percentile.value = '0'
  expect(editor.commit()).toEqual({
    ast: { op: 'percentile', percentile: 0, operand: { op: 'ref', id: 'A' } }
  })

  editor.percentile.value = '100'
  expect(editor.commit()).toEqual({
    ast: { op: 'percentile', percentile: 100, operand: { op: 'ref', id: 'A' } }
  })
})

test('commit rejects an empty or whitespace percentile instead of reading it as 0', () => {
  const editor = mountEditor()
  editor.selectItem('A')

  editor.percentile.value = ''
  expect('errors' in editor.commit()).toBe(true)

  editor.percentile.value = '   '
  expect('errors' in editor.commit()).toBe(true)
})

test('reset clears the selection and restores the default percentile', () => {
  const editor = mountEditor()
  editor.selectItem('A')
  editor.percentile.value = '50'
  editor.reset()
  expect(editor.selectedId.value).toBeNull()
  expect(editor.percentile.value).toBe('95')
})

async function suggestionNames(editor: TransformationEditor, query: string): Promise<string[]> {
  const options = editor.percentileOptions
  if (options.type !== 'callback-filtered') {
    throw new Error('expected callback-filtered percentile options')
  }
  const response = await options.querySuggestions(query)
  if (!(response instanceof Response)) {
    throw new Error('expected a suggestion response')
  }
  return response.choices.flatMap((choice) =>
    'name' in choice && choice.name !== null ? [choice.name] : []
  )
}

test('percentile suggestions offer the common values for an empty query', async () => {
  const editor = mountEditor()
  expect(await suggestionNames(editor, '')).toEqual(['50', '75', '90', '95', '99'])
})

test('percentile suggestions filter by prefix, injecting the typed value', async () => {
  const editor = mountEditor()
  expect(await suggestionNames(editor, '9')).toEqual(['9', '90', '95', '99'])
})

test('percentile suggestions inject a valid custom value', async () => {
  const editor = mountEditor()
  expect(await suggestionNames(editor, '80')).toEqual(['80'])
  expect(await suggestionNames(editor, '99.5')).toEqual(['99.5'])
})

test('percentile suggestions ignore out-of-range custom values', async () => {
  const editor = mountEditor()
  expect(await suggestionNames(editor, '150')).toEqual([])
})
