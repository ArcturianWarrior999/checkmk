<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'
import { ref } from 'vue'

import EditableTable from '@/monitoring/shared/components/EditableTable.vue'
import DragHandleCell from '@/monitoring/shared/components/cell/DragHandleCell.vue'
import StringCell from '@/monitoring/shared/components/cell/StringCell.vue'

// The DragHandleCell only renders its handle when it can inject the row-drag
// handlers that EditableTable provides.

interface DemoRow {
  id: string
  label: string
}

const rows = ref<DemoRow[]>([
  { id: 'a', label: 'CPU utilization' },
  { id: 'b', label: 'Memory used' },
  { id: 'c', label: 'Disk throughput' }
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
  <EditableTable
    :rows="rows"
    :columns="columns"
    :get-row-key="(row) => row.id"
    row-height="40px"
    @reorder="onReorder"
  >
    <template #row="{ row }">
      <DragHandleCell column-id="drag" vertical-align="middle" />
      <StringCell column-id="label" :value="row.label" vertical-align="middle" />
    </template>
  </EditableTable>
</template>
