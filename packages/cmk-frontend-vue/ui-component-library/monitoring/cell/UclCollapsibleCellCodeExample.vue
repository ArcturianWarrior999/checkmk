<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'
import { ref } from 'vue'

import EditableTable from '@/monitoring/shared/components/EditableTable.vue'
import CollapsibleCell from '@/monitoring/shared/components/cell/CollapsibleCell.vue'

interface DemoRow {
  id: string
  title: string
}

const rows = ref<DemoRow[]>([{ id: 'a', title: 'CPU utilization — system' }])
const columns: ColumnDef<DemoRow>[] = [{ id: 'title', header: 'Title', meta: { stretch: true } }]

// EditableTable renders the #expansion slot as a row beneath the cell whenever
// expandedRows[rowKey] is true; the cell's chevron toggles that entry.
const expandedRows = ref<Record<string, boolean>>({})
</script>

<template>
  <EditableTable
    :expanded-rows="expandedRows"
    :rows="rows"
    :columns="columns"
    :get-row-key="(row) => row.id"
  >
    <template #row="{ row }">
      <CollapsibleCell
        column-id="title"
        :expanded="expandedRows[row.id] ?? false"
        :controls-id="`expansion-${row.id}`"
        @update:expanded="(value: boolean) => (expandedRows[row.id] = value)"
      >
        <span>{{ row.title }}</span>
      </CollapsibleCell>
    </template>

    <template #expansion="{ row }">
      <td :id="`expansion-${row.id}`">Row-specific detail content.</td>
    </template>
  </EditableTable>
</template>
