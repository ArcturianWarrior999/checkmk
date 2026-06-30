<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
// TODO: usage example — shows how to wire the TimeSeriesGraph renderer through
// useGraphView (emit-and-wait). Not yet consumed by a real call site.
import { computed, ref, watch } from 'vue'

import usei18n from '@/lib/i18n'

import CmkLabeledSwitch from '@/components/CmkLabeledSwitch.vue'

import { useGraphView } from '../composables/useGraphView'
import GraphBrush from './GraphBrush/GraphBrush.vue'
import TimeSeriesGraph, {
  type ConsolidationFn,
  type GraphOptions,
  type HorizontalLine,
  type LineInterpolator,
  type Metric,
  type RequestedTimeRange,
  type Size,
  type TimeRange,
  type ZoomMode
} from './TimeSeriesGraph'

interface CmkInteractionFlags {
  zoom: 'enabled' | 'disabled'
  panning: 'enabled' | 'disabled'
  hover: 'enabled' | 'disabled'
}

const props = defineProps<{
  graphOptions: GraphOptions
  interaction: CmkInteractionFlags
  size: Size
  metrics: Metric[]
  timeRange: TimeRange
  minTimeRange: number | null
  minValueRange: number | null
  consolidationFunction?: ConsolidationFn
  horizontalLines?: HorizontalLine[]
  curveInterpolator?: LineInterpolator
  // Optional overview series for the navigator brush (coarse, wider, end-anchored context)
  // and its domain. When omitted, the brush is not rendered.
  overview?: { metrics: Metric[]; timeRange: TimeRange }
  showBrush?: boolean
}>()

const emit = defineEmits<{ 'update:requestedTimeRange': [RequestedTimeRange] }>()

const {
  timeRange: viewTimeRange,
  valueRange: viewValueRange,
  inspectionActive,
  handleIntent
} = useGraphView(() => props.timeRange)

const zoomMode = ref<ZoomMode>('time')
const peakZoomActive = computed({
  get: () => zoomMode.value === 'value',
  set: (active) => {
    zoomMode.value = active ? 'value' : 'time'
  }
})

const { _t } = usei18n()
const timeZoomLabel = _t('Time zoom')
const peakZoomLabel = _t('Peak zoom')

watch(
  () => props.timeRange,
  () => handleIntent({ kind: 'rangeCommit', timeRange: props.timeRange })
)
</script>

<template>
  <div class="graphing-time-series-graph-view">
    <CmkLabeledSwitch
      v-model="peakZoomActive"
      :off-label="timeZoomLabel"
      :on-label="peakZoomLabel"
      class="graphing-time-series-graph-view__zoom-switch"
    />
    <TimeSeriesGraph
      :metrics="metrics"
      :time_range="viewTimeRange"
      :value-range="viewValueRange"
      :zoom-mode="zoomMode"
      :min-time-range="minTimeRange"
      :min-value-range="minValueRange"
      :inspecting="inspectionActive"
      :pan-enabled="interaction.panning === 'enabled'"
      :consolidation-function="consolidationFunction ?? 'avg'"
      :horizontal_lines="horizontalLines ?? []"
      :curve-interpolator="curveInterpolator ?? 'linear'"
      :size="size"
      :options="graphOptions"
      :highlighted-metric-name="null"
      @zoom="(payload) => handleIntent({ kind: 'zoomTransient', ...payload })"
      @pan="(payload) => handleIntent({ kind: 'pan', ...payload })"
      @reset="() => handleIntent({ kind: 'reset' })"
    />

    <!--
      plot-left=50 / width=size.width+60 mirror the renderer's private figure MARGIN
      (left=50, left+right=60) so the brush track aligns under the plot. Exporting MARGIN
      from TimeSeriesGraph.vue (or deriving these) is a follow-up.
    -->
    <GraphBrush
      v-if="showBrush && overview"
      class="graphing-time-series-graph-view__brush"
      :metrics="overview.metrics"
      :domain="overview.timeRange"
      :window="{ start: viewTimeRange.start, end: viewTimeRange.end }"
      :min-span="minTimeRange"
      :width="size.width + 60"
      :plot-left="50"
      :plot-width="size.width"
      @update:requested-time-range="(value) => emit('update:requestedTimeRange', value)"
    />
  </div>
</template>

<style scoped>
.graphing-time-series-graph-view {
  position: relative;
  width: fit-content;
}

.graphing-time-series-graph-view__zoom-switch {
  position: absolute;
  top: var(--dimension-4);
  left: var(--dimension-4);
  z-index: 3;
}

.graphing-time-series-graph-view__brush {
  display: block;
  margin-top: var(--dimension-6);
}
</style>
