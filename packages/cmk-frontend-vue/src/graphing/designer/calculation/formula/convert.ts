/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { components } from 'cmk-shared-typing/typescript/openapi_internal'

import type { Formula } from './grammar'

/** The formula ast as the REST API types it. */
export type ApiFormulaNode = components['schemas']['CustomGraphRRDFormulaDataSource']['ast']

/** Identity — the compile tripwire that `Formula` stays assignable to the wire type. */
export function toApiAst(ast: Formula): ApiFormulaNode {
  return ast
}

/** Narrows a wire-format ast to `Formula`; throws on empty function operands. */
export function fromApiAst(node: ApiFormulaNode): Formula {
  switch (node.op) {
    case 'ref':
    case 'num':
      return node
    case 'sum':
    case 'difference':
    case 'product':
    case 'fraction':
      return {
        op: node.op,
        operands: [fromApiAst(node.operands[0]), fromApiAst(node.operands[1])]
      }
    case 'avg':
    case 'min':
    case 'max':
    case 'fsum': {
      const [first, ...rest] = node.operands.map(fromApiAst)
      if (first === undefined) {
        throw new Error(`Empty operands in '${node.op}' node`)
      }
      return { op: node.op, operands: [first, ...rest] }
    }
    case 'percentile':
      return { op: 'percentile', percentile: node.percentile, operand: fromApiAst(node.operand) }
    default:
      throw new Error(`Unknown formula node: ${JSON.stringify(node satisfies never)}`)
  }
}
