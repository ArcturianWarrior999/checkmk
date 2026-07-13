/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { type Domain, type GraphItem, type ItemId, domainOf, isDynamic } from '../../types'
import { type Formula, isFunction } from './grammar'
import { referencesTransitively } from './refs'

export type ValidationIssue =
  | { code: 'unknown-ref'; id: ItemId }
  | { code: 'self-ref'; id: ItemId }
  | { code: 'cyclic-ref'; id: ItemId }
  | { code: 'domain-mismatch'; id: ItemId }
  | { code: 'needs-consolidation'; id: ItemId }

/** Validate a formula against the known items and the editor's domain; it must not reference `editedItemId`, directly or through other formulas (cycle). */
export function validateFormula(
  ast: Formula,
  items: readonly GraphItem[],
  domain: Domain,
  editedItemId: ItemId | null = null
): ValidationIssue[] {
  const byId = new Map(items.map((item) => [item.id, item]))
  const issues: ValidationIssue[] = []
  const seen = new Set<string>()

  const record = (issue: ValidationIssue): void => {
    const key = `${issue.code}:${issue.id}`
    if (!seen.has(key)) {
      seen.add(key)
      issues.push(issue)
    }
  }

  const visit = (node: Formula, parent: Formula | null): void => {
    switch (node.op) {
      case 'num':
        return
      case 'percentile':
        visit(node.operand, node)
        return
      case 'ref': {
        if (node.id === editedItemId) {
          record({ code: 'self-ref', id: node.id })
          return
        }
        const item = byId.get(node.id)
        if (item === undefined) {
          record({ code: 'unknown-ref', id: node.id })
        } else if (domainOf(item.type) !== domain) {
          record({ code: 'domain-mismatch', id: node.id })
        } else if (isDynamic(item.type) && !isConsolidated(node, parent)) {
          record({ code: 'needs-consolidation', id: node.id })
        } else if (editedItemId !== null && referencesTransitively(byId, node.id, editedItemId)) {
          record({ code: 'cyclic-ref', id: node.id })
        }
        return
      }
    }
    for (const operand of node.operands) {
      visit(operand, node)
    }
  }

  visit(ast, null)
  return issues
}

/** A dynamic reference is consolidated iff it is the single, sole operand of an aggregation function. */
function isConsolidated(ref: Formula, parent: Formula | null): boolean {
  return (
    parent !== null &&
    isFunction(parent) &&
    parent.operands.length === 1 &&
    parent.operands[0] === ref
  )
}
