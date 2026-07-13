/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { type Formula, isArithmetic } from '@/graphing/designer/calculation/formula'

const PERCENTILE: Formula = { op: 'percentile', percentile: 95, operand: { op: 'ref', id: 'A' } }

test('accepts refs, numbers, binary and function trees', () => {
  expect(isArithmetic({ op: 'ref', id: 'A' })).toBe(true)
  expect(isArithmetic({ op: 'num', value: 1 })).toBe(true)
  expect(
    isArithmetic({
      op: 'sum',
      operands: [
        { op: 'ref', id: 'A' },
        { op: 'num', value: 1 }
      ]
    })
  ).toBe(true)
  expect(isArithmetic({ op: 'avg', operands: [{ op: 'ref', id: 'A' }] })).toBe(true)
})

test('rejects a top-level percentile', () => {
  expect(isArithmetic(PERCENTILE)).toBe(false)
})

test('rejects a percentile nested inside operands', () => {
  expect(isArithmetic({ op: 'sum', operands: [{ op: 'ref', id: 'B' }, PERCENTILE] })).toBe(false)
  expect(isArithmetic({ op: 'max', operands: [PERCENTILE] })).toBe(false)
})
