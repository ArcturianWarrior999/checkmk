<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { scaleLinear } from 'd3-scale'
import { area, curveMonotoneX, line } from 'd3-shape'
import { computed, ref, useTemplateRef } from 'vue'

import usei18n from '@/lib/i18n'
import { useResizeObserver } from '@/lib/useResizeObserver'

import { chartColorCss } from '../colors'
import type { TrendChartDisplayMode, TrendChartSeriesWithColor } from './types'

const { _t } = usei18n()

const props = defineProps<{
  series: TrendChartSeriesWithColor[]
  displayMode: TrendChartDisplayMode
  formatValue: (value: number) => string
}>()

// Room for the y-axis value labels (left) and the x-axis time labels (bottom).
const MARGIN = { top: 8, right: 8, bottom: 20, left: 56 }
const X_TICK_COUNT = 5
const Y_TICK_COUNT = 4

// A ResizeObserver keeps the chart sized to its container; the defaults only
// apply before the first measurement (and in non-DOM test environments).
const rootRef = useTemplateRef<HTMLElement>('rootRef')
const width = ref(600)
const height = ref(240)
const { observe } = useResizeObserver((entries) => {
  const entry = entries[0]
  if (entry) {
    width.value = entry.contentRect.width
    height.value = entry.contentRect.height
  }
})
observe(rootRef)

// One point per minute; all series share the window length. Fewer than two
// points cannot form a path, so the chart renders empty.
const pointCount = computed(() =>
  props.series.reduce((max, series) => Math.max(max, series.dataPoints.length), 0)
)
const hasData = computed(() => pointCount.value >= 2)

const innerWidth = computed(() => Math.max(0, width.value - MARGIN.left - MARGIN.right))
const innerHeight = computed(() => Math.max(0, height.value - MARGIN.top - MARGIN.bottom))

const xScale = computed(() =>
  scaleLinear()
    .domain([0, Math.max(1, pointCount.value - 1)])
    .range([MARGIN.left, MARGIN.left + innerWidth.value])
)

// Lines scale to the largest single value, stacked areas to the largest
// cumulative sum across the series at any bucket.
const yMax = computed(() => {
  if (props.displayMode === 'stacked_area') {
    let max = 0
    for (let i = 0; i < pointCount.value; i++) {
      let sum = 0
      for (const series of props.series) {
        sum += series.dataPoints[i] ?? 0
      }
      max = Math.max(max, sum)
    }
    return max
  }
  return props.series.reduce(
    (max, series) => Math.max(max, ...(series.dataPoints.length ? series.dataPoints : [0])),
    0
  )
})

const yScale = computed(() =>
  scaleLinear()
    .domain([0, yMax.value > 0 ? yMax.value : 1])
    .range([MARGIN.top + innerHeight.value, MARGIN.top])
    .nice(Y_TICK_COUNT)
)

const yTicks = computed(() => yScale.value.ticks(Y_TICK_COUNT))

// Evenly spaced time ticks, labelled by how many minutes ago the bucket is
// (the newest bucket is "now"); relative labels avoid a clock dependency.
const xTicks = computed(() => {
  const count = pointCount.value
  if (!hasData.value) {
    return []
  }
  return Array.from({ length: X_TICK_COUNT }, (_unused, k) => {
    const index = Math.round(((count - 1) * k) / (X_TICK_COUNT - 1))
    const minutesAgo = count - 1 - index
    return { index, label: minutesAgo === 0 ? _t('now') : `-${minutesAgo} min` }
  })
})

// Stacked bands: each series sits on the cumulative sum of the ones before it.
const stackedBands = computed(() => {
  const lowerAccum = new Array<number>(pointCount.value).fill(0)
  return props.series.map((series) => {
    const lower = lowerAccum.slice()
    const upper = lower.map((low, i) => low + (series.dataPoints[i] ?? 0))
    for (let i = 0; i < upper.length; i++) {
      lowerAccum[i] = upper[i]!
    }
    return { color: series.color, lower, upper }
  })
})

const indices = computed(() => Array.from({ length: pointCount.value }, (_unused, i) => i))

const linePaths = computed(() => {
  if (!hasData.value) {
    return []
  }
  return props.series.map((series) => {
    const gen = line<number>()
      .x((_unused, i) => xScale.value(i))
      .y((_unused, i) => yScale.value(series.dataPoints[i] ?? 0))
      .curve(curveMonotoneX)
    return { color: chartColorCss(series.color), d: gen(indices.value) ?? '' }
  })
})

const areaPaths = computed(() => {
  if (!hasData.value) {
    return []
  }
  return stackedBands.value.map((band) => {
    const areaGen = area<number>()
      .x((_unused, i) => xScale.value(i))
      .y0((_unused, i) => yScale.value(band.lower[i] ?? 0))
      .y1((_unused, i) => yScale.value(band.upper[i] ?? 0))
      .curve(curveMonotoneX)
    const topGen = line<number>()
      .x((_unused, i) => xScale.value(i))
      .y((_unused, i) => yScale.value(band.upper[i] ?? 0))
      .curve(curveMonotoneX)
    return {
      color: chartColorCss(band.color),
      area: areaGen(indices.value) ?? '',
      top: topGen(indices.value) ?? ''
    }
  })
})
</script>

<template>
  <div ref="rootRef" class="network-flow-trend-chart-plot">
    <svg
      class="network-flow-trend-chart-plot__svg"
      :viewBox="`0 0 ${width} ${height}`"
      :width="width"
      :height="height"
      preserveAspectRatio="none"
    >
      <g class="network-flow-trend-chart-plot__grid">
        <line
          v-for="tick in yTicks"
          :key="`grid-${tick}`"
          :x1="MARGIN.left"
          :x2="MARGIN.left + innerWidth"
          :y1="yScale(tick)"
          :y2="yScale(tick)"
        />
      </g>

      <g class="network-flow-trend-chart-plot__values">
        <text
          v-for="tick in yTicks"
          :key="`y-${tick}`"
          :x="MARGIN.left - 6"
          :y="yScale(tick)"
          dominant-baseline="middle"
          text-anchor="end"
        >
          {{ formatValue(tick) }}
        </text>
      </g>

      <g class="network-flow-trend-chart-plot__times">
        <text
          v-for="tick in xTicks"
          :key="`x-${tick.index}`"
          :x="xScale(tick.index)"
          :y="height - 4"
          text-anchor="middle"
        >
          {{ tick.label }}
        </text>
      </g>

      <template v-if="displayMode === 'stacked_area'">
        <template v-for="(band, index) in areaPaths" :key="`band-${index}`">
          <path :d="band.area" :fill="band.color" fill-opacity="0.4" stroke="none" />
          <path :d="band.top" fill="none" :stroke="band.color" stroke-width="1.5" />
        </template>
      </template>
      <template v-else>
        <path
          v-for="(path, index) in linePaths"
          :key="`line-${index}`"
          :d="path.d"
          fill="none"
          :stroke="path.color"
          stroke-width="1.5"
          stroke-linejoin="round"
          stroke-linecap="round"
        />
      </template>
    </svg>
  </div>
</template>

<style scoped>
.network-flow-trend-chart-plot {
  width: 100%;
  height: 100%;
}

.network-flow-trend-chart-plot__svg {
  display: block;
  width: 100%;
  height: 100%;
}

.network-flow-trend-chart-plot__grid line {
  stroke: var(--ux-theme-4);
  stroke-width: 1;
}

.network-flow-trend-chart-plot__values text,
.network-flow-trend-chart-plot__times text {
  font-size: 11px;
  fill: var(--color-mid-grey-50);
}
</style>
