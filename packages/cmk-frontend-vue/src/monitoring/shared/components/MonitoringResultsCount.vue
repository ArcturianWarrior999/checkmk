<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed, inject } from 'vue'

import usei18n from '@/lib/i18n'

import { MONITORING_SERVICE } from './MonitoringTableContext'

const { _t } = usei18n()

const monitoringService = inject(MONITORING_SERVICE)

const narrowed = computed(
  () =>
    (monitoringService?.filters.activeFilterCount ?? 0) > 0 ||
    (monitoringService?.committedSearchQuery.value ?? '') !== ''
)

const matched = computed(() => monitoringService?.matched.value ?? 0)

const visible = computed(() => narrowed.value && matched.value > 0)

const label = computed(() => _t('Rows matching your criteria: %{count}', { count: matched.value }))
</script>

<template>
  <p class="monitoring-results-count" aria-live="polite">{{ visible ? label : '' }}</p>
</template>

<style scoped>
.monitoring-results-count {
  min-height: 1lh;
  margin: 0;
}
</style>
