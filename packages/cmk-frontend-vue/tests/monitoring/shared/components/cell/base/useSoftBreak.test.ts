/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { ref } from 'vue'

import { useSoftBreak } from '@/monitoring/shared/components/cell/base/useSoftBreak'

const ZWSP = '​'

test('inserts a zero-width space after spaces, hyphens, underscores and dots', () => {
  const result = useSoftBreak(() => 'a b-c_d.e')

  expect(result.value).toBe(`a ${ZWSP}b-${ZWSP}c_${ZWSP}d.${ZWSP}e`)
})

test('breaks long unbroken runs every hardBreakEvery characters', () => {
  const result = useSoftBreak(() => 'abcdefg', 3)

  expect(result.value).toBe(`abc${ZWSP}def${ZWSP}g`)
})

test('leaves short runs without separators untouched', () => {
  const result = useSoftBreak(() => 'abc', 15)

  expect(result.value).toBe('abc')
})

test('recomputes when the source text changes', () => {
  const text = ref('one')
  const result = useSoftBreak(text, 15)

  expect(result.value).toBe('one')

  text.value = 'two three'
  expect(result.value).toBe(`two ${ZWSP}three`)
})
