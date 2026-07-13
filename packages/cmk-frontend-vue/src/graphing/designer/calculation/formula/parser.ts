/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import {
  type ArithmeticNode,
  BINARY_OPERATORS,
  BINARY_OP_BY_SYMBOL,
  FUNCTION_NAMES,
  FUNCTION_OP_BY_NAME,
  type OperatorSymbol,
  isOperatorSymbol
} from './grammar'

/** Recursion cap for nested expressions; generous for real formulas, far below the call-stack limit. */
const MAX_NESTING_DEPTH = 64

/** Machine-readable parse problems; translated to user-facing text at the display layer. */
export type ParseErrorDetail =
  | { code: 'empty-formula' }
  | { code: 'invalid-number' }
  | { code: 'unexpected-character'; character: string }
  | { code: 'unexpected-token'; token: string }
  | { code: 'unexpected-end' }
  | { code: 'unknown-function'; name: string; available: string[] }
  | { code: 'empty-function-args'; name: string }
  | { code: 'expected-token'; symbol: string }
  | { code: 'nesting-too-deep' }

export class FormulaParseError extends Error {
  readonly detail: ParseErrorDetail
  /** 0-based index into the source string where the problem was detected. */
  readonly position: number

  constructor(detail: ParseErrorDetail, position: number) {
    super(detail.code)
    this.detail = detail
    this.position = position
  }
}

export type ParseResult = { ast: ArithmeticNode } | { error: FormulaParseError }

type Token =
  | { type: 'ref'; value: string; position: number }
  | { type: 'func'; value: string; position: number }
  | { type: 'num'; value: string; position: number }
  | { type: 'op'; value: OperatorSymbol; position: number }
  | { type: 'lparen' | 'rparen' | 'comma'; value: string; position: number }

class Tokenizer {
  private pos = 0

  constructor(private readonly src: string) {}

  tokenize(): Token[] {
    const tokens: Token[] = []
    while (this.pos < this.src.length) {
      const ch = this.src[this.pos]!
      if (ch === ' ' || ch === '\t' || ch === '\n' || ch === '\r') {
        this.pos++
        continue
      }
      const start = this.pos
      if (ch >= 'A' && ch <= 'Z') {
        tokens.push({
          type: 'ref',
          value: this.consumeWhile((c) => c >= 'A' && c <= 'Z'),
          position: start
        })
      } else if (ch >= 'a' && ch <= 'z') {
        tokens.push({
          type: 'func',
          value: this.consumeWhile((c) => c >= 'a' && c <= 'z'),
          position: start
        })
      } else if ((ch >= '0' && ch <= '9') || ch === '.') {
        const num = this.consumeNumber()
        if (num === null) {
          throw new FormulaParseError({ code: 'invalid-number' }, start)
        }
        tokens.push({ type: 'num', value: num, position: start })
      } else if (isOperatorSymbol(ch)) {
        this.pos++
        tokens.push({ type: 'op', value: ch, position: start })
      } else if (ch === '(') {
        this.pos++
        tokens.push({ type: 'lparen', value: ch, position: start })
      } else if (ch === ')') {
        this.pos++
        tokens.push({ type: 'rparen', value: ch, position: start })
      } else if (ch === ',') {
        this.pos++
        tokens.push({ type: 'comma', value: ch, position: start })
      } else {
        throw new FormulaParseError({ code: 'unexpected-character', character: ch }, start)
      }
    }
    return tokens
  }

  private consumeWhile(predicate: (c: string) => boolean): string {
    const start = this.pos
    while (this.pos < this.src.length && predicate(this.src[this.pos]!)) {
      this.pos++
    }
    return this.src.slice(start, this.pos)
  }

  private consumeNumber(): string | null {
    const start = this.pos
    let seenDot = false
    let seenDigit = false
    while (this.pos < this.src.length) {
      const c = this.src[this.pos]!
      if (c >= '0' && c <= '9') {
        seenDigit = true
        this.pos++
      } else if (c === '.' && !seenDot) {
        seenDot = true
        this.pos++
      } else {
        break
      }
    }
    return seenDigit ? this.src.slice(start, this.pos) : null
  }
}

