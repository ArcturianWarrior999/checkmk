/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'

import type { Metric } from '@/graphing/components/TimeSeriesGraph'
import AppearanceTable from '@/graphing/designer/components/AppearanceTable.vue'
import { useGraphItems } from '@/graphing/designer/composables/useGraphItems'
import type { DesignerItem } from '@/graphing/designer/drafts'
import type { ItemId } from '@/graphing/designer/types'

import { rrdMetricItem, rrdQueryItem } from '../fixtures'

const PALETTE: readonly string[] = ['#28a2f3', '#ff8400']

function metric(name: string, points: (number | null)[]): Metric {
  return {
    metadata: {
      name,
      title: name,
      unit: {
        notation: 'decimal',
        symbol: '',
        precision: { type: 'auto', digits: 2 },
        convertible: false
      },
      color: '#123456'
    },
    render: { stack: null, inverse: false, hidden: false },
    data_points: points
  }
}

function renderTable(seed: DesignerItem[], metricsBySource: Map<ItemId, Metric[]>) {
  const store = useGraphItems(PALETTE, seed)
  return { store, ...render(AppearanceTable, { props: { store, metricsBySource } }) }
}

test('shows the stats of rows that map to exactly one series', () => {
  renderTable(
    [rrdMetricItem('A'), rrdQueryItem('B')],
    new Map([
      ['A', [metric('a', [10, 30, 20])]],
      ['B', [metric('b1', [1]), metric('b2', [2])]]
    ])
  )
  // min, avg, max, last of row A
  expect(screen.getByText('10')).toBeInTheDocument()
  expect(screen.getAllByText('20')).not.toHaveLength(0)
  expect(screen.getByText('30')).toBeInTheDocument()
  // Row B fans into two series: no row-level stats.
  expect(screen.queryByText('1')).not.toBeInTheDocument()
  expect(screen.queryByText('2')).not.toBeInTheDocument()
})

test('shows the source type and title of every row', () => {
  renderTable([rrdMetricItem('A', { title: 'CPU load' }), rrdQueryItem('B')], new Map())
  expect(screen.getByText('CPU load')).toBeInTheDocument()
  expect(screen.getAllByText('Checkmk RRD')).toHaveLength(2)
})
