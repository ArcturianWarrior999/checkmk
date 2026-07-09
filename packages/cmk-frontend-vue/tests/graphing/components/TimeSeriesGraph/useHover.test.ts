/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render } from '@testing-library/vue'
import { scaleLinear, scaleTime } from 'd3-scale'
import { afterEach, describe, expect, test, vi } from 'vitest'
import { defineComponent, h, ref } from 'vue'

import type { Metric } from '@/graphing/components/TimeSeriesGraph'
import { downsampleToColumns, m4 } from '@/graphing/components/TimeSeriesGraph/decimation/decimate'
import { computeStackedSeries } from '@/graphing/components/TimeSeriesGraph/render/stacked'
import { useHover } from '@/graphing/components/TimeSeriesGraph/useHover'

const UNIT: Metric['metadata']['unit'] = {
  notation: 'decimal',
  symbol: '',
  precision: { type: 'auto', digits: 2 },
  convertible: true
}

const TIME_RANGE = { start: 0, end: 100, step: 10 }
const PLOT_WIDTH = 100
const PLOT_HEIGHT = 100

function makeLineMetric(name: string, dataPoints: (number | null)[]): Metric {
  return {
    metadata: { name, title: name, unit: UNIT, color: '#ff0000' },
    render: { stack: null, inverse: false, hidden: false },
    data_points: dataPoints
  }
}

function constantPoints(value: number | null): (number | null)[] {
  return Array.from({ length: 11 }, () => value)
}

function mountHover(metrics: Metric[]): ReturnType<typeof useHover> {
  const xScale = scaleTime()
    .domain([new Date(TIME_RANGE.start * 1000), new Date(TIME_RANGE.end * 1000)])
    .range([0, PLOT_WIDTH])
  const yScale = scaleLinear().domain([0, 100]).range([PLOT_HEIGHT, 0])
  let api!: ReturnType<typeof useHover>
  const harness = defineComponent({
    setup() {
      api = useHover({
        metrics: () => metrics,
        consolidation: () => 'avg',
        plotWidth: ref(PLOT_WIDTH),
        plotHeight: ref(PLOT_HEIGHT),
        xScale,
        yScale
      })
      return () => h('div')
    }
  })
  render(harness)
  const buckets = metrics.map((metric) =>
    downsampleToColumns(
      m4(metric.data_points, TIME_RANGE, 4000),
      [TIME_RANGE.start, TIME_RANGE.end],
      PLOT_WIDTH
    )
  )
  api.recordDrawnGeometry(buckets, computeStackedSeries(metrics, buckets, 'avg'))
  return api
}

describe('useHover — hit-test', () => {
  test('flags the metric drawn nearest the cursor as closest', () => {
    const hover = mountHover([
      makeLineMetric('low', constantPoints(10)),
      makeLineMetric('high', constantPoints(90))
    ])

    hover.moveHoverTo({ x: 50, y: 85 })

    const samples = hover.hoverState.value!.samples
    expect(samples.map((sample) => [sample.metricName, sample.isClosest])).toEqual([
      ['low', true],
      ['high', false]
    ])
  })

  test('carries the cursor position and snaps the crosshair near it', () => {
    const hover = mountHover([makeLineMetric('low', constantPoints(10))])

    hover.moveHoverTo({ x: 50, y: 85 })

    const state = hover.hoverState.value!
    expect(state.cursorX).toBe(50)
    expect(state.cursorY).toBe(85)
    expect(Math.abs(state.snapX - 50)).toBeLessThanOrEqual(1)
  })

  test('a metric without data points gets an n/a sample and is never closest', () => {
    const hover = mountHover([
      makeLineMetric('empty', constantPoints(null)),
      makeLineMetric('high', constantPoints(90))
    ])

    hover.moveHoverTo({ x: 50, y: 85 })

    const samples = hover.hoverState.value!.samples
    expect(samples[0]).toMatchObject({
      metricName: 'empty',
      formattedValue: 'n/a',
      pixelY: null,
      isClosest: false
    })
    expect(samples[1]!.isClosest).toBe(true)
  })

  test('a cursor outside the plot yields no hover state', () => {
    const hover = mountHover([makeLineMetric('low', constantPoints(10))])
    hover.moveHoverTo({ x: 50, y: 85 })

    hover.moveHoverTo({ x: -1, y: 50 })

    expect(hover.hoverState.value).toBeNull()
  })
})

describe('useHover — clearing', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  test('clearHover drops the state immediately', () => {
    const hover = mountHover([makeLineMetric('low', constantPoints(10))])
    hover.moveHoverTo({ x: 50, y: 85 })

    hover.clearHover()

    expect(hover.hoverState.value).toBeNull()
  })

  test('clearHoverAfterDelay drops the state only once the delay elapsed', () => {
    vi.useFakeTimers()
    const hover = mountHover([makeLineMetric('low', constantPoints(10))])
    hover.moveHoverTo({ x: 50, y: 85 })

    hover.clearHoverAfterDelay()

    expect(hover.hoverState.value).not.toBeNull()
    vi.advanceTimersByTime(150)
    expect(hover.hoverState.value).toBeNull()
  })

  test('cancelPendingHoverClear keeps the state alive past the delay', () => {
    vi.useFakeTimers()
    const hover = mountHover([makeLineMetric('low', constantPoints(10))])
    hover.moveHoverTo({ x: 50, y: 85 })
    hover.clearHoverAfterDelay()

    hover.cancelPendingHoverClear()

    vi.advanceTimersByTime(1000)
    expect(hover.hoverState.value).not.toBeNull()
  })

  test('moving the hover cancels a pending clear', () => {
    vi.useFakeTimers()
    const hover = mountHover([makeLineMetric('low', constantPoints(10))])
    hover.moveHoverTo({ x: 50, y: 85 })
    hover.clearHoverAfterDelay()

    hover.moveHoverTo({ x: 60, y: 85 })

    vi.advanceTimersByTime(1000)
    expect(hover.hoverState.value).not.toBeNull()
  })
})