class Parser {
  private idx = 0
  private depth = 0

  constructor(
    private readonly tokens: Token[],
    private readonly sourceLength: number
  ) {}

  private peek(): Token | undefined {
    return this.tokens[this.idx]
  }

  private next(): Token | undefined {
    return this.tokens[this.idx++]
  }

  parse(): ArithmeticNode {
    const node = this.parseExpression(1)
    const rest = this.peek()
    if (rest !== undefined) {
      throw new FormulaParseError({ code: 'unexpected-token', token: rest.value }, rest.position)
    }
    return node
  }

  private parseExpression(minPrecedence: number): ArithmeticNode {
    let left = this.parsePrimary()
    for (;;) {
      const token = this.peek()
      if (token === undefined || token.type !== 'op') {
        break
      }
      const op = BINARY_OP_BY_SYMBOL[token.value]
      const precedence = BINARY_OPERATORS[op].precedence
      if (precedence < minPrecedence) {
        break
      }
      this.next()
      const right = this.parseExpression(precedence + 1)
      left = { op, operands: [left, right] }
    }
    return left
  }

  private parsePrimary(): ArithmeticNode {
    if (++this.depth > MAX_NESTING_DEPTH) {
      throw new FormulaParseError(
        { code: 'nesting-too-deep' },
        this.peek()?.position ?? this.sourceLength
      )
    }
    try {
      const token = this.peek()
      if (token === undefined) {
        throw new FormulaParseError({ code: 'unexpected-end' }, this.sourceLength)
      }

      if (token.type === 'op' && token.value === '-') {
        this.next()
        const operand = this.parsePrimary()
        if (operand.op === 'num') {
          return { op: 'num', value: -operand.value }
        }
        return { op: 'difference', operands: [{ op: 'num', value: 0 }, operand] }
      }

      if (token.type === 'num') {
        this.next()
        return { op: 'num', value: Number(token.value) }
      }

      if (token.type === 'ref') {
        this.next()
        return { op: 'ref', id: token.value }
      }

      if (token.type === 'func') {
        return this.parseFunctionCall(token)
      }

      if (token.type === 'lparen') {
        this.next()
        const inner = this.parseExpression(1)
        this.expect('rparen', ')')
        return inner
      }

      throw new FormulaParseError({ code: 'unexpected-token', token: token.value }, token.position)
    } finally {
      this.depth--
    }
  }

  private parseFunctionCall(nameToken: Token & { type: 'func' }): ArithmeticNode {
    const op = FUNCTION_OP_BY_NAME[nameToken.value]
    if (op === undefined) {
      throw new FormulaParseError(
        {
          code: 'unknown-function',
          name: nameToken.value,
          available: Object.values(FUNCTION_NAMES)
        },
        nameToken.position
      )
    }
    this.next()
    this.expect('lparen', '(')
    const empty = this.peek()
    if (empty?.type === 'rparen') {
      throw new FormulaParseError(
        { code: 'empty-function-args', name: nameToken.value },
        empty.position
      )
    }
    const operands: [ArithmeticNode, ...ArithmeticNode[]] = [this.parseExpression(1)]
    while (this.peek()?.type === 'comma') {
      this.next()
      operands.push(this.parseExpression(1))
    }
    this.expect('rparen', ')')
    return { op, operands }
  }

  private expect(type: Token['type'], symbol: string): void {
    const token = this.peek()
    if (token === undefined) {
      throw new FormulaParseError({ code: 'expected-token', symbol }, this.sourceLength)
    }
    if (token.type !== type) {
      throw new FormulaParseError({ code: 'expected-token', symbol }, token.position)
    }
    this.next()
  }
}

/** Parse a formula expression into an AST, or return a positioned error. */
export function parseFormula(source: string): ParseResult {
  try {
    const tokens = new Tokenizer(source).tokenize()
    if (tokens.length === 0) {
      throw new FormulaParseError({ code: 'empty-formula' }, 0)
    }
    return { ast: new Parser(tokens, source.length).parse() }
  } catch (error) {
    if (error instanceof FormulaParseError) {
      return { error }
    }
    throw error
  }
}
