<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import usei18n from '@/lib/i18n'
import useId from '@/lib/useId'

import CmkDropdown from '@/components/CmkDropdown'
import CmkHelpText from '@/components/CmkHelpText.vue'
import CmkLabel from '@/components/CmkLabel.vue'
import type { Suggestions } from '@/components/CmkSuggestions'
import CmkInlineValidation from '@/components/user-input/CmkInlineValidation.vue'

import type { ItemId } from '../../types'

const { _t } = usei18n()

const { metricOptions, percentileOptions, errors } = defineProps<{
  metricOptions: Suggestions
  percentileOptions: Suggestions
  errors?: string[]
}>()

const metricId = useId()
const transformationId = useId()

const selectedId = defineModel<ItemId | null>('selectedId', { required: true })
const percentile = defineModel<string | null>('percentile', { required: true })
</script>

<template>
  <div class="graphing-transformation-editor">
    <div
      class="graphing-transformation-editor__label graphing-transformation-editor__label--metric"
    >
      <CmkLabel :for="metricId">{{ _t('Metric') }}</CmkLabel>
    </div>
    <div
      class="graphing-transformation-editor__label graphing-transformation-editor__label--transformation"
    >
      <CmkLabel :for="transformationId">{{ _t('Transformation') }}</CmkLabel>
      <CmkHelpText
        :help="_t('Applies a percentile transformation to the selected metric.')"
        :aria-label="_t('Help: Transformation')"
      />
    </div>
    <CmkDropdown
      v-model="selectedId"
      :component-id="metricId"
      class="graphing-transformation-editor__control--metric"
      width="fill"
      :options="metricOptions"
      :label="_t('Metric')"
      :input-hint="_t('Select one metric')"
    />
    <CmkDropdown
      v-model="percentile"
      :component-id="transformationId"
      class="graphing-transformation-editor__control--percentile"
      width="fill"
      :options="percentileOptions"
      :label="_t('Transformation')"
      :input-hint="_t('Percentile')"
    />
    <CmkInlineValidation
      v-if="errors?.length"
      class="graphing-transformation-editor__errors"
      :validation="errors"
    />
  </div>
</template>

<style scoped>
.graphing-transformation-editor {
  display: grid;
  grid-template-columns: 1fr minmax(10em, 12em);
  gap: var(--dimension-3) var(--dimension-4);
  flex: 1;
  align-items: end;
}

.graphing-transformation-editor__label {
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: var(--dimension-3);
  font-weight: var(--font-weight-bold);
}

.graphing-transformation-editor__label--metric {
  grid-column: 1;
  grid-row: 1;
}

.graphing-transformation-editor__label--transformation {
  grid-column: 2;
  grid-row: 1;
}

.graphing-transformation-editor__control--metric {
  grid-column: 1;
  grid-row: 2;
}

.graphing-transformation-editor__control--percentile {
  grid-column: 2;
  grid-row: 2;
}

.graphing-transformation-editor__errors {
  grid-column: 1 / -1;
  grid-row: 3;
}

/* CmkDropdown has no height prop; match the adjacent action-button height and re-center its label. */
/* stylelint-disable-next-line selector-pseudo-class-no-unknown, checkmk/vue-bem-naming-convention */
.graphing-transformation-editor :deep(.cmk-dropdown-button) {
  height: var(--dimension-10);
  align-items: center;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
