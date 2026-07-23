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

import type { NetworkFlowKpiStatCardContent } from '@/dashboard/types/widget.ts'
import { dashboardAPI } from '@/dashboard/utils.ts'
import CmkKpiStatCard, { type DeltaSemantics } from '@/network-flow/CmkKpiStatCard'

import DashboardContentContainer from '../DashboardContentContainer.vue'
import type { ContentProps } from '../types.ts'

const { _t } = usei18n()
const props = defineProps<ContentProps<NetworkFlowKpiStatCardContent>>()

// How each metric presents itself: the unit formatting follows the metric
// (bytes scale to KB/MB/GB..., counts to K/M/...) and the delta coloring
// follows what an increase of the metric MEANS, not its direction alone.
// Everything the widget launches with is neutral; a future "up is bad"
// metric (e.g. engaged alerts) declares itself here.
interface MetricPresentation {
  formatter: SIFormatter
  deltaSemantics: DeltaSemantics
}

// Canonical SI byte formatter (base 1000), matching CmkRankedTable: 801_840_000_000 → "801.84 GB".
const BYTES = new SIFormatter('B', { type: 'strict', digits: 2 })
// Unitless activity counts: 532 → "532", 4_300 → "4.3 K".
const COUNT = new SIFormatter('', { type: 'strict', digits: 1 })
// Rates in bits per second, in the mockups' unit style: 3_200_000_000 → "3.20 Gbps".
const THROUGHPUT = new SIFormatter('bps', { type: 'strict', digits: 2 })

const METRIC_PRESENTATION: Record<NetworkFlowKpiStatCardContent['metric'], MetricPresentation> = {
  total_bytes: { formatter: BYTES, deltaSemantics: 'neutral' },
  ingress_bytes: { formatter: BYTES, deltaSemantics: 'neutral' },
  egress_bytes: { formatter: BYTES, deltaSemantics: 'neutral' },
  active_hosts: { formatter: COUNT, deltaSemantics: 'neutral' },
  total_flows: { formatter: COUNT, deltaSemantics: 'neutral' },
  active_asn: { formatter: COUNT, deltaSemantics: 'neutral' },
  peak_throughput: { formatter: THROUGHPUT, deltaSemantics: 'neutral' },
  avg_throughput: { formatter: THROUGHPUT, deltaSemantics: 'neutral' }
}

interface CardData {
  value: string
  unit: string | undefined
  deltaRatio: number | undefined
  series: number[]
}

const data = ref<CardData | undefined>(undefined)
// A backend-reported condition (flow monitoring disabled, database unreachable,
// query failed) is an expected state shown as a warning; anything unexpected is
// an error - mirroring how the ntop widget distinguishes severity.
const error = ref<{ variant: 'warning' | 'error'; message: string } | null>(null)

const presentation = computed(() => METRIC_PRESENTATION[props.content.metric])

function buildCardData(value: number, previousValue: number, series: number[]): CardData {
  // The card renders the value and its unit in different sizes, so the
  // formatter's "801.84 GB" is split at the first space; plain counts
  // ("532") have no unit part.
  const rendered = presentation.value.formatter.render(value)
  const spaceIndex = rendered.indexOf(' ')
  // A delta needs a positive reference: a zero previous window means "no
  // comparison possible", not an infinite increase.
  const deltaRatio =
    props.content.show_delta && previousValue > 0
      ? (value - previousValue) / previousValue
      : undefined
  return {
    value: spaceIndex === -1 ? rendered : rendered.slice(0, spaceIndex),
    unit: spaceIndex === -1 ? undefined : rendered.slice(spaceIndex + 1),
    deltaRatio,
    series
  }
}

const fetchData = async (): Promise<void> => {
  error.value = null
  try {
    const response = await dashboardAPI.computeNetworkFlowKpiStatCardData(
      props.content,
      props.effective_filter_context.filters
    )
    data.value = buildCardData(
      response.value.value,
      response.value.previous_value,
      response.value.series
    )
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
    <div class="db-content-network-flow-kpi-stat-card__wrapper">
      <div v-if="error" class="db-content-network-flow-kpi-stat-card__error">
        <CmkAlertBox :variant="error.variant">{{ error.message }}</CmkAlertBox>
      </div>
      <CmkLoading v-else-if="data === undefined" />
      <CmkKpiStatCard
        v-else
        :value="data.value"
        :unit="data.unit"
        :delta-ratio="data.deltaRatio"
        :delta-semantics="presentation.deltaSemantics"
        :series="data.series"
        :color="content.accent"
      />
    </div>
  </DashboardContentContainer>
</template>

<style scoped>
.db-content-network-flow-kpi-stat-card__wrapper {
  display: flex;
  flex: 1;
  min-height: 0;
  padding: calc(var(--spacing) * 2);
}

.db-content-network-flow-kpi-stat-card__error {
  margin: auto;
  max-width: 90%;
}
</style>
