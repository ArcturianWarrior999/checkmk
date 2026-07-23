<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed } from 'vue'

import usei18n from '@/lib/i18n'

import CmkDropdown from '@/components/CmkDropdown'
import CmkLabel from '@/components/CmkLabel.vue'

import {
  CONSOLIDATION_FUNCTIONS,
  type ConsolidationFn,
  isConsolidationFn,
  useConsolidationFunctionLabels
} from '@/graphing/components/consolidation'

const { modelValue } = defineProps<{
  modelValue: ConsolidationFn
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ConsolidationFn]
}>()

const { _t } = usei18n()
const labels = useConsolidationFunctionLabels()

const suggestions = computed(() => ({
  type: 'fixed' as const,
  suggestions: CONSOLIDATION_FUNCTIONS.map((name) => ({ name, title: labels.value[name] }))
}))

function onChange(value: string | null): void {
  if (isConsolidationFn(value)) {
    emit('update:modelValue', value)
  }
}
</script>

<template>
  <div class="graphing-consolidation-select">
    <CmkLabel variant="subtitle">{{ _t('Then consolidate by') }}</CmkLabel>
    <CmkDropdown
      :model-value="modelValue"
      :options="suggestions"
      :label="_t('Consolidation function')"
      floating
      @update:model-value="onChange"
    />
  </div>
</template>

<style scoped>
.graphing-consolidation-select {
  display: flex;
  flex-direction: column;
  gap: var(--dimension-3);
}
</style>
