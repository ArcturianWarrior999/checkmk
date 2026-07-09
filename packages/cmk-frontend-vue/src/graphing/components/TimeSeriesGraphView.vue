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
  type PinPayload,
  type RequestedTimeRange,
  type Size,
  type TimeRange,
  type ZoomMode
} from './TimeSeriesGraph'
import { CANVAS_MARGIN_HORIZONTAL, CANVAS_MARGIN_LEFT } from './constants'

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
  overview?: { metrics: Metric[]; timeRange: TimeRange }
  showBrush?: boolean
  brushWindow?: { start: number; end: number }
  showPin?: boolean
}>()

const emit = defineEmits<{
  'update:requestedTimeRange': [RequestedTimeRange]
  'update:view': [TimeRange]
  pinAction: [PinPayload]
}>()

const {
  timeRange: viewTimeRange,
  valueRange: viewValueRange,
  inspectionActive,
  handleIntent
} = useGraphView(() => props.timeRange)

watch(viewTimeRange, (view) => emit('update:view', view), { immediate: true, deep: true })

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

const pinTime = ref<number | null>(null)
function onPinAction(payload: PinPayload): void {
  pinTime.value = null
  emit('pinAction', payload)
}

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
      :show-pin="showPin"
      :pin-time="pinTime"
      @zoom="(payload) => handleIntent({ kind: 'zoomTransient', ...payload })"
      @pan="(payload) => handleIntent({ kind: 'pan', ...payload })"
      @reset="() => handleIntent({ kind: 'reset' })"
      @pin-create="pinTime = $event.time"
      @pin-action="onPinAction"
    />

    <!--
      plot-left=CANVAS_MARGIN_LEFT / width=size.width+CANVAS_MARGIN_HORIZONTAL mirror the renderer's private figure MARGIN
      (left=CANVAS_MARGIN_LEFT, left+right=CANVAS_MARGIN_HORIZONTAL) so the brush track aligns under the plot. Exporting MARGIN
      from TimeSeriesGraph.vue (or deriving these) is a follow-up.
    -->
    <GraphBrush
      v-if="showBrush && overview"
      class="graphing-time-series-graph-view__brush"
      :metrics="overview.metrics"
      :domain="overview.timeRange"
      :window="brushWindow ?? { start: viewTimeRange.start, end: viewTimeRange.end }"
      :min-span="minTimeRange"
      :width="size.width + CANVAS_MARGIN_HORIZONTAL"
      :plot-left="CANVAS_MARGIN_LEFT"
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
