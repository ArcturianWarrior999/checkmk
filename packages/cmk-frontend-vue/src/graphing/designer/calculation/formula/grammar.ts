/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { ItemId } from '../../types'

/** Binary operators, higher precedence binds tighter. */
export const BINARY_OPERATORS = {
  sum: { symbol: '+', precedence: 1 },
  difference: { symbol: '-', precedence: 1 },
  product: { symbol: '*', precedence: 2 },
  fraction: { symbol: '/', precedence: 2 }
} as const

/** Aggregation functions mapped to their text name. */
export const FUNCTION_NAMES = {
  avg: 'avg',
  min: 'min',
  max: 'max',
  fsum: 'sum'
} as const

/** Binary arithmetic operators. */
export type BinaryOp = keyof typeof BINARY_OPERATORS

/** Variadic aggregation functions. */
export type FunctionOp = keyof typeof FUNCTION_NAMES

/** The operator-bar's binary symbols. */
export type OperatorSymbol = (typeof BINARY_OPERATORS)[BinaryOp]['symbol']

/** The operator-bar's function names. */
export type FunctionName = (typeof FUNCTION_NAMES)[FunctionOp]

export type RefNode = { op: 'ref'; id: ItemId }
export type NumNode = { op: 'num'; value: number }

// Interfaces (not type aliases) so members resolve lazily, making the recursive node unions below legal.
export interface BinaryNode<Operand> {
  op: BinaryOp
  operands: [Operand, Operand]
}
export interface FunctionNode<Operand> {
  op: FunctionOp
  operands: [Operand, ...Operand[]]
}

/** The percentile-free subset the text grammar can express (parser output, serializer input). */
export type ArithmeticNode =
  | RefNode
  | NumNode
  | BinaryNode<ArithmeticNode>
  | FunctionNode<ArithmeticNode>

export interface PercentileNode {
  op: 'percentile'
  percentile: number
  operand: Formula
}

/** A full formula AST as the REST API stores it (`CustomGraphFormulaNode`) */
export type Formula =
  | RefNode
  | NumNode
  | BinaryNode<Formula>
  | FunctionNode<Formula>
  | PercentileNode

/** Inverse of {@link BINARY_OPERATORS}: text symbol → operator. */
export const BINARY_OP_BY_SYMBOL: Record<OperatorSymbol, BinaryOp> = Object.fromEntries(
  Object.entries(BINARY_OPERATORS).map(([op, { symbol }]) => [symbol, op])
) as Record<OperatorSymbol, BinaryOp>

/** Whether `ch` is one of the binary operator symbols. */
export function isOperatorSymbol(ch: string): ch is OperatorSymbol {
  return Object.hasOwn(BINARY_OP_BY_SYMBOL, ch)
}

/** Inverse of {@link FUNCTION_NAMES}: text name → function op, undefined for unknown names. */
export const FUNCTION_OP_BY_NAME: Partial<Record<string, FunctionOp>> = Object.fromEntries(
  Object.entries(FUNCTION_NAMES).map(([op, name]) => [name, op])
) as Partial<Record<string, FunctionOp>>

export function isBinary(node: ArithmeticNode): node is BinaryNode<ArithmeticNode>
export function isBinary(node: Formula): node is BinaryNode<Formula>
export function isBinary(node: Formula): boolean {
  return Object.hasOwn(BINARY_OPERATORS, node.op)
}

export function isFunction(node: ArithmeticNode): node is FunctionNode<ArithmeticNode>
export function isFunction(node: Formula): node is FunctionNode<Formula>
export function isFunction(node: Formula): boolean {
  return Object.hasOwn(FUNCTION_NAMES, node.op)
}

/** Narrows to the percentile-free subset the text grammar can express. */
export function isArithmetic(node: Formula): node is ArithmeticNode {
  switch (node.op) {
    case 'percentile':
      return false
    case 'ref':
    case 'num':
      return true
  }
  return node.operands.every(isArithmetic)
}
