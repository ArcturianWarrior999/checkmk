<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { untranslated } from '@/lib/i18n'
import type { TranslatedString } from '@/lib/i18nString'

import CmkDropdown from '@/components/CmkDropdown'
import type { Suggestions } from '@/components/CmkSuggestions'

import BaseCell, { type CellVerticalAlign } from './BaseCell.vue'

const { width = 'fill', inputHint = untranslated('') } = defineProps<{
  columnId?: string | undefined
  options: Suggestions
  label: TranslatedString
  inputHint?: TranslatedString
  disabled?: boolean
  required?: boolean
  width?: 'default' | 'wide' | 'fill'
  verticalAlign?: CellVerticalAlign | undefined
}>()

const selected = defineModel<string | null>({ required: false, default: null })
</script>

<template>
  <BaseCell class="monitoring-dropdown-cell" :column-id="columnId" :vertical-align="verticalAlign">
    <CmkDropdown
      v-model="selected"
      floating
      :options="options"
      :label="label"
      :input-hint="inputHint"
      :disabled="disabled"
      :required="required"
      :width="width"
    />
  </BaseCell>
</template>

<style scoped>
/* The fill width carries a global 10em min-width that would overflow
   columns narrower than that; the cell must win. */
/* stylelint-disable-next-line selector-pseudo-class-no-unknown, checkmk/vue-bem-naming-convention */
.monitoring-dropdown-cell :deep(.cmk-dropdown-button--width-fill) {
  min-width: 0;
}
</style>
