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

import type { NetworkFlowTopTableContent } from '@/dashboard/types/widget.ts'
import { dashboardAPI } from '@/dashboard/utils.ts'
import CmkRankedTable from '@/network-flow/CmkRankedTable'
import type { ChartColor, RankedTableColumn, RankedTableRow } from '@/network-flow/CmkRankedTable'

import DashboardContentContainer from '../DashboardContentContainer.vue'
import type { ContentProps } from '../types.ts'

const { _t } = usei18n()
const props = defineProps<ContentProps<NetworkFlowTopTableContent>>()

const columns = ref<RankedTableColumn[] | undefined>(undefined)
const rows = ref<RankedTableRow[] | undefined>(undefined)
// A backend-reported condition (flow monitoring disabled, database unreachable,
// query failed) is an expected state shown as a warning; anything unexpected is
// an error - mirroring how the ntop widget distinguishes severity.
const error = ref<{ variant: 'warning' | 'error'; message: string } | null>(null)

// The widget's accent values name colors of the chart palette, so the
// configuration passes straight through (the assignment is type-checked).
const barColor = computed<ChartColor>(() => props.content.accent)

const fetchData = async (): Promise<void> => {
  error.value = null
  try {
    const response = await dashboardAPI.computeNetworkFlowTopTableData(
      props.content,
      props.effective_filter_context.filters
    )
    columns.value = response.value.columns
    rows.value = response.value.rows
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
    <div class="db-content-network-flow-top-table__wrapper">
      <div v-if="error" class="db-content-network-flow-top-table__error">
        <CmkAlertBox :variant="error.variant">{{ error.message }}</CmkAlertBox>
      </div>
      <CmkLoading v-else-if="columns === undefined || rows === undefined" />
      <CmkRankedTable v-else :columns="columns" :rows="rows" :bar-color="barColor" />
    </div>
  </DashboardContentContainer>
</template>

<style scoped>
.db-content-network-flow-top-table__wrapper {
  display: flex;
  flex: 1;
  min-height: 0;
  padding: var(--spacing);
}

.db-content-network-flow-top-table__error {
  margin: auto;
  max-width: 90%;
}
</style>
