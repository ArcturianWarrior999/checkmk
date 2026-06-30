<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import type { GraphFigureProps } from '../types'
import GraphTimestamp from './GraphTimestamp.vue'
import GraphTitle from './GraphTitle.vue'
import TimeSeriesGraph from './TimeSeriesGraph'

withDefaults(defineProps<GraphFigureProps>(), {
  interactive: true,
  canvasWidth: 800,
  canvasHeight: 300
})
</script>

<template>
  <div class="graphing-graph-figure">
    <div v-if="showTitle || showTimestamp" class="graphing-graph-figure__header">
      <div class="graphing-graph-figure__meta">
        <GraphTitle v-if="showTitle" :title="title ?? ''" />
        <GraphTimestamp v-if="showTimestamp && timeRange" :time-range="timeRange" />
      </div>
    </div>

    <!-- TODO: pass the right boolean into 'inspecting' so TimeSeriesGraph knows when to render
               its reset button -->
    <TimeSeriesGraph
      v-if="timeRange"
      :time_range="timeRange"
      :metrics="metrics"
      :horizontal_lines="horizontalLines ?? []"
      :value-range="null"
      zoom-mode="time"
      :size="{ width: canvasWidth, height: canvasHeight, mode: 'fixed' }"
      :min-time-range="null"
      :min-value-range="null"
      :inspecting="false"
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
