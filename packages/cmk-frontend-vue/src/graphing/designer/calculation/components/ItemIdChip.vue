<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed } from 'vue'

import { contrastTextColor } from '@/lib/contrastText'

import type { ItemId } from '../../types'
import ItemIdLabel from './ItemIdLabel.vue'

const { id, color } = defineProps<{
  id: ItemId
  color?: string | undefined
}>()

const chipStyle = computed(() =>
  color === undefined
    ? { backgroundColor: 'var(--color-mid-grey-50)', color: 'var(--color-conference-grey-100)' }
    : { backgroundColor: color, color: contrastTextColor(color) }
)
</script>

<template>
  <span class="graphing-item-id-chip" :style="chipStyle">
    <ItemIdLabel :id="id" />
  </span>
</template>

<style scoped>
.graphing-item-id-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding: var(--dimension-2);
  min-width: var(--dimension-6);
  border-radius: var(--border-radius-half);
}
</style>
