<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script lang="ts">
import { type PanelConfig } from '@ucl/_ucl/components/detail-page'

import codeExample from './UclVisibilityCellCodeExample.vue?raw'

export const panelConfig = {
  visible: {
    type: 'boolean' as const,
    title: 'visible',
    initialState: true,
    help: 'Whether the eye icon shows the visible or hidden state. Bound via v-model.'
  },
  justify: {
    type: 'list' as const,
    title: 'justify',
    options: [
      { title: 'left', name: 'left' },
      { title: 'center', name: 'center' },
      { title: 'right', name: 'right' }
    ],
    initialState: 'center',
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
import type { ColumnDef, ColumnFiltersState, SortingState } from '@tanstack/vue-table'
import {
  UclDetailPageCodeExample,
  UclDetailPageComponent,
  UclDetailPageHeader,
  UclDetailPageLayout,
  UclPropertiesPanel
} from '@ucl/_ucl/components/detail-page'
import type { InferPanelState } from '@ucl/_ucl/types/prop-panel'
import { computed, ref } from 'vue'

import MonitoringTable from '@/monitoring/shared/components/MonitoringTable.vue'
import type { ColumnJustify } from '@/monitoring/shared/components/MonitoringTableContext'
import type { CellVerticalAlign } from '@/monitoring/shared/components/cell/BaseCell.vue'
import VisibilityCell from '@/monitoring/shared/components/cell/VisibilityCell.vue'

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

type DemoRow = { id: string }

const rows: DemoRow[] = [{ id: 'demo' }]
const sortState = ref<SortingState>([])
const filterState = ref<ColumnFiltersState>([])

const columns = computed<ColumnDef<DemoRow>[]>(() => [
  {
    id: 'cell',
    header: 'Visible',
    minSize: 60,
    maxSize: 120,
    meta: { justify: justify.value }
  }
])
</script>

<template>
  <UclDetailPageLayout>
    <UclDetailPageHeader>VisibilityCell</UclDetailPageHeader>

    <UclDetailPageComponent>
      <div class="ucl-visibility-cell__table-wrap">
        <MonitoringTable
          :rows="rows"
          :fetch-state="'idle'"
          :has-loaded="true"
          :columns="columns"
          :sort-state="sortState"
          :filter-state="filterState"
          @update:sort-state="sortState = $event"
          @update:filter-state="filterState = $event"
        >
          <template #row>
            <VisibilityCell
              v-model="propState.visible"
              column-id="cell"
              :vertical-align="verticalAlign"
            />
          </template>
        </MonitoringTable>
      </div>

      <template #properties>
        <UclPropertiesPanel v-model="propState" :config="panelConfig" />
      </template>
    </UclDetailPageComponent>

    <UclDetailPageCodeExample :code="codeExample" />
  </UclDetailPageLayout>
</template>

<style scoped>
.ucl-visibility-cell__table-wrap {
  width: 100%;
}

/* The demo has a single sized column. MonitoringTable stretches its table to
   width: 100%, which (with table-layout: fixed) would spread the slack onto that
   lone column and hide its size. Let the table size to its columns instead. */
/* stylelint-disable-next-line selector-pseudo-class-no-unknown, checkmk/vue-bem-naming-convention */
.ucl-visibility-cell__table-wrap :deep(.monitoring-table__table) {
  width: auto;
}
</style>
