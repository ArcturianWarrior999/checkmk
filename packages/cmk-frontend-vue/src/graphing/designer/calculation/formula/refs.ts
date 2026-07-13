/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { type GraphItem, type ItemId, isFormula } from '../../types'
import type { Formula } from './grammar'

/** The ids directly referenced by the AST, unique, in first-appearance order. */
export function collectDirectRefs(ast: Formula): ItemId[] {
  const ids: ItemId[] = []
  const seen = new Set<ItemId>()
  const visit = (node: Formula): void => {
    switch (node.op) {
      case 'num':
        return
      case 'ref':
        if (!seen.has(node.id)) {
          seen.add(node.id)
          ids.push(node.id)
        }
        return
      case 'percentile':
        visit(node.operand)
        return
    }
    for (const operand of node.operands) {
      visit(operand)
    }
  }
  visit(ast)
  return ids
}

/** Whether following formula refs from `startId` reaches `targetId` (cycle detection). */
export function referencesTransitively(
  itemsById: ReadonlyMap<ItemId, GraphItem>,
  startId: ItemId,
  targetId: ItemId
): boolean {
  const stack: ItemId[] = [startId]
  const visited = new Set<ItemId>()
  while (stack.length > 0) {
    const id = stack.pop()!
    if (visited.has(id)) {
      continue
    }
    visited.add(id)
    const item = itemsById.get(id)
    if (item === undefined || !isFormula(item)) {
      continue
    }
    for (const ref of collectDirectRefs(item.ast)) {
      if (ref === targetId) {
        return true
      }
      stack.push(ref)
    }
  }
  return false
}
