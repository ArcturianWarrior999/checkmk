/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { serializeFormula } from '@/graphing/designer/calculation/formula'

import { parseOrThrow as parse } from '../../fixtures'

test('serializes with spaces around binary operators', () => {
  expect(serializeFormula(parse('A+B'))).toBe('A + B')
})

test('adds parentheses only where precedence requires', () => {
  expect(serializeFormula(parse('A + B * C'))).toBe('A + B * C')
  expect(serializeFormula(parse('(A + B) * C'))).toBe('(A + B) * C')
})

test('preserves right-hand grouping for non-associative operators', () => {
  expect(serializeFormula(parse('A - (B - C)'))).toBe('A - (B - C)')
  expect(serializeFormula(parse('A - B - C'))).toBe('A - B - C')
})

test('serializes function calls, mapping fsum back to sum', () => {
  expect(serializeFormula(parse('avg(A, B)'))).toBe('avg(A, B)')
  expect(serializeFormula(parse('sum(A)'))).toBe('sum(A)')
})

test('serializes negative literals', () => {
  expect(serializeFormula({ op: 'num', value: -3 })).toBe('-3')
})

test('serializes a unary-minus source as its 0 - x rewrite', () => {
  expect(serializeFormula(parse('-A'))).toBe('0 - A')
})

test('expands exponent notation to plain decimal', () => {
  expect(serializeFormula({ op: 'num', value: 1e-7 })).toBe('0.0000001')
  expect(serializeFormula({ op: 'num', value: 1e21 })).toBe('1000000000000000000000')
  expect(serializeFormula({ op: 'num', value: -1.5e-8 })).toBe('-0.000000015')
})

test('round-trips extreme values exactly', () => {
  for (const value of [1e-30, -1e-30, 5e-324, 1.7976931348623157e308, 123456.789e-40]) {
    const text = serializeFormula({ op: 'num', value })
    expect(text).not.toContain('e')
    expect(parse(text)).toEqual({ op: 'num', value })
  }
})

test('throws on non-finite numbers', () => {
  expect(() => serializeFormula({ op: 'num', value: Number.NaN })).toThrow()
  expect(() => serializeFormula({ op: 'num', value: Number.POSITIVE_INFINITY })).toThrow()
})

test('round-trips parse -> serialize -> parse', () => {
  for (const source of [
    'A + B * C',
    '(A + B) * C',
    'A - (B - C)',
    'avg(A, B) / sum(C)',
    '-A * B',
    '0.0000001 + A'
  ]) {
    const ast = parse(source)
    expect(parse(serializeFormula(ast))).toEqual(ast)
  }
})
