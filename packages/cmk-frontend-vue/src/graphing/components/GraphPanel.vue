<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { useGraphVisibility } from '../composables/useGraphVisibility'
import type { ConsolidationFn, GraphPanelEmits, GraphPanelProps } from '../types.ts'
import GraphBurgerMenu from './GraphBurgerMenu.vue'
import GraphLegend from './GraphLegend.vue'
import GraphTimestamp from './GraphTimestamp.vue'
import GraphTitle from './GraphTitle.vue'
import TimeSeriesGraph from './TimeSeriesGraph'

const props = withDefaults(defineProps<GraphPanelProps>(), {
  interactive: true,
  canvasWidth: 800,
  canvasHeight: 300,
  legendPosition: 'bottom'
})

const emit = defineEmits<GraphPanelEmits>()

/* TODO: get activeTimeRange from useGraphTimeRange as well and use it
const { activeTimeRange, setActiveTimeRange } = useGraphTimeRange(() => props.requestedTimeRange)
*/

const {
  hiddenMetricNames,
  hiddenLineNames,
  highlightedMetricName,
  activeConsolidationFunction,
  visibleMetrics,
  visibleHorizontalLines,
  setConsolidationFunction
} = useGraphVisibility(
  () => props.metrics,
  () => props.horizontalLines ?? []
)

/* TODO: trigger updateTimeRange() through the future brush/pan component
function updateTimeRange(val: RequestedTimeRange) {
  setActiveTimeRange(val)
  emit('update:requestedTimeRange', val)
}
*/

function updateConsolidationFunction(val: ConsolidationFn) {
  setConsolidationFunction(val)
  emit('update:consolidationFn', val)
}
</script>

<template>
  <div class="graphing-graph-panel">
    <div
      class="graphing-graph-panel__container"
      :class="{ 'graphing-graph-panel__container--legend-right': legendPosition === 'right' }"
    >
      <div class="graphing-graph-panel__canvas-area">
        <div
          v-if="showTitle || showTimestamp || showBurgerMenu"
          class="graphing-graph-panel__header"
        >
          <div class="graphing-graph-panel__meta">
            <GraphTitle v-if="showTitle" :title="title ?? ''" />
            <GraphTimestamp v-if="showTimestamp && timeRange" :time-range="timeRange" />
          </div>
          <GraphBurgerMenu v-if="showBurgerMenu" :groups="burgerMenuGroups ?? []" />
        </div>

        <!-- TODO: 'zoom-mode': pass the right literal ('time' | 'value') once the toggle element
                   is implemented
                   'inspecting': pass the right boolean so TimeSeriesGraph knows when to render
                   its reset button
        -->
        <TimeSeriesGraph
          v-if="timeRange"
          :time_range="timeRange"
          :metrics="visibleMetrics"
          :horizontal_lines="visibleHorizontalLines"
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
          :highlighted-metric-name="highlightedMetricName"
        />

        <!-- TODO: add the brush/pan component here. it may
         * be conditional by a new boolean prop like 'showPanningBrush',
         * use 'activeTimeRange' and 'metrics', and
         * trigger updateTimeRange() -->
      </div>

      <GraphLegend
        v-if="showLegend"
        class="graphing-graph-panel__legend"
        :metrics="metrics"
        :horizontal-lines="horizontalLines ?? []"
        :consolidation-fn="activeConsolidationFunction"
        :hidden-metric-names="hiddenMetricNames"
        :hidden-line-names="hiddenLineNames"
        @update:consolidation-fn="updateConsolidationFunction($event)"
        @update:hidden-metric-names="hiddenMetricNames = $event"
        @update:hidden-line-names="hiddenLineNames = $event"
        @hover-metric="highlightedMetricName = $event"
        @request-show-all="
          () => {
            /* TODO: open metric slideout */
          }
        "
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.graphing-graph-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: calc(var(--spacing) * 3);
}

.graphing-graph-panel__meta {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-double);
}

.graphing-graph-panel__container--legend-right {
  display: flex;
  align-items: flex-start;
  gap: calc(var(--spacing) * 3);
}

.graphing-graph-panel__canvas-area {
  flex: 1;
  min-width: 0;
}

.graphing-graph-panel__legend {
  margin-top: calc(var(--spacing) * 2);

  .graphing-graph-panel__container--legend-right & {
    width: 480px;
    flex-shrink: 0;
    margin-top: 0;
  }
}
</style>
