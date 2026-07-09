/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type * as intl from '@internationalized/date'
import { render, screen } from '@testing-library/vue'
import type { components } from 'cmk-shared-typing/typescript/openapi_internal'

import GraphFigure from '@/graphing/components/GraphFigure.vue'
import type { Metric, TimeRange } from '@/graphing/components/TimeSeriesGraph'

vi.mock('@/graphing/components/TimeSeriesGraph', () => ({
  default: {
    inheritAttrs: false,
    template: '<div data-testid="time-series-graph" />'
  }
}))

vi.mock('@internationalized/date', async (importOriginal) => {
  const actual = await importOriginal<typeof intl>()
  return { ...actual, getLocalTimeZone: () => 'UTC' }
})

const UNIT: components['schemas']['ApiUnitFormat'] = {
  notation: 'decimal',
  symbol: '',
  precision: { type: 'auto', digits: 2 },
  convertible: true
}

const TIME_RANGE: TimeRange = { start: 1_781_524_800, end: 1_781_528_400, step: 300 }

const CPU: Metric = {
  metadata: { name: 'cpu', title: 'CPU', unit: UNIT, color: '#ff0000' },
  render: { stack: 'area', inverse: false, hidden: false },
  data_points: [1, 2, 3]
}

test('does not render TimeSeriesGraph when dataTimeRange is absent', () => {
  render(GraphFigure, { props: { metrics: [CPU] } })
  expect(screen.queryByTestId('time-series-graph')).not.toBeInTheDocument()
})

test('renders TimeSeriesGraph when dataTimeRange is provided', () => {
  render(GraphFigure, { props: { metrics: [CPU], dataTimeRange: TIME_RANGE } })
  expect(screen.getByTestId('time-series-graph')).toBeInTheDocument()
})

test('does not render header when neither showTitle nor showTimestamp is set', () => {
  render(GraphFigure, { props: { metrics: [CPU], dataTimeRange: TIME_RANGE } })
  expect(document.querySelector('.graphing-graph-figure__header')).not.toBeInTheDocument()
})

test('renders title when showTitle is true', () => {
  render(GraphFigure, {
    props: { metrics: [CPU], dataTimeRange: TIME_RANGE, title: 'My Graph', showTitle: true }
  })
  expect(screen.getByText('My Graph')).toBeInTheDocument()
})

test('does not render title when showTitle is false', () => {
  render(GraphFigure, {
    props: { metrics: [CPU], dataTimeRange: TIME_RANGE, title: 'My Graph', showTitle: false }
  })
  expect(screen.queryByText('My Graph')).not.toBeInTheDocument()
})

test('renders GraphTimestamp when showTimestamp is true and dataTimeRange is provided', () => {
  render(GraphFigure, {
    props: { metrics: [CPU], dataTimeRange: TIME_RANGE, showTimestamp: true }
  })
  expect(document.querySelector('.graphing-graph-timestamp')).toBeInTheDocument()
})

test('does not render GraphTimestamp when showTimestamp is true but dataTimeRange is absent', () => {
  render(GraphFigure, { props: { metrics: [CPU], showTimestamp: true } })
  expect(document.querySelector('.graphing-graph-timestamp')).not.toBeInTheDocument()
})
