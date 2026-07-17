<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'
import { computed } from 'vue'

import usei18n from '@/lib/i18n'

import CmkScrollContainer from '@/components/CmkScrollContainer.vue'

import EditableTable from '@/monitoring/shared/components/EditableTable.vue'
import BaseCell from '@/monitoring/shared/components/cell/BaseCell.vue'
import ColorPickerCell from '@/monitoring/shared/components/cell/ColorPickerCell.vue'
import DragHandleCell from '@/monitoring/shared/components/cell/DragHandleCell.vue'
import DropdownCell from '@/monitoring/shared/components/cell/DropdownCell.vue'
import SwitchCell from '@/monitoring/shared/components/cell/SwitchCell.vue'
import VisibilityCell from '@/monitoring/shared/components/cell/VisibilityCell.vue'

import type { Metric } from '../../components/TimeSeriesGraph'
import { type MetricStats, metricStats } from '../../components/legend/legendUtils'
import type { GraphItemsStore } from '../composables/useGraphItems'
import { useRowLabels } from '../composables/useRowLabels'
import type { DesignerItem } from '../drafts'
import { type ItemId, isSingleLine, parseLineType } from '../types'

const { store, metricsBySource } = defineProps<{
  store: GraphItemsStore
  /** Fetched series per data-source row, for the live-data columns. */
  metricsBySource: Map<ItemId, Metric[]>
}>()

const { _t } = usei18n()
const { sourceTypeLabel, lineStyleSuggestions, lineStyleLabel } = useRowLabels()

const columns: ColumnDef<DesignerItem>[] = [
  { id: 'drag', header: '', meta: { justify: 'center' } },
  { id: 'visibility', header: '', meta: { justify: 'center' } },
  { id: 'id', header: _t('ID'), meta: { justify: 'left' } },
  { id: 'source', header: _t('Source'), meta: { justify: 'left' } },
  { id: 'color', header: _t('Color'), meta: { justify: 'center' } },
  { id: 'title', header: _t('Title'), minSize: 200, meta: { stretch: true } },
  { id: 'line_style', header: _t('Line style'), meta: { justify: 'left' } },
  { id: 'mirrored', header: _t('Mirrored'), meta: { justify: 'center' } },
  { id: 'min', header: _t('Min'), meta: { justify: 'right' } },
  { id: 'avg', header: _t('Average'), meta: { justify: 'right' } },
  { id: 'max', header: _t('Max'), meta: { justify: 'right' } },
  { id: 'last', header: _t('Last'), meta: { justify: 'right' } }
]

/** Row stats are only attributable when the row produced exactly one series. */
const statsBySource = computed(() => {
  const stats = new Map<ItemId, MetricStats>()
  for (const [id, series] of metricsBySource) {
    if (series.length === 1) {
      stats.set(id, metricStats(series[0]!))
    }
  }
  return stats
})

function onLineStyleChange(row: DesignerItem, value: string | null): void {
  const lineType = parseLineType(value)
  if (lineType !== undefined) {
    store.patch(row.id, { line_type: lineType })
  }
}
</script>

<template>
  <CmkScrollContainer
    type="outer"
    height="auto"
    max-height="none"
    class="graphing-appearance-table"
  >
    <EditableTable
      :rows="[...store.items.value]"
      :columns="columns"
      :get-row-key="(row: DesignerItem) => row.id"
      @reorder="(from: number, to: number) => store.move(from, to)"
    >
      <template #row="{ row }">
        <DragHandleCell column-id="drag" vertical-align="middle" />
        <VisibilityCell
          column-id="visibility"
          vertical-align="middle"
          :model-value="row.visible"
          @update:model-value="store.setVisibility([row.id], $event)"
        />
        <BaseCell column-id="id" vertical-align="middle">{{ row.id }}</BaseCell>
        <BaseCell column-id="source" vertical-align="middle" no-wrap>{{
          sourceTypeLabel(row.type)
        }}</BaseCell>
        <ColorPickerCell
          v-if="isSingleLine(row)"
          column-id="color"
          vertical-align="middle"
          :model-value="row.color"
          @update:model-value="store.patch(row.id, { color: $event })"
        />
        <BaseCell v-else column-id="color" vertical-align="middle" />
        <BaseCell column-id="title" vertical-align="middle" no-wrap>{{ row.title }}</BaseCell>
        <DropdownCell
          column-id="line_style"
          vertical-align="middle"
          :model-value="row.line_type"
          :options="lineStyleSuggestions"
          :label="lineStyleLabel"
          @update:model-value="onLineStyleChange(row, $event)"
        />
        <SwitchCell
          column-id="mirrored"
          vertical-align="middle"
          :model-value="row.mirrored"
          @update:model-value="store.patch(row.id, { mirrored: $event })"
        />
        <BaseCell column-id="min" vertical-align="middle">{{
          statsBySource.get(row.id)?.min
        }}</BaseCell>
        <BaseCell column-id="avg" vertical-align="middle">{{
          statsBySource.get(row.id)?.avg
        }}</BaseCell>
        <BaseCell column-id="max" vertical-align="middle">{{
          statsBySource.get(row.id)?.max
        }}</BaseCell>
        <BaseCell column-id="last" vertical-align="middle">{{
          statsBySource.get(row.id)?.last
        }}</BaseCell>
      </template>
      <template #empty-state>
        {{ _t('This graph has no data sources yet.') }}
      </template>
    </EditableTable>
  </CmkScrollContainer>
</template>

<style scoped>
.graphing-appearance-table {
  flex: 0 1 auto;
  min-height: 0;
}
</style>
