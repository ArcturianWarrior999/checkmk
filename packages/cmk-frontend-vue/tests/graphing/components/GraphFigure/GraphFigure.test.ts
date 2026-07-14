/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type * as intl from '@internationalized/date'
import { render, screen, waitFor } from '@testing-library/vue'
import type { components } from 'cmk-shared-typing/typescript/openapi_internal'

import client from '@/lib/rest-api-client/client'

import GraphFigure from '@/graphing/components/GraphFigure/GraphFigure.vue'

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

const FETCHED = {
  metrics: [
    {
      metadata: { name: 'cpu', title: 'CPU utilization', unit: UNIT, color: '#ff0000' },
      render: { stack: 'area', inverse: false, hidden: false },
      data_points: [1, 2, 3]
    }
  ],
  time_range: { start: 1_000, end: 2_000, step: 60 },
  horizontal_lines: []
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let postSpy: any

beforeEach(() => {
  postSpy = vi.spyOn(client, 'POST')
  postSpy.mockResolvedValue({
    data: FETCHED,
    error: undefined,
    response: new Response('{}', { status: 200 })
  } as never)
})

afterEach(() => {
  vi.restoreAllMocks()
})

function renderFigure(props: Record<string, unknown> = {}) {
  return render(GraphFigure, {
    props: {
      graphType: 'template',
      internal: '{"graphs": []}',
      timerange: { type: 'age', hours: 4 },
      ...props
    }
  })
}

test('shows the loading spinner while the fetch is pending', () => {
  postSpy.mockReturnValue(new Promise(() => {}))
  renderFigure()
  expect(document.querySelector('.graphing-graph-figure__loading-icon')).toBeInTheDocument()
  expect(screen.queryByTestId('time-series-graph')).not.toBeInTheDocument()
})

test('renders the graph once data arrives', async () => {
  renderFigure()
  expect(await screen.findByTestId('time-series-graph')).toBeInTheDocument()
})

test('shows the error message when the fetch fails', async () => {
  postSpy.mockRejectedValue(new Error('crash'))
  renderFigure()
  expect(await screen.findByText(/crash/)).toBeInTheDocument()
})

test('fetches the definition via fetch_data with the max consolidation', async () => {
  renderFigure()

  await waitFor(() => expect(postSpy).toHaveBeenCalledTimes(1))
  const body = postSpy.mock.calls[0][1].body
  expect(body.graph_type).toBe('template')
  expect(body.internal).toBe('{"graphs": []}')
  expect(body.consolidation_function).toBe('max')
})

test('shows the timestamp only when requested', async () => {
  const { unmount } = renderFigure({ showTimestamp: true })
  await screen.findByTestId('time-series-graph')
  expect(document.querySelector('.graphing-graph-timestamp')).toBeInTheDocument()
  unmount()

  renderFigure()
  await screen.findByTestId('time-series-graph')
  expect(document.querySelector('.graphing-graph-timestamp')).not.toBeInTheDocument()
})

test('shows the compact legend only when requested', async () => {
  const { unmount } = renderFigure({ showLegend: true })
  await screen.findByTestId('time-series-graph')
  // The compact legend middle-truncates names into head/tail spans; the full title
  // is carried by the series' title attribute.
  expect(screen.getByTitle('CPU utilization')).toBeInTheDocument()
  expect(document.querySelector('.graphing-graph-legend-compact')).toBeInTheDocument()
  unmount()

  renderFigure()
  await screen.findByTestId('time-series-graph')
  expect(document.querySelector('.graphing-graph-legend-compact')).not.toBeInTheDocument()
})

test('shows the burger menu only when requested', async () => {
  const { unmount } = renderFigure({ showBurgerMenu: true })
  await screen.findByTestId('time-series-graph')
  expect(document.querySelector('.graphing-graph-burger-menu')).toBeInTheDocument()
  unmount()

  renderFigure()
  await screen.findByTestId('time-series-graph')
  expect(document.querySelector('.graphing-graph-burger-menu')).not.toBeInTheDocument()
})
