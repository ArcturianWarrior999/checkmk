/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { AttributeFilterModel } from '@/metric-backend/attribute-filter/types'

export type PresetName = 'empty' | 'individual' | 'groupsWithExtra' | 'singleGroup'

export const presetOptions: Array<{ title: string; name: PresetName }> = [
  { title: 'Empty', name: 'empty' },
  { title: '3 individual pills', name: 'individual' },
  { title: '2 groups of 3 + 1 extra pill', name: 'groupsWithExtra' },
  { title: '1 group of 5 pills', name: 'singleGroup' }
]

export const filterPresets: Record<PresetName, AttributeFilterModel> = {
  empty: [],
  individual: [
    {
      id: 'individual-g1',
      conditions: [
        {
          id: 'individual-1',
          attributeKind: 'resource',
          key: 'service.name',
          operator: 'eq',
          value: 'frontend'
        }
      ]
    },
    {
      id: 'individual-g2',
      conditions: [
        {
          id: 'individual-2',
          attributeKind: 'datapoint',
          key: 'http.method',
          operator: 'eq',
          value: 'GET'
        }
      ]
    },
    {
      id: 'individual-g3',
      conditions: [
        {
          id: 'individual-3',
          attributeKind: 'datapoint',
          key: 'http.status_code',
          operator: 'eq',
          value: '200'
        }
      ]
    }
  ],
  groupsWithExtra: [
    {
      id: 'gx-g1',
      conditions: [
        {
          id: 'gx-g1-a',
          attributeKind: 'resource',
          key: 'service.name',
          operator: 'eq',
          value: 'frontend'
        },
        {
          id: 'gx-g1-b',
          attributeKind: 'datapoint',
          key: 'http.method',
          operator: 'eq',
          value: 'GET'
        },
        {
          id: 'gx-g1-c',
          attributeKind: 'datapoint',
          key: 'http.status_code',
          operator: 'eq',
          value: '200'
        }
      ]
    },
    {
      id: 'gx-g2',
      conditions: [
        {
          id: 'gx-g2-a',
          attributeKind: 'resource',
          key: 'service.name',
          operator: 'eq',
          value: 'checkout'
        },
        {
          id: 'gx-g2-b',
          attributeKind: 'datapoint',
          key: 'http.method',
          operator: 'eq',
          value: 'POST'
        },
        {
          id: 'gx-g2-c',
          attributeKind: 'datapoint',
          key: 'http.status_code',
          operator: 'eq',
          value: '500'
        }
      ]
    },
    {
      id: 'gx-g3',
      conditions: [
        {
          id: 'gx-extra',
          attributeKind: 'resource',
          key: 'host.name',
          operator: 'contains',
          value: 'prod'
        }
      ]
    }
  ],
  singleGroup: [
    {
      id: 'single-g',
      conditions: [
        {
          id: 'single-1',
          attributeKind: 'resource',
          key: 'service.name',
          operator: 'eq',
          value: 'frontend'
        },
        {
          id: 'single-2',
          attributeKind: 'resource',
          key: 'deployment.environment',
          operator: 'eq',
          value: 'production'
        },
        {
          id: 'single-3',
          attributeKind: 'datapoint',
          key: 'http.method',
          operator: 'eq',
          value: 'GET'
        },
        {
          id: 'single-4',
          attributeKind: 'datapoint',
          key: 'http.route',
          operator: 'starts_with',
          value: '/api'
        },
        {
          id: 'single-5',
          attributeKind: 'datapoint',
          key: 'http.status_code',
          operator: 'eq',
          value: '200'
        }
      ]
    }
  ]
}
