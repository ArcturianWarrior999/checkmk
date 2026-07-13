/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import {
  FormulaParseError,
  type ParseErrorDetail,
  parseFormula
} from '@/graphing/designer/calculation/formula'

import { parseOrThrow as parse } from '../../fixtures'

function parseError(source: string): FormulaParseError {
  const result = parseFormula(source)
  if (!('error' in result)) {
    throw new Error(`expected a parse error for: ${source}`)
  }
  return result.error
}

test('parses a simple binary expression', () => {
  expect(parse('A + B')).toEqual({
    op: 'sum',
    operands: [
      { op: 'ref', id: 'A' },
      { op: 'ref', id: 'B' }
    ]
  })
})

test('gives * / higher precedence than + -', () => {
  expect(parse('A + B * C')).toEqual({
    op: 'sum',
    operands: [
      { op: 'ref', id: 'A' },
      {
        op: 'product',
        operands: [
          { op: 'ref', id: 'B' },
          { op: 'ref', id: 'C' }
        ]
      }
    ]
  })
})

test('is left-associative', () => {
  expect(parse('A - B - C')).toEqual({
    op: 'difference',
    operands: [
      {
        op: 'difference',
        operands: [
          { op: 'ref', id: 'A' },
          { op: 'ref', id: 'B' }
        ]
      },
      { op: 'ref', id: 'C' }
    ]
  })
})

test('honours parentheses', () => {
  expect(parse('(A + B) * C')).toEqual({
    op: 'product',
    operands: [
      {
        op: 'sum',
        operands: [
          { op: 'ref', id: 'A' },
          { op: 'ref', id: 'B' }
        ]
      },
      { op: 'ref', id: 'C' }
    ]
  })
})

test('parses multi-letter references', () => {
  expect(parse('AA + AB')).toEqual({
    op: 'sum',
    operands: [
      { op: 'ref', id: 'AA' },
      { op: 'ref', id: 'AB' }
    ]
  })
})

test('parses variadic function calls', () => {
  expect(parse('avg(A, B, C)')).toEqual({
    op: 'avg',
    operands: [
      { op: 'ref', id: 'A' },
      { op: 'ref', id: 'B' },
      { op: 'ref', id: 'C' }
    ]
  })
})

test('maps the sum() function to fsum (distinct from the + operator)', () => {
  expect(parse('sum(A)')).toEqual({ op: 'fsum', operands: [{ op: 'ref', id: 'A' }] })
})

test('parses decimal and negative number literals', () => {
  expect(parse('2.5 + A')).toEqual({
    op: 'sum',
    operands: [
      { op: 'num', value: 2.5 },
      { op: 'ref', id: 'A' }
    ]
  })
  expect(parse('.5')).toEqual({ op: 'num', value: 0.5 })
  expect(parse('-3')).toEqual({ op: 'num', value: -3 })
})

test('parses unary minus on a reference as 0 - ref', () => {
  expect(parse('-A')).toEqual({
    op: 'difference',
    operands: [
      { op: 'num', value: 0 },
      { op: 'ref', id: 'A' }
    ]
  })
})

test('binds unary minus tighter than multiplication', () => {
  expect(parse('2 * -3')).toEqual({
    op: 'product',
    operands: [
      { op: 'num', value: 2 },
      { op: 'num', value: -3 }
    ]
  })
  expect(parse('-A * B')).toEqual({
    op: 'product',
    operands: [
      {
        op: 'difference',
        operands: [
          { op: 'num', value: 0 },
          { op: 'ref', id: 'A' }
        ]
      },
      { op: 'ref', id: 'B' }
    ]
  })
})

test('parses unary minus on a parenthesized expression', () => {
  expect(parse('-(A + B)')).toEqual({
    op: 'difference',
    operands: [
      { op: 'num', value: 0 },
      {
        op: 'sum',
        operands: [
          { op: 'ref', id: 'A' },
          { op: 'ref', id: 'B' }
        ]
      }
    ]
  })
})

test('parses nested function calls', () => {
  expect(parse('avg(min(A, B), C)')).toEqual({
    op: 'avg',
    operands: [
      {
        op: 'min',
        operands: [
          { op: 'ref', id: 'A' },
          { op: 'ref', id: 'B' }
        ]
      },
      { op: 'ref', id: 'C' }
    ]
  })
})

test('rejects exponent notation (no e-notation in the grammar)', () => {
  expect('error' in parseFormula('1e-7')).toBe(true)
})

test('reports the error position at the point of failure', () => {
  const error = parseError('(A +')
  expect(error.detail).toEqual({ code: 'unexpected-end' })
  expect(error.position).toBe(4)
})

test('reports the error position of an unexpected trailing token', () => {
  const error = parseError('A B')
  expect(error.detail).toEqual({ code: 'unexpected-token', token: 'B' })
  expect(error.position).toBe(2)
})

test('rejects a malformed number', () => {
  const error = parseError('.')
  expect(error.detail).toEqual({ code: 'invalid-number' })
  expect(error.position).toBe(0)
})

test('rejects a trailing token after a complete expression', () => {
  const error = parseError('A + B C')
  expect(error.detail).toEqual({ code: 'unexpected-token', token: 'C' })
  expect(error.position).toBe(6)
})

test('rejects the percent operator (percentile is not typed here)', () => {
  const error = parseError('A % B')
  expect(error.detail).toEqual({ code: 'unexpected-character', character: '%' })
  expect(error.position).toBe(2)
})

test('rejects an empty formula', () => {
  const error = parseError('   ')
  expect(error.detail).toEqual({ code: 'empty-formula' })
  expect(error.position).toBe(0)
})

test('errors are FormulaParseError instances', () => {
  expect(parseError('A B')).toBeInstanceOf(FormulaParseError)
})

test('rejects a function call without arguments', () => {
  const error = parseError('min()')
  expect(error.detail).toEqual({ code: 'empty-function-args', name: 'min' })
  expect(error.position).toBe(4)
})

test('lists the available functions for an unknown function name', () => {
  const error = parseError('foo(A)')
  const detail: ParseErrorDetail = error.detail
  expect(detail).toEqual({
    code: 'unknown-function',
    name: 'foo',
    available: ['avg', 'min', 'max', 'sum']
  })
})

test('expects an opening parenthesis after a function name', () => {
  const error = parseError('avg A')
  expect(error.detail).toEqual({ code: 'expected-token', symbol: '(' })
  expect(error.position).toBe(4)
})

test('expects a closing parenthesis for an unclosed group', () => {
  const error = parseError('(A')
  expect(error.detail).toEqual({ code: 'expected-token', symbol: ')' })
  expect(error.position).toBe(2)
})

test('rejects excessive nesting instead of overflowing the call stack', () => {
  const parens = parseError(`${'('.repeat(1000)}A${')'.repeat(1000)}`)
  expect(parens.detail).toEqual({ code: 'nesting-too-deep' })
  const minuses = parseError(`${'-'.repeat(1000)}1`)
  expect(minuses.detail).toEqual({ code: 'nesting-too-deep' })
})

test('parses formulas nested well below the cap', () => {
  expect(parse(`${'('.repeat(32)}A${')'.repeat(32)}`)).toEqual({ op: 'ref', id: 'A' })
})
