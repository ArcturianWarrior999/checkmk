<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { useGraphInteraction } from '../composables/useGraphInteraction'
import type { GraphFigureProps } from '../types'
import GraphTimestamp from './GraphTimestamp.vue'
import GraphTitle from './GraphTitle.vue'
import TimeSeriesGraph from './TimeSeriesGraph'

const props = withDefaults(defineProps<GraphFigureProps>(), {
  interactive: true,
  canvasWidth: 800,
  canvasHeight: 300
})

const {
  viewTimeRange,
  viewValueRange,
  inspectionActive,
  zoomMode,
  pinTime,
  onZoom,
  onPan,
  onReset,
  onPinCreate,
  clearPin
} = useGraphInteraction(() => props.dataTimeRange)
</script>

<template>
  <div class="graphing-graph-figure">
    <div v-if="showTitle || showTimestamp" class="graphing-graph-figure__header">
      <div class="graphing-graph-figure__meta">
        <GraphTitle v-if="showTitle" :title="title ?? ''" />
        <GraphTimestamp v-if="showTimestamp && dataTimeRange" :time-range="dataTimeRange" />
      </div>
    </div>

    <TimeSeriesGraph
      v-if="dataTimeRange"
      :time_range="viewTimeRange"
      :metrics="metrics"
      :horizontal_lines="horizontalLines ?? []"
      :value-range="viewValueRange"
      :zoom-mode="zoomMode"
      :size="{ width: canvasWidth, height: canvasHeight, mode: 'fixed' }"
      :min-time-range="null"
      :min-value-range="null"
      :inspecting="inspectionActive"
      :pan-enabled="interactive"
      :options="{
        header: { title: title ?? null, show_graph_time: false },
        name: title ?? '',
        x_axis: null,
        y_axis: null,
        show_pin: false,
        font_size_pt: 10
      }"
      :highlighted-metric-name="null"
      :pin-time="pinTime"
      @zoom="onZoom"
      @pan="onPan"
      @reset="onReset"
      @pin-create="onPinCreate"
      @pin-action="clearPin"
    />
  </div>
</template>

<style scoped lang="scss">
.graphing-graph-figure__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: calc(var(--spacing) * 3);
}

.graphing-graph-figure__meta {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-double);
}
</style>
