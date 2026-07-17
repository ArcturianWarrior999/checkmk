<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import type { components } from 'cmk-shared-typing/typescript/openapi_internal'
import { computed, onMounted, ref, watch } from 'vue'

import usei18n from '@/lib/i18n'
import client, { unwrap } from '@/lib/rest-api-client/client'
import { staticAssertNever } from '@/lib/typeUtils'

import CmkIcon from '@/components/CmkIcon'

import type {
  CombinedGraphContent,
  PerformanceGraphContent,
  SingleTimeseriesContent
} from '@/dashboard/types/widget.ts'
import GraphFigure from '@/graphing/components/GraphFigure/GraphFigure.vue'

import DashboardContentContainer from './DashboardContentContainer.vue'
import type { ContentProps } from './types.ts'

type DiscoveredGraph = components['schemas']['ApiDiscoveredGraph']

const { _t } = usei18n()
const props =
  defineProps<
    ContentProps<PerformanceGraphContent | SingleTimeseriesContent | CombinedGraphContent>
  >()

const shell = ref<DiscoveredGraph | null>(null)
const errorMessage = ref<string | null>(null)
const isDiscovering = ref<boolean>(true)

const singleContext = computed(() => {
  const filters = props.effective_filter_context.filters
  return {
    host: filters['host']?.['host'] ?? null,
    service: filters['service']?.['service'] ?? null,
    site: filters['site']?.['site'] ?? null
  }
})

// Latest-wins: discard responses of superseded requests.
let requestCounter = 0

// Mirrors the legacy SingleTimeseriesDashlet._metric_color mapping.
const DEFAULT_THEME_COLOR = '#008EFF'

const resolveTimeseriesColor = (color: SingleTimeseriesContent['color']): string | null => {
  if (color === 'default_metric') {
    return null
  }
  return color === 'default_theme' ? DEFAULT_THEME_COLOR : color
}

type GraphDiscovery = { graphs: DiscoveredGraph[] } | { error: string }

const discoverGraphs = async (): Promise<GraphDiscovery> => {
  const content = props.content
  const { host, service, site } = singleContext.value
  switch (content.type) {
    case 'single_timeseries':
      if (host === null || service === null) {
        return { error: _t('Missing needed host and service parameters.') }
      }
      return unwrap(
        await client.POST('/domain-types/graph/actions/discover_single_timeseries_graphs/invoke', {
          params: { header: { 'Content-Type': 'application/json' } },
          body: {
            hostname: host,
            service_description: service,
            metric: content.metric,
            color: resolveTimeseriesColor(content.color)
          }
        })
      )
    case 'performance_graph':
      if (host === null || service === null) {
        return { error: _t('Missing needed host and service parameters.') }
      }
      // A numeric source is a pre-2.0 1-based index that cannot be resolved here.
      if (typeof content.source === 'number') {
        return {
          error: _t(
            'This widget references its graph by a deprecated index. Please edit the widget and re-select the graph.'
          )
        }
      }
      return unwrap(
        await client.POST('/domain-types/graph/actions/discover_template_graphs/invoke', {
          params: { header: { 'Content-Type': 'application/json' } },
          body: {
            hostname: host,
            service_description: service,
            site,
            graph_id: content.source
          }
        })
      )
    case 'combined_graph':
      return unwrap(
        await client.POST('/domain-types/graph/actions/discover_combined_graphs/invoke', {
          params: { header: { 'Content-Type': 'application/json' } },
          body: {
            context: props.effective_filter_context.filters,
            graph_id: content.graph_template
          }
        })
      )
    default:
      staticAssertNever(content)
      return { graphs: [] }
  }
}

const loadGraph = async () => {
  const counter = ++requestCounter
  try {
    const discovery = await discoverGraphs()
    if (counter !== requestCounter) {
      return
    }
    if ('error' in discovery) {
      errorMessage.value = discovery.error
    } else {
      shell.value = discovery.graphs[0] ?? null
      errorMessage.value = null
    }
    isDiscovering.value = false
  } catch (error) {
    if (counter !== requestCounter) {
      return
    }
    errorMessage.value = `${_t('Failed to load graph:')} ${(error as Error).message}`
    isDiscovering.value = false
  }
}

const discoveryKey = computed(() => {
  const content = props.content
  switch (content.type) {
    case 'single_timeseries':
      return { metric: content.metric, color: content.color, context: singleContext.value }
    case 'performance_graph':
      return { source: content.source, context: singleContext.value }
    case 'combined_graph':
      return {
        graph_template: content.graph_template,
        context: props.effective_filter_context.filters
      }
    default:
      staticAssertNever(content)
      return {}
  }
})

watch(
  () => JSON.stringify(discoveryKey.value),
  () => void loadGraph()
)

const showLegend = computed(() => props.content.graph_render_options?.show_legend ?? false)
const showTimestamp = computed(() => props.content.graph_render_options?.show_graph_time ?? false)
const combinationMode = computed(() => {
  const content = props.content
  return content.type === 'combined_graph' ? content.presentation : null
})

onMounted(() => {
  void loadGraph()
})
</script>

<template>
  <DashboardContentContainer
    :effective-title="effectiveTitle"
    :general_settings="general_settings"
    content-overflow="hidden"
    :is-scrollable-preview="(isPreview ?? false) && showLegend"
  >
    <div
      class="db-content-time-series-graph"
      :class="{ 'db-content-time-series-graph--preview': isPreview }"
    >
      <CmkIcon
        v-if="isDiscovering"
        name="load-graph"
        size="xlarge"
        class="db-content-time-series-graph__loading-icon"
      />
      <div v-else-if="errorMessage" class="db-content-time-series-graph__error error">
        {{ errorMessage }}
      </div>
      <GraphFigure
        v-else-if="shell"
        :graph-type="shell.graph_type"
        :internal="shell.internal"
        :timerange="content.timerange"
        :combination-mode="combinationMode"
        :show-legend="showLegend"
        :show-timestamp="showTimestamp"
      />
    </div>
  </DashboardContentContainer>
</template>

<style scoped>
.db-content-time-series-graph {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;

  &.db-content-time-series-graph--preview {
    pointer-events: none;
  }
}

.db-content-time-series-graph__loading-icon {
  margin: auto;
}

.db-content-time-series-graph__error {
  padding: var(--dimension-6);
}
</style>
