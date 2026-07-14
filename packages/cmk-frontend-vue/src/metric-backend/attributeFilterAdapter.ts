/**
 * Copyright (C) 2026 Checkmk GmbH - License: Checkmk Enterprise License
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { GraphLineQueryAttributes } from 'cmk-shared-typing/typescript/graph_designer'

import type { AttributeFilterModel, AttributeKind, Condition } from './attribute-filter/types'

export type AttributeKindKey = Exclude<AttributeKind, null>

export const ATTRIBUTE_KIND_ORDER: AttributeKindKey[] = ['resource', 'scope', 'datapoint']

export const KEY_IDENTS: Record<AttributeKindKey, string> = {
  resource: 'monitored_resource_attributes_keys_backend',
  scope: 'monitored_scope_attributes_keys_backend',
  datapoint: 'monitored_data_point_attributes_keys_backend'
}

export const VALUE_IDENTS: Record<AttributeKindKey, string> = {
  resource: 'monitored_resource_attributes_values_backend',
  scope: 'monitored_scope_attributes_values_backend',
  datapoint: 'monitored_data_point_attributes_values_backend'
}

export interface ThreeLists {
  resource: GraphLineQueryAttributes
  scope: GraphLineQueryAttributes
  datapoint: GraphLineQueryAttributes
}

export function toModel(lists: ThreeLists, newId: () => string): AttributeFilterModel {
  const conditions: Condition[] = []
  for (const attributeKind of ATTRIBUTE_KIND_ORDER) {
    for (const attr of lists[attributeKind]) {
      conditions.push({
        id: newId(),
        attributeKind,
        key: attr.key,
        operator: 'eq',
        value: attr.value
      })
    }
  }
  return conditions.length === 0 ? [] : [{ id: newId(), conditions }]
}

// The three lists cannot express OR, so all groups flatten together.
export function fromModel(model: AttributeFilterModel): ThreeLists {
  const lists: ThreeLists = { resource: [], scope: [], datapoint: [] }
  for (const condition of model.flatMap((group) => group.conditions)) {
    // Skip key-less conditions (a pill still being created).
    if (condition.attributeKind === null || !condition.key) {
      continue
    }
    lists[condition.attributeKind].push({ key: condition.key, value: condition.value })
  }
  return lists
}

export interface AutoCompleteContext {
  metric_name?: string
  attribute_key?: string
  resource_attributes?: GraphLineQueryAttributes
  scope_attributes?: GraphLineQueryAttributes
  data_point_attributes?: GraphLineQueryAttributes
  static_resource_attribute_keys?: string[]
}

export interface ContextOptions {
  metricName?: string | null
  staticResourceAttributeKeys?: string[] | null
  attributeKey?: string | null
  excludeId?: string
}

type AttrsKey = 'resource_attributes' | 'scope_attributes' | 'data_point_attributes'

const CONTEXT_KEYS: Record<AttributeKindKey, AttrsKey> = {
  resource: 'resource_attributes',
  scope: 'scope_attributes',
  datapoint: 'data_point_attributes'
}

// Exclude the condition being edited (excludeId) so it does not constrain its own
// value suggestions.
export function buildAutocompleteContext(
  model: AttributeFilterModel,
  options: ContextOptions = {}
): AutoCompleteContext {
  const context: AutoCompleteContext = {}
  if (options.metricName) {
    context.metric_name = options.metricName
  }
  const conditions = model.flatMap((group) => group.conditions)
  for (const attributeKind of ATTRIBUTE_KIND_ORDER) {
    const attrs = conditions
      .filter(
        (c) =>
          c.attributeKind === attributeKind &&
          c.id !== options.excludeId &&
          c.key !== null &&
          c.key !== '' &&
          c.value !== ''
      )
      .map((c) => ({ key: c.key as string, value: c.value }))
    if (attrs.length > 0) {
      context[CONTEXT_KEYS[attributeKind]] = attrs
    }
  }
  if (options.attributeKey) {
    context.attribute_key = options.attributeKey
  }
  if (options.staticResourceAttributeKeys) {
    context.static_resource_attribute_keys = options.staticResourceAttributeKeys
  }
  return context
}
