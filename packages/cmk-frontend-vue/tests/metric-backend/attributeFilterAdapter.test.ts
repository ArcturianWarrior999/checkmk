/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { AttributeFilterModel, Condition } from '@/metric-backend/attribute-filter/types'
import {
  type ThreeLists,
  buildAutocompleteContext,
  fromModel,
  toModel
} from '@/metric-backend/attributeFilterAdapter'

let counter = 0
function newId(): string {
  counter += 1
  return `id-${counter}`
}

function group(...conditions: Condition[]): AttributeFilterModel {
  return [{ id: 'g', conditions }]
}

const lists: ThreeLists = {
  resource: [{ key: 'service.name', value: 'frontend' }],
  scope: [{ key: 'otel.library.name', value: 'http' }],
  datapoint: [
    { key: 'http.method', value: 'GET' },
    { key: 'http.route', value: '/api' }
  ]
}

describe('toModel', () => {
  test('concatenates resource -> scope -> datapoint into one AND group', () => {
    const model = toModel(lists, newId)

    expect(model).toHaveLength(1)
    expect(model[0]!.conditions.map((c) => [c.attributeKind, c.key, c.value, c.operator])).toEqual([
      ['resource', 'service.name', 'frontend', 'eq'],
      ['scope', 'otel.library.name', 'http', 'eq'],
      ['datapoint', 'http.method', 'GET', 'eq'],
      ['datapoint', 'http.route', '/api', 'eq']
    ])
  })

  test('produces an empty model for empty lists', () => {
    expect(toModel({ resource: [], scope: [], datapoint: [] }, newId)).toEqual([])
  })
})

describe('fromModel', () => {
  test('buckets conditions back into the three lists by attributeKind', () => {
    expect(fromModel(toModel(lists, newId))).toEqual(lists)
  })

  test('drops conditions with no attributeKind or empty key (pills still being created)', () => {
    const model = group(
      { id: 'a', attributeKind: null, key: '', operator: 'eq', value: '' },
      { id: 'b', attributeKind: 'resource', key: '', operator: 'eq', value: 'x' },
      { id: 'c', attributeKind: 'scope', key: 'otel.library.name', operator: 'eq', value: 'http' }
    )

    expect(fromModel(model)).toEqual({
      resource: [],
      scope: [{ key: 'otel.library.name', value: 'http' }],
      datapoint: []
    })
  })

  test('round-trips a model through fromModel -> toModel preserving content', () => {
    const model = toModel(lists, newId)
    expect(fromModel(toModel(fromModel(model), newId))).toEqual(lists)
  })
})

describe('buildAutocompleteContext', () => {
  test('emits per-type cascading attrs plus metric name and static keys', () => {
    const context = buildAutocompleteContext(toModel(lists, newId), {
      metricName: 'http_requests',
      staticResourceAttributeKeys: ['service.name']
    })

    expect(context).toEqual({
      metric_name: 'http_requests',
      resource_attributes: [{ key: 'service.name', value: 'frontend' }],
      scope_attributes: [{ key: 'otel.library.name', value: 'http' }],
      data_point_attributes: [
        { key: 'http.method', value: 'GET' },
        { key: 'http.route', value: '/api' }
      ],
      static_resource_attribute_keys: ['service.name']
    })
  })

  test('omits incomplete conditions (missing key or value) from the context', () => {
    const model = group(
      { id: 'a', attributeKind: 'resource', key: 'service.name', operator: 'eq', value: '' },
      { id: 'b', attributeKind: 'resource', key: 'host.name', operator: 'eq', value: 'web-01' }
    )

    expect(buildAutocompleteContext(model)).toEqual({
      resource_attributes: [{ key: 'host.name', value: 'web-01' }]
    })
  })

  test('excludes the condition being edited via excludeId', () => {
    const model = group(
      { id: 'self', attributeKind: 'datapoint', key: 'http.method', operator: 'eq', value: 'GET' },
      { id: 'other', attributeKind: 'datapoint', key: 'http.route', operator: 'eq', value: '/api' }
    )

    expect(
      buildAutocompleteContext(model, { attributeKey: 'http.method', excludeId: 'self' })
    ).toEqual({
      data_point_attributes: [{ key: 'http.route', value: '/api' }],
      attribute_key: 'http.method'
    })
  })

  test('omits empty optional fields', () => {
    expect(buildAutocompleteContext([])).toEqual({})
  })
})
