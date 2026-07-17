<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import type { TranslatedString } from '@/lib/i18nString'

import CmkIcon from '@/components/CmkIcon'
import type { Suggestions } from '@/components/CmkSuggestions'

import CmkDropdown from './CmkDropdown.vue'
import type { ButtonVariants } from './CmkDropdownButton.vue'

defineProps<{
  options: Suggestions
  label: TranslatedString
  width?: ButtonVariants['width']
  floating?: boolean
}>()

const emit = defineEmits<{
  (event: 'select', value: string): void
}>()

function onSelect(value: string | null): void {
  if (value !== null) {
    emit('select', value)
  }
}
</script>

<template>
  <CmkDropdown
    :model-value="null"
    :options="options"
    :label="label"
    :input-hint="label"
    :width="width"
    :floating="floating"
    @update:model-value="onSelect"
  >
    <template #button-prefix>
      <CmkIcon name="plus" variant="inline" size="small" />
    </template>
  </CmkDropdown>
</template>
