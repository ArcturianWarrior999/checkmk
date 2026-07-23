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

const total = computed(() => monitoringService?.total.value ?? 0)

const label = computed(() => _t('Total rows: %{total}', { total: total.value }))
</script>

<template>
  <p v-if="total > 0" class="monitoring-total-count">{{ label }}</p>
</template>

<style scoped>
.monitoring-total-count {
  margin: 0;
  white-space: nowrap;
}
</style>
