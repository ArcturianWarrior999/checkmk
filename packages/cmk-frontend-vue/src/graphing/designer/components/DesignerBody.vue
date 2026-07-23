<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import type { CustomGraphDesignerMode } from 'cmk-shared-typing/typescript/custom_graph_designer'
import { computed, ref, watch } from 'vue'

import usei18n from '@/lib/i18n'
import type { TranslatedString } from '@/lib/i18nString'
import { useResizeObserver } from '@/lib/useResizeObserver'

import CmkAlertBox from '@/components/CmkAlertBox.vue'
import CmkMultitoneIcon from '@/components/CmkIcon/CmkMultitoneIcon.vue'
import CmkTabs, { CmkTab, CmkTabContent } from '@/components/CmkTabs'

import { useGlobalRefresh } from '../../GlobalRefreshControl/useGlobalRefresh'
import GraphPanel from '../../components/GraphPanel.vue'
import type { ConsolidationFn } from '../../components/consolidation'
import { useRequestedTimeRange } from '../../composables/useRequestedTimeRange'
import { type CustomGraphObject, updateCustomGraph } from '../api'
import { MetricsCalculationSlideout, type RefVisibility } from '../calculation'
import { useCustomGraphData } from '../composables/useCustomGraphData'
import { useDeleteWithDependents } from '../composables/useDeleteWithDependents'
import { useGraphItems } from '../composables/useGraphItems'
import { fromApiDataSource, isComplete, toApiDataSources } from '../drafts'
import type { FormulaDraft, ItemId } from '../types'
import AppearanceTable from './AppearanceTable.vue'
import DeleteWithDependentsPopup from './DeleteWithDependentsPopup.vue'
import MetricsTable from './MetricsTable.vue'

/** Fallback until the container is measured (e.g. non-DOM test environments). */
const DEFAULT_FIGURE_WIDTH = 1000

const {
  graph,
  graphName,
  etag,
  ownerParam,
  mode,
  palette,
  thresholds,
  metricBackendAvailable,
  titleMacroHelp
} = defineProps<{
  graph: CustomGraphObject
  graphName: string
  etag: string | null
  /** Query parameter for foreign graphs; undefined for the user's own graph. */
  ownerParam: string | undefined
  mode: CustomGraphDesignerMode
  palette: readonly string[]
  thresholds: { warning: string; critical: string }
  metricBackendAvailable: boolean
  titleMacroHelp: string
}>()

const emit = defineEmits<{
  saved: [graph: CustomGraphObject, etag: string | null]
}>()

const { _t } = usei18n()

const store = useGraphItems(palette, graph.extensions.content.data_sources.map(fromApiDataSource))
const completeItems = computed(() => store.items.value.filter(isComplete))

const consolidationFn = ref<ConsolidationFn>('max')
// The app seeds the global time range from the configured default before we mount.
const requestedTimeRange = useRequestedTimeRange()

const graphContainer = ref<HTMLElement | null>(null)
const figureWidth = ref(DEFAULT_FIGURE_WIDTH)
const { observe } = useResizeObserver((entries) => {
  const width = entries[0]!.contentBoxSize![0]!.inlineSize
  if (width > 0) {
    figureWidth.value = Math.round(width)
  }
})
observe(graphContainer)

const data = useCustomGraphData({
  getItems: () => store.items.value,
  getGraphOptions: () => graph.extensions.content.graph_options,
  getRequestedTimeRange: () => requestedTimeRange.value,
  getConsolidationFn: () => consolidationFn.value,
  getFigureWidth: () => figureWidth.value,
  withOverview: () => mode === 'view',
  // Edit mode fetches hidden rows too, so the appearance table can show their stats.
  getFetchHidden: () => mode === 'edit'
})

const hiddenSourceIds = computed(
  () => new Set(store.items.value.filter((item) => !item.visible).map((item) => item.id))
)
/** The fetched series minus the ones whose source row is hidden — only these are drawn. */
const drawnMetrics = computed(() =>
  data.metrics.value.filter((metric) => !hiddenSourceIds.value.has(metric.source_id))
)
const drawnOverview = computed(() => {
  const overview = data.overview.value
  return overview === undefined
    ? undefined
    : {
        metrics: overview.metrics.filter((metric) => !hiddenSourceIds.value.has(metric.source_id)),
        timeRange: overview.timeRange
      }
})

const { refreshTick } = useGlobalRefresh()
watch(refreshTick, () => data.refetch())
watch(
  () => mode,
  () => data.refetch()
)

type Tab = 'appearance' | 'metrics'
const activeTab = ref<Tab>('appearance')
const TABS: { id: Tab; label: TranslatedString }[] = [
  { id: 'appearance', label: _t('Graph appearance') },
  { id: 'metrics', label: _t('Metrics selection') }
]

function onTabChange(value: string | number): void {
  if (value === 'appearance' || value === 'metrics') {
    activeTab.value = value
  }
}

const saveError = ref<string | null>(null)
const isSaving = ref(false)

/** Rows the wire format cannot express: incomplete drafts and formulas with broken refs. */
function invalidRowIds(): ItemId[] {
  const keptIds = new Set(toApiDataSources(store.items.value).map((source) => source.id))
  return store.items.value.map((item) => item.id).filter((id) => !keptIds.has(id))
}

