<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed } from 'vue'

import { contrastTextColor } from '@/lib/contrastText'
import type { TranslatedString } from '@/lib/i18nString'

import CmkButton from '@/components/CmkButton'

import type { ItemId } from '../../types'
import ItemIdLabel from './ItemIdLabel.vue'

const { id, color, label, disabled } = defineProps<{
  id: ItemId
  color?: string | undefined
  /** Accessible name of the button. */
  label: TranslatedString
  disabled?: boolean | undefined
}>()

const emit = defineEmits<{ click: [] }>()

const chipStyle = computed(() =>
  color === undefined
    ? { backgroundColor: 'var(--color-mid-grey-50)', color: 'var(--color-conference-grey-100)' }
    : { backgroundColor: color, color: contrastTextColor(color) }
)
</script>

<template>
  <CmkButton
    variant="optional"
    class="graphing-item-id-button"
    :aria-label="label"
    :disabled="disabled"
    @click="emit('click')"
  >
    <span class="graphing-item-id-button__chip" :style="chipStyle">
      <ItemIdLabel :id="id" />
    </span>
  </CmkButton>
</template>

<style scoped>
.graphing-item-id-button {
  padding: 0 calc((var(--dimension-10) - var(--dimension-6)) / 2 - var(--dimension-1));
}

.graphing-item-id-button__chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding: var(--dimension-2);
  min-width: var(--dimension-6);
  border-radius: var(--border-radius-half);
}
</style>
