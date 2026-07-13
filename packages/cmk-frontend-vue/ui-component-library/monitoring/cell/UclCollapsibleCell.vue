<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script lang="ts">
import { type PanelConfig } from '@ucl/_ucl/components/detail-page'

import codeExample from './UclCollapsibleCellCodeExample.vue?raw'

export const panelConfig = {
  expanded: {
    type: 'boolean' as const,
    title: 'expanded',
    initialState: false,
    help: 'Whether the chevron points down (expanded). The owning table renders the #expansion row beneath the cell while true.'
  },
  justify: {
    type: 'list' as const,
    title: 'justify',
    options: [
      { title: 'left', name: 'left' },
      { title: 'center', name: 'center' },
      { title: 'right', name: 'right' }
    ],
    initialState: 'left',
    help: 'Horizontal alignment of the cell content.'
  },
  verticalAlign: {
    type: 'list' as const,
    title: 'verticalAlign',
    options: [
      { title: 'top', name: 'top' },
      { title: 'middle', name: 'middle' }
    ],
    initialState: 'middle',
    help: 'Vertical alignment of the cell content within the row.'
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
import type { ColumnJustify } from '@/monitoring/shared/components/MonitoringTableContext'
import type { CellVerticalAlign } from '@/monitoring/shared/components/cell/BaseCell.vue'
import CollapsibleCell from '@/monitoring/shared/components/cell/CollapsibleCell.vue'

defineProps<{ screenshotMode: boolean }>()

const propState = ref(
  Object.fromEntries(
    Object.entries(panelConfig).map(([key, def]) => [key, def.initialState])
  ) as InferPanelState<typeof panelConfig>
)

const justify = computed<ColumnJustify>(() => propState.value.justify as ColumnJustify)
const verticalAlign = computed<CellVerticalAlign>(
  () => propState.value.verticalAlign as CellVerticalAlign
)

interface DemoRow {
  id: string
  title: string
}

const rows = ref<DemoRow[]>([{ id: 'demo', title: 'CPU utilization — system' }])

const expandedRows = computed<Record<string, boolean>>(() => ({
  demo: propState.value.expanded
}))

const columns = computed<ColumnDef<DemoRow>[]>(() => [
  { id: 'title', header: 'Title', meta: { justify: justify.value, stretch: true } }
])
</script>

<template>
  <UclDetailPageLayout>
    <UclDetailPageHeader>CollapsibleCell</UclDetailPageHeader>

    <UclDetailPageComponent>
      <div class="ucl-collapsible-cell__viewport">
        <EditableTable
          :rows="rows"
          :columns="columns"
          :get-row-key="(row) => row.id"
          :expanded-rows="expandedRows"
        >
          <template #row="{ row }">
            <CollapsibleCell
              column-id="title"
              :expanded="propState.expanded"
              :controls-id="`expansion-${row.id}`"
              :vertical-align="verticalAlign"
              @update:expanded="propState.expanded = $event"
            >
              <span>{{ row.title }}</span>
            </CollapsibleCell>
          </template>

          <template #expansion="{ row }">
            <td :id="`expansion-${row.id}`">
              <div class="ucl-collapsible-cell__expansion-panel">
                Row-specific detail content for “{{ row.title }}” — an arbitrary form goes here.
              </div>
            </td>
          </template>
        </EditableTable>
      </div>

      <template #properties>
        <UclPropertiesPanel v-model="propState" :config="panelConfig" />
      </template>
    </UclDetailPageComponent>

    <UclDetailPageCodeExample :code="codeExample" />
  </UclDetailPageLayout>
</template>

<style scoped>
.ucl-collapsible-cell__viewport {
  width: 420px;
  max-width: 100%;
}

.ucl-collapsible-cell__expansion-panel {
  margin: var(--dimension-4) 0;
  padding: var(--dimension-6);
  background: var(--ux-theme-2);
  border-radius: var(--border-radius);
}
</style>
