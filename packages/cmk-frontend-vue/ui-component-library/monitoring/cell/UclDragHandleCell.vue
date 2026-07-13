<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script lang="ts">
import { type PanelConfig } from '@ucl/_ucl/components/detail-page'

import codeExample from './UclDragHandleCellCodeExample.vue?raw'

export const panelConfig = {
  verticalAlign: {
    type: 'list' as const,
    title: 'verticalAlign',
    options: [
      { title: 'top', name: 'top' },
      { title: 'middle', name: 'middle' }
    ],
    initialState: 'middle',
    help: 'Vertical alignment of the drag handle within the row.'
  }
} satisfies PanelConfig
</script>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'
import {
  UclDetailPageCodeExample,
  UclDetailPageComponent,
  UclDetailPageHeader,
  UclDetailPageLayout,
  UclPropertiesPanel
} from '@ucl/_ucl/components/detail-page'
import type { InferPanelState } from '@ucl/_ucl/types/prop-panel'
import { computed, ref } from 'vue'

import EditableTable from '@/monitoring/shared/components/EditableTable.vue'
import type { CellVerticalAlign } from '@/monitoring/shared/components/cell/BaseCell.vue'
import DragHandleCell from '@/monitoring/shared/components/cell/DragHandleCell.vue'
import StringCell from '@/monitoring/shared/components/cell/StringCell.vue'

defineProps<{ screenshotMode: boolean }>()

const propState = ref(
  Object.fromEntries(
    Object.entries(panelConfig).map(([key, def]) => [key, def.initialState])
  ) as InferPanelState<typeof panelConfig>
)

const verticalAlign = computed<CellVerticalAlign>(
  () => propState.value.verticalAlign as CellVerticalAlign
)

interface DemoRow {
  id: string
  label: string
}

const rows = ref<DemoRow[]>([
  { id: 'a', label: 'CPU utilization' },
  { id: 'b', label: 'Memory used' },
  { id: 'c', label: 'Disk throughput' },
  { id: 'd', label: 'Network traffic' }
])

const columns: ColumnDef<DemoRow>[] = [
  { id: 'drag', header: '' },
  { id: 'label', header: 'Metric', meta: { stretch: true } }
]

function onReorder(fromIndex: number, toIndex: number): void {
  const next = [...rows.value]
  const moved = next.splice(fromIndex, 1)[0]!
  next.splice(toIndex, 0, moved)
  rows.value = next
}
</script>

<template>
  <UclDetailPageLayout>
    <UclDetailPageHeader>DragHandleCell</UclDetailPageHeader>

    <UclDetailPageComponent>
      <div class="ucl-drag-handle-cell__stack">
        <EditableTable
          :rows="rows"
          :columns="columns"
          :get-row-key="(row) => row.id"
          row-height="40px"
          @reorder="onReorder"
        >
          <template #row="{ row }">
            <DragHandleCell column-id="drag" :vertical-align="verticalAlign" />
            <StringCell column-id="label" :value="row.label" :vertical-align="verticalAlign" />
          </template>
        </EditableTable>

        <p class="ucl-drag-handle-cell__hint">
          Drag a row by its handle to reorder. The handle only renders inside
          <code>EditableTable</code>, which provides the row-drag handlers the cell injects — a
          <code>MonitoringTable</code> would render an empty cell.
        </p>
      </div>

      <template #properties>
        <UclPropertiesPanel v-model="propState" :config="panelConfig" />
      </template>
    </UclDetailPageComponent>

    <UclDetailPageCodeExample :code="codeExample" />
  </UclDetailPageLayout>
</template>

<style scoped>
.ucl-drag-handle-cell__stack {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--dimension-4);
  width: 100%;
  min-width: 0;
}

.ucl-drag-handle-cell__hint {
  margin: 0;
  font-style: italic;
  opacity: 0.7;
}
</style>
