/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import {
  type ArithmeticNode,
  BINARY_OPERATORS,
  FUNCTION_NAMES,
  isBinary,
  isFunction
} from './grammar'

/** Decimal text for a finite number; `String(value)` exponent form is expanded to plain decimal (the grammar has no e-notation). */
function numberToText(value: number): string {
  if (!Number.isFinite(value)) {
    throw new Error(`Cannot serialize non-finite number: ${value}`)
  }
  const text = String(value)
  return text.includes('e') ? expandExponent(text) : text
}

/** Expand `String(value)` exponent notation ("1.5e-7", "1e+21") to plain decimal text. */
function expandExponent(text: string): string {
  const [mantissa, exponentText] = text.split('e') as [string, string]
  const exponent = Number(exponentText)
  const negative = mantissa.startsWith('-')
  const unsigned = negative ? mantissa.slice(1) : mantissa
  const dot = unsigned.indexOf('.')
  const digits = unsigned.replace('.', '')
  const pointIndex = (dot === -1 ? unsigned.length : dot) + exponent
  let expanded: string
  if (pointIndex <= 0) {
    expanded = `0.${'0'.repeat(-pointIndex)}${digits}`
  } else if (pointIndex >= digits.length) {
    expanded = digits + '0'.repeat(pointIndex - digits.length)
  } else {
    expanded = `${digits.slice(0, pointIndex)}.${digits.slice(pointIndex)}`
  }
  return negative ? `-${expanded}` : expanded
}

/** Serialize an arithmetic AST to its canonical text form. */
export function serializeFormula(node: ArithmeticNode): string {
  switch (node.op) {
    case 'ref':
      return node.id
    case 'num':
      return numberToText(node.value)
  }
  if (isFunction(node)) {
    return `${FUNCTION_NAMES[node.op]}(${node.operands.map(serializeFormula).join(', ')})`
  }
  const [left, right] = node.operands
  const { symbol, precedence } = BINARY_OPERATORS[node.op]
  return `${serializeChild(left, precedence, 'left')} ${symbol} ${serializeChild(right, precedence, 'right')}`
}

function serializeChild(
  child: ArithmeticNode,
  parentPrecedence: number,
  side: 'left' | 'right'
): string {
  const text = serializeFormula(child)
  if (!isBinary(child)) {
    return text
  }
  const childPrecedence = BINARY_OPERATORS[child.op].precedence
  const needsParens =
    childPrecedence < parentPrecedence || (childPrecedence === parentPrecedence && side === 'right')
  return needsParens ? `(${text})` : text
}
