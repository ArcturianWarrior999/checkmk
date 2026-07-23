<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed, onBeforeMount, ref, watch } from 'vue'

import { CmkApiError } from '@/lib/error'
import usei18n from '@/lib/i18n'

import CmkAlertBox from '@/components/CmkAlertBox.vue'
import CmkLoading from '@/components/CmkLoading.vue'

import type { NetworkFlowDonutContent } from '@/dashboard/types/widget.ts'
import { dashboardAPI } from '@/dashboard/utils.ts'
import CmkDonutChart, { type ChartColor, type DonutSlice } from '@/network-flow/CmkDonutChart'

import DashboardContentContainer from '../DashboardContentContainer.vue'
import type { ContentProps } from '../types.ts'

const { _t } = usei18n()
const props = defineProps<ContentProps<NetworkFlowDonutContent>>()

// Slice colors are presentation, so the palette lives here rather than in the
// config. Slices cycle through the accent palette; the aggregated "Other" tail
// always uses the neutral grey.
const SLICE_PALETTE: ChartColor[] = ['green', 'blue', 'magenta', 'yellow', 'orange', 'purple']

const slices = ref<DonutSlice[] | undefined>(undefined)
// A backend-reported condition (flow monitoring disabled, database unreachable,
// query failed) is an expected state shown as a warning; anything unexpected is
// an error - mirroring how the ntop widget distinguishes severity.
const error = ref<{ variant: 'warning' | 'error'; message: string } | null>(null)

function buildSlices(
  computedSlices: { label: string; value: number }[],
  total: number
): DonutSlice[] {
  const result: DonutSlice[] = computedSlices.map((slice, index) => ({
    key: `slice-${index}`,
    label: slice.label,
    value: slice.value,
    color: SLICE_PALETTE[index % SLICE_PALETTE.length]!
  }))
  // The backend returns the grand total across all entities, so the tail beyond
  // the ranked slices becomes an aggregated "Other" slice.
  const shown = computedSlices.reduce((sum, slice) => sum + slice.value, 0)
  const other = total - shown
  if (other > 0) {
    result.push({ key: 'other', label: _t('Other'), value: other, color: 'grey' })
  }
  return result
}

const fetchData = async (): Promise<void> => {
  error.value = null
  try {
    const response = await dashboardAPI.computeNetworkFlowDonutData(
      props.content,
      props.effective_filter_context.filters
    )
    slices.value = buildSlices(response.value.slices, response.value.total)
  } catch (e) {
    error.value =
      e instanceof CmkApiError
        ? { variant: 'warning', message: e.message }
        : { variant: 'error', message: _t('Failed to load the widget data') }
  }
}

onBeforeMount(() => void fetchData())

const dataParameters = computed(() =>
  JSON.stringify({ filters: props.effective_filter_context.filters, content: props.content })
)
watch(dataParameters, () => void fetchData())
</script>

<template>
  <DashboardContentContainer
    :effective-title="effectiveTitle"
    :general_settings="general_settings"
    content-overflow="hidden"
  >
    <div class="db-content-network-flow-donut__wrapper">
      <div v-if="error" class="db-content-network-flow-donut__error">
        <CmkAlertBox :variant="error.variant">{{ error.message }}</CmkAlertBox>
      </div>
      <CmkLoading v-else-if="slices === undefined" />
      <CmkDonutChart v-else :slices="slices" />
    </div>
  </DashboardContentContainer>
</template>

<style scoped>
.db-content-network-flow-donut__wrapper {
  display: flex;
  flex: 1;
  min-height: 0;
  padding: calc(var(--spacing) * 2);
}

.db-content-network-flow-donut__error {
  margin: auto;
  max-width: 90%;
}
</style>
