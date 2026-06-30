/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render, screen } from '@testing-library/vue'
import type { components } from 'cmk-shared-typing/typescript/openapi_internal'

import GraphPanel from '@/graphing/components/GraphPanel.vue'
import type { Metric, TimeRange } from '@/graphing/components/TimeSeriesGraph'
import type { BurgerMenuGroup, RequestedTimeRange } from '@/graphing/types'

// Mock renders received metric titles as text so tests can assert on visibility filtering.
vi.mock('@/graphing/components/TimeSeriesGraph', () => ({
  default: {
    inheritAttrs: false,
    props: ['metrics'],
    template:
      '<div data-testid="time-series-graph">{{ metrics.map((m) => m.metadata.title).join(",") }}</div>'
  }
}))

const UNIT: components['schemas']['ApiUnitFormat'] = {
  notation: 'decimal',
  symbol: '',
  precision: { type: 'auto', digits: 2 },
  convertible: true
}

const TIME_RANGE: TimeRange = { start: 1_781_524_800, end: 1_781_528_400, step: 300 }
const REQUESTED: RequestedTimeRange = { start: 1_781_524_800, end: 1_781_528_400 }

function makeMetric(name: string, title: string): Metric {
  return {
    metadata: { name, title, unit: UNIT, color: '#ff0000' },
    render: { stack: 'area', inverse: false, hidden: false },
    data_points: [1, 2, 3]
  }
}

const CPU = makeMetric('cpu', 'CPU')
const MEM = makeMetric('mem', 'Memory')

const BURGER_GROUPS: BurgerMenuGroup[] = [
  { heading: 'Export', actions: [{ label: 'Export as JSON', onClick: vi.fn() }] }
]

test('does not render the legend when showLegend is not set', () => {
  render(GraphPanel, {
    props: { metrics: [CPU], timeRange: TIME_RANGE, requestedTimeRange: REQUESTED }
  })
  expect(document.querySelector('.graphing-graph-panel__legend')).not.toBeInTheDocument()
})

test('renders the legend when showLegend is true', () => {
  render(GraphPanel, {
    props: {
      metrics: [CPU],
      timeRange: TIME_RANGE,
      requestedTimeRange: REQUESTED,
      showLegend: true
    }
  })
  expect(document.querySelector('.graphing-graph-panel__legend')).toBeInTheDocument()
})

test('does not render GraphBurgerMenu when showBurgerMenu is not set', () => {
  render(GraphPanel, {
    props: { metrics: [CPU], timeRange: TIME_RANGE, requestedTimeRange: REQUESTED }
  })
  expect(screen.queryByRole('button')).not.toBeInTheDocument()
})

test('renders GraphBurgerMenu when showBurgerMenu is true', () => {
  render(GraphPanel, {
    props: {
      metrics: [CPU],
      timeRange: TIME_RANGE,
      requestedTimeRange: REQUESTED,
      showBurgerMenu: true,
      burgerMenuGroups: BURGER_GROUPS
    }
  })
  expect(screen.getByRole('button')).toBeInTheDocument()
})

test('renders title when showTitle is true', () => {
  render(GraphPanel, {
    props: {
      metrics: [CPU],
      timeRange: TIME_RANGE,
      requestedTimeRange: REQUESTED,
      title: 'Panel Title',
      showTitle: true
    }
  })
  expect(screen.getByText('Panel Title')).toBeInTheDocument()
})

test('applies legend-right modifier class when legendPosition is "right"', () => {
  render(GraphPanel, {
    props: {
      metrics: [CPU],
      timeRange: TIME_RANGE,
      requestedTimeRange: REQUESTED,
      legendPosition: 'right'
    }
  })
  expect(
    document.querySelector('.graphing-graph-panel__container--legend-right')
  ).toBeInTheDocument()
})

test('does not apply legend-right modifier class when legendPosition is "bottom"', () => {
  render(GraphPanel, {
    props: {
      metrics: [CPU],
      timeRange: TIME_RANGE,
      requestedTimeRange: REQUESTED,
      legendPosition: 'bottom'
    }
  })
  expect(
    document.querySelector('.graphing-graph-panel__container--legend-right')
  ).not.toBeInTheDocument()
})

test('hiding a metric via the legend eye removes it from what TimeSeriesGraph receives', async () => {
  render(GraphPanel, {
    props: {
      metrics: [CPU, MEM],
      timeRange: TIME_RANGE,
      requestedTimeRange: REQUESTED,
      showLegend: true
    }
  })

  expect(screen.getByTestId('time-series-graph')).toHaveTextContent('CPU,Memory')

  const cpuRow = screen.getByText('CPU').closest('tr')!
  await fireEvent.click(cpuRow.querySelector('button')!)

  expect(screen.getByTestId('time-series-graph')).toHaveTextContent('Memory')
  expect(screen.getByTestId('time-series-graph')).not.toHaveTextContent('CPU')
})
