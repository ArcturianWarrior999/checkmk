<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import CmkPerfometer from '@/components/CmkPerfometer.vue'

import BaseCell, { type CellLink } from './BaseCell.vue'

// TODO(CMK-36919): source this data from the OpenAPI-generated perfometer type
// (components['schemas'][...]) once the services-of-a-host endpoint exposes it,
// mirroring how ModeInfo is consumed in shared/api/types.ts.
export interface PerfometerData {
  value: number
  valueRange: [number, number]
  formatted: string
  color: string
}

export interface PerfometerCellProps {
  data?: PerfometerData | undefined
  stale?: boolean | undefined
  linkedTo?: CellLink | undefined
  columnId?: string | undefined
}

const props = defineProps<PerfometerCellProps>()
</script>

<template>
  <BaseCell :column-id="columnId" :linked-to="linkedTo" vertical-align="middle">
    <template #default>
      <CmkPerfometer
        v-if="props.data"
        :class="{ 'monitoring-perfometer-cell--stale': stale }"
        :value="props.data.value"
        :value-range="props.data.valueRange"
        :formatted="props.data.formatted"
        :color="props.data.color"
      />
    </template>
  </BaseCell>
</template>

<style scoped>
.monitoring-perfometer-cell--stale {
  filter: saturate(0%);
}
</style>
