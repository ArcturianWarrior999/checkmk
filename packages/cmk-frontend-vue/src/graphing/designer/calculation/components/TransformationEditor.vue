<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import usei18n from '@/lib/i18n'

import CmkDropdown from '@/components/CmkDropdown'
import CmkHelpText from '@/components/CmkHelpText.vue'
import type { Suggestions } from '@/components/CmkSuggestions'
import CmkHeading from '@/components/typography/CmkHeading.vue'
import CmkInlineValidation from '@/components/user-input/CmkInlineValidation.vue'

import type { ItemId } from '../../types'

const { _t } = usei18n()

const { metricOptions, percentileOptions, errors } = defineProps<{
  metricOptions: Suggestions
  percentileOptions: Suggestions
  errors?: string[]
}>()

const selectedId = defineModel<ItemId | null>('selectedId', { required: true })
const percentile = defineModel<string | null>('percentile', { required: true })
</script>

<template>
  <div class="graphing-transformation-editor">
    <div
      class="graphing-transformation-editor__label graphing-transformation-editor__label--metric"
    >
      <CmkHeading type="h4">{{ _t('Metric') }}</CmkHeading>
    </div>
    <div
      class="graphing-transformation-editor__label graphing-transformation-editor__label--transformation"
    >
      <CmkHeading type="h4">{{ _t('Transformation') }}</CmkHeading>
      <CmkHelpText
        :help="_t('Applies a percentile transformation to the selected metric.')"
        :aria-label="_t('Help: Transformation')"
      />
    </div>
    <CmkDropdown
      v-model="selectedId"
      class="graphing-transformation-editor__control--metric"
      width="fill"
      :options="metricOptions"
      :label="_t('Metric')"
      :input-hint="_t('Select one metric')"
    />
    <CmkDropdown
      v-model="percentile"
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
  grid-template-areas:
    'metric-label transformation-label'
    'metric percentile'
    'errors errors';
  gap: var(--dimension-3) var(--dimension-4);
  flex: 1;
  align-items: end;
}

.graphing-transformation-editor__label {
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: var(--dimension-3);
}

.graphing-transformation-editor__label--metric {
  grid-area: metric-label;
}

.graphing-transformation-editor__label--transformation {
  grid-area: transformation-label;
}

.graphing-transformation-editor__control--metric {
  grid-area: metric;
}

.graphing-transformation-editor__control--percentile {
  grid-area: percentile;
}

.graphing-transformation-editor__errors {
  grid-area: errors;
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
