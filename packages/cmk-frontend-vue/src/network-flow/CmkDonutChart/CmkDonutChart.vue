<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed } from 'vue'

import { chartColorCss } from '../colors'
import type { CmkDonutChartProps } from './types'

const props = defineProps<CmkDonutChartProps>()

// SVG geometry. The arcs are drawn as stroke segments on a single circle using
// stroke-dasharray/dashoffset (the same technique as CmkProgressCircle), so no
// charting dependency is needed. The <svg> is rotated -90deg so the first slice
// starts at the top (12 o'clock) instead of at 3 o'clock.
const SIZE = 120
const STROKE = 20
const RADIUS = (SIZE - STROKE) / 2
const CENTER = SIZE / 2
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

const total = computed(() => props.slices.reduce((sum, slice) => sum + slice.value, 0))

interface Segment {
  key: string
  color: string
  dash: number
  gap: number
  offset: number
}

// One dashed segment per slice: the dash covers the slice's fraction of the
// ring, the gap covers the rest, and a growing negative offset moves each
// segment to start where the previous one ended.
const segments = computed<Segment[]>(() => {
  if (total.value <= 0) {
    return []
  }
  let consumed = 0
  return props.slices.map((slice) => {
    const dash = (slice.value / total.value) * CIRCUMFERENCE
    const segment: Segment = {
      key: slice.key,
      color: chartColorCss(slice.color),
      dash,
      gap: CIRCUMFERENCE - dash,
      offset: -consumed
    }
    consumed += dash
    return segment
  })
})

function percent(value: number): number {
  return total.value > 0 ? (value / total.value) * 100 : 0
}

function percentText(value: number): string {
  return `${percent(value).toFixed(1)}%`
}

// The center highlights the top slice (the caller ranks them, so it is first).
const topSlice = computed(() => props.slices[0])
</script>

<template>
  <div class="network-flow-cmk-donut-chart">
    <div class="network-flow-cmk-donut-chart__figure">
      <svg
        class="network-flow-cmk-donut-chart__svg"
        :viewBox="`0 0 ${SIZE} ${SIZE}`"
        role="img"
        preserveAspectRatio="xMidYMid meet"
      >
        <circle
          v-if="!segments.length"
          class="network-flow-cmk-donut-chart__empty-track"
          :cx="CENTER"
          :cy="CENTER"
          :r="RADIUS"
          :stroke-width="STROKE"
          fill="none"
        />
        <circle
          v-for="segment in segments"
          :key="segment.key"
          :cx="CENTER"
          :cy="CENTER"
          :r="RADIUS"
          :stroke="segment.color"
          :stroke-width="STROKE"
          fill="none"
          :stroke-dasharray="`${segment.dash} ${segment.gap}`"
          :stroke-dashoffset="segment.offset"
        />
      </svg>
      <div v-if="topSlice" class="network-flow-cmk-donut-chart__center">
        <span class="network-flow-cmk-donut-chart__center-value">{{
          percentText(topSlice.value)
        }}</span>
        <span class="network-flow-cmk-donut-chart__center-label">{{ topSlice.label }}</span>
      </div>
    </div>

    <ul class="network-flow-cmk-donut-chart__legend">
      <li
        v-for="slice in slices"
        :key="slice.key"
        class="network-flow-cmk-donut-chart__legend-item"
      >
        <span
          class="network-flow-cmk-donut-chart__swatch"
          :style="{ backgroundColor: chartColorCss(slice.color) }"
        />
        <span class="network-flow-cmk-donut-chart__legend-label">{{ slice.label }}</span>
        <span class="network-flow-cmk-donut-chart__legend-value">{{
          percentText(slice.value)
        }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.network-flow-cmk-donut-chart {
  display: flex;
  gap: clamp(8px, 3cqw, 24px);
  align-items: center;
  width: 100%;
  height: 100%;
  font-size: clamp(11px, 9cqh, 14px);
  container-type: size;
}

.network-flow-cmk-donut-chart__figure {
  position: relative;
  flex: 0 0 auto;
  align-self: stretch;
  aspect-ratio: 1;
  max-height: 100%;
}

.network-flow-cmk-donut-chart__svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.network-flow-cmk-donut-chart__empty-track {
  stroke: var(--ux-theme-4);
}

.network-flow-cmk-donut-chart__center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.network-flow-cmk-donut-chart__center-value {
  font-size: 1.6em;
  font-weight: var(--font-weight-bold);
  line-height: 1;
}

.network-flow-cmk-donut-chart__center-label {
  font-size: 0.85em;
  color: var(--color-mid-grey-50);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.network-flow-cmk-donut-chart__legend {
  flex: 1;
  min-width: 0;
  padding: 0;
  margin: 0;
  overflow: hidden;
  list-style: none;
}

.network-flow-cmk-donut-chart__legend-item {
  display: flex;
  gap: clamp(4px, 1cqw, 10px);
  align-items: center;
  padding: clamp(2px, 1.5cqh, 7px) 0;
  border-bottom: 1px solid var(--ux-theme-6);
}

.network-flow-cmk-donut-chart__swatch {
  flex: 0 0 auto;
  width: 0.75em;
  height: 0.75em;
  border-radius: 2px;
}

.network-flow-cmk-donut-chart__legend-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.network-flow-cmk-donut-chart__legend-value {
  font-variant-numeric: tabular-nums;
  text-align: right;
}
</style>
