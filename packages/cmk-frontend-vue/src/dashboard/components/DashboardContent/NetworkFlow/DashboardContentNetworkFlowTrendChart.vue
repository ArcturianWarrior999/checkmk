<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed, onBeforeMount, ref, watch } from 'vue'

import { CmkApiError } from '@/lib/error'
import usei18n from '@/lib/i18n'
import { SIFormatter } from '@/lib/unit-format/notationFormatter'

import CmkAlertBox from '@/components/CmkAlertBox.vue'
import CmkLoading from '@/components/CmkLoading.vue'

import type { NetworkFlowTrendChartContent } from '@/dashboard/types/widget.ts'
import { dashboardAPI } from '@/dashboard/utils.ts'
import CmkTrendChart, { type TrendChartSeries } from '@/network-flow/CmkTrendChart'

import DashboardContentContainer from '../DashboardContentContainer.vue'
import type { ContentProps } from '../types.ts'

const { _t } = usei18n()
const props = defineProps<ContentProps<NetworkFlowTrendChartContent>>()

// The trend series are per-minute throughput values; format both the axis ticks
// and the legend statistics as bits per second, in the mockups' unit style
// (3_200_000_000 → "3.20 Gbps").
const THROUGHPUT = new SIFormatter('bps', { type: 'strict', digits: 2 })
const formatValue = (value: number): string => THROUGHPUT.render(value)

const series = ref<TrendChartSeries[] | undefined>(undefined)
// A backend-reported condition (flow monitoring disabled, database unreachable,
// query failed) is an expected state shown as a warning; anything unexpected is
// an error - mirroring the other network flow widgets.
const error = ref<{ variant: 'warning' | 'error'; message: string } | null>(null)

const fetchData = async (): Promise<void> => {
  error.value = null
  try {
    const response = await dashboardAPI.computeNetworkFlowTrendChartData(
      props.content,
      props.effective_filter_context.filters
    )
    series.value = response.value.series.map((item) => ({
      name: item.name,
      dataPoints: item.data_points,
      minimum: item.minimum,
      maximum: item.maximum,
      average: item.average,
      last: item.last
    }))
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
    <div class="db-content-network-flow-trend-chart__wrapper">
      <div v-if="error" class="db-content-network-flow-trend-chart__error">
        <CmkAlertBox :variant="error.variant">{{ error.message }}</CmkAlertBox>
      </div>
      <CmkLoading v-else-if="series === undefined" />
      <CmkTrendChart
        v-else
        :series="series"
        :display-mode="content.display_mode"
        :format-value="formatValue"
      />
    </div>
  </DashboardContentContainer>
</template>

<style scoped>
.db-content-network-flow-trend-chart__wrapper {
  display: flex;
  flex: 1;
  min-height: 0;
  padding: calc(var(--spacing) * 2);
}

.db-content-network-flow-trend-chart__error {
  margin: auto;
  max-width: 90%;
}
</style>
