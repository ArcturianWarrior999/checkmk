/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import {
  type ApiFormulaNode,
  type Formula,
  fromApiAst,
  toApiAst
} from '@/graphing/designer/calculation/formula'

test.each(['sum', 'difference', 'product', 'fraction'] as const)('round-trips a %s node', (op) => {
  const formula: Formula = {
    op,
    operands: [
      { op: 'ref', id: 'A' },
      { op: 'num', value: 2 }
    ]
  }
  expect(fromApiAst(toApiAst(formula))).toEqual(formula)
})

test.each(['avg', 'min', 'max', 'fsum'] as const)('round-trips a %s node', (op) => {
  const formula: Formula = { op, operands: [{ op: 'ref', id: 'A' }] }
  expect(fromApiAst(toApiAst(formula))).toEqual(formula)
})

test('round-trips a nested percentile formula', () => {
  const formula: Formula = {
    op: 'percentile',
    percentile: 95,
    operand: {
      op: 'sum',
      operands: [
        { op: 'ref', id: 'A' },
        {
          op: 'avg',
          operands: [
            { op: 'ref', id: 'B' },
            { op: 'num', value: 1.5 }
          ]
        }
      ]
    }
  }
  expect(fromApiAst(toApiAst(formula))).toEqual(formula)
})

test('rejects empty function operands', () => {
  const node: ApiFormulaNode = { op: 'avg', operands: [] }
  expect(() => fromApiAst(node)).toThrow("Empty operands in 'avg' node")
})

test('rejects empty function operands in nested nodes', () => {
  const node: ApiFormulaNode = {
    op: 'sum',
    operands: [
      { op: 'ref', id: 'A' },
      { op: 'max', operands: [] }
    ]
  }
  expect(() => fromApiAst(node)).toThrow("Empty operands in 'max' node")
})
