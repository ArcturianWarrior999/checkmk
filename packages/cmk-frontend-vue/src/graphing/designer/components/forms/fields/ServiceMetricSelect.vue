<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import type { Autocompleter } from 'cmk-shared-typing/typescript/vue_formspec_components'
import { computed } from 'vue'

import usei18n from '@/lib/i18n'
import type { TranslatedString } from '@/lib/i18nString'

import CmkLabel from '@/components/CmkLabel.vue'
import type { ConfiguredFilters } from '@/components/filter'
import CmkLabelRequired from '@/components/user-input/CmkLabelRequired.vue'

import FormAutocompleter from '@/form/private/FormAutocompleter/FormAutocompleter.vue'

const {
  modelValue,
  context,
  placeholder,
  required = false,
  showIndependentOfContext = false
} = defineProps<{
  modelValue: string | null
  context: ConfiguredFilters
  placeholder?: TranslatedString
  required?: boolean
  /** Resolve metric suggestions from the filter context even without an exact host+service. */
  showIndependentOfContext?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()

const { _t } = usei18n()

const metricAutocompleter = computed<Autocompleter>(() => ({
  fetch_method: 'rest_autocomplete',
  data: {
    ident: 'monitored_metrics',
    params: { show_independent_of_context: showIndependentOfContext, strict: true, context }
  }
}))
</script>

<template>
  <div class="graphing-service-metric-select">
    <CmkLabel variant="subtitle"
      >{{ _t('Service metric') }}<CmkLabelRequired :show="required" space="before"
    /></CmkLabel>
    <FormAutocompleter
      :model-value="modelValue"
      :autocompleter="metricAutocompleter"
      :size="0"
      :placeholder="placeholder ?? _t('Select metric')"
      width="wide"
      floating
      @update:model-value="emit('update:modelValue', $event)"
    />
  </div>
</template>

<style scoped>
.graphing-service-metric-select {
  display: flex;
  flex-direction: column;
  gap: var(--dimension-3);
}
</style>