async function save(): Promise<void> {
  if (isSaving.value) {
    return
  }
  const invalid = invalidRowIds()
  if (invalid.length > 0) {
    saveError.value = _t(
      'These rows are incomplete or reference incomplete rows and cannot be saved: %{ids}',
      { ids: invalid.join(', ') }
    )
    return
  }
  if (etag === null) {
    saveError.value = _t(
      'The graph was loaded without a version identifier — reload the page before saving.'
    )
    return
  }
  saveError.value = null
  isSaving.value = true
  try {
    const result = await updateCustomGraph(
      graphName,
      etag,
      {
        title: graph.title ?? graphName,
        metadata: graph.extensions.metadata,
        content: {
          graph_options: graph.extensions.content.graph_options,
          data_sources: toApiDataSources(store.items.value)
        }
      },
      ownerParam
    )
    emit('saved', result.graph, result.etag)
  } catch (e) {
    saveError.value = e instanceof Error ? e.message : String(e)
  } finally {
    isSaving.value = false
  }
}

defineExpose({ save })

const slideoutOpen = ref(false)

function applyRefVisibility(refVisibility: RefVisibility): void {
  if (refVisibility !== null) {
    store.setVisibility(refVisibility.ids, refVisibility.visible)
  }
}

function onCalculationAdd(draft: FormulaDraft, refVisibility: RefVisibility): void {
  store.addFormula(draft)
  applyRefVisibility(refVisibility)
}

function onCalculationUpdate(id: ItemId, draft: FormulaDraft, refVisibility: RefVisibility): void {
  store.updateFormula(id, draft)
  applyRefVisibility(refVisibility)
}

const calculationDelete = useDeleteWithDependents(store)
</script>

<template>
  <div
    ref="graphContainer"
    class="graphing-designer-body"
    :class="{ 'graphing-designer-body--edit': mode === 'edit' }"
  >
    <CmkAlertBox v-if="data.error.value !== null" variant="error">
      {{ data.error.value }}
    </CmkAlertBox>

    <GraphPanel
      class="graphing-designer-body__preview"
      :metrics="drawnMetrics"
      :data-time-range="data.dataTimeRange.value"
      :horizontal-lines="data.horizontalLines.value"
      :requested-time-range="requestedTimeRange"
      :title="graph.title ?? graphName"
      show-title
      show-timestamp
      :figure-width="figureWidth"
      :show-legend="mode === 'view'"
      :show-brush="mode === 'view'"
      :overview="drawnOverview"
      @update:requested-time-range="requestedTimeRange = $event"
      @update:consolidation-fn="consolidationFn = $event"
    />

    <template v-if="mode === 'edit'">
      <CmkAlertBox v-if="saveError !== null" variant="error">
        {{ saveError }}
      </CmkAlertBox>

      <CmkTabs
        class="graphing-designer-body__tabs"
        :model-value="activeTab"
        @update:model-value="onTabChange"
      >
        <template #tabs>
          <CmkTab v-for="tab in TABS" :id="tab.id" :key="tab.id">
            <span class="graphing-designer-body__tab-label">
              <span v-if="activeTab === tab.id" class="graphing-designer-body__tab-check">
                <CmkMultitoneIcon name="checkmark" primary-color="font" size="small" />
              </span>
              {{ tab.label }}
            </span>
          </CmkTab>
        </template>
        <template #tab-contents>
          <CmkTabContent id="appearance" class="graphing-designer-body__tab-panel">
            <AppearanceTable :store="store" :metrics-by-source="data.metricsBySource.value" />
          </CmkTabContent>
          <CmkTabContent id="metrics" class="graphing-designer-body__tab-panel">
            <MetricsTable
              :store="store"
              :thresholds="thresholds"
              :metric-backend-available="metricBackendAvailable"
              :title-macro-help="titleMacroHelp"
              @add-calculation="slideoutOpen = true"
            />
          </CmkTabContent>
        </template>
      </CmkTabs>

      <MetricsCalculationSlideout
        :open="slideoutOpen"
        :items="completeItems"
        :next-id="store.nextId.value"
        :next-color="store.nextColor.value"
        @add="onCalculationAdd"
        @update="onCalculationUpdate"
        @delete="(id) => calculationDelete.request([id])"
        @close="slideoutOpen = false"
      />

      <DeleteWithDependentsPopup
        v-if="calculationDelete.pending.value !== null"
        open
        :ids="calculationDelete.pending.value.ids"
        :dependents="calculationDelete.pending.value.dependents"
        @confirm="calculationDelete.confirm()"
        @close="calculationDelete.cancel()"
      />
    </template>
  </div>
</template>

<style scoped>
.graphing-designer-body {
  display: flex;
  flex-direction: column;
  gap: var(--dimension-6);
  padding: var(--dimension-6);
  background: var(--ux-theme-3);
  border-radius: var(--border-radius);
}

.graphing-designer-body--edit {
  flex: 0 1 auto;
  min-height: 0;
  overflow: hidden;
}

.graphing-designer-body--edit .graphing-designer-body__preview {
  flex-shrink: 0;
}

.graphing-designer-body--edit .graphing-designer-body__tabs {
  flex: 0 1 auto;
  min-height: 0;
}

.graphing-designer-body--edit .graphing-designer-body__tab-panel:not([hidden]) {
  display: flex;
  flex-direction: column;
  flex: 0 1 auto;
  min-height: 0;
  background: var(--ux-theme-2);
}

.graphing-designer-body__tab-label {
  display: flex;
  align-items: center;
  gap: var(--dimension-3);
}

.graphing-designer-body__tab-check {
  display: flex;
  line-height: 0;
}
</style>
