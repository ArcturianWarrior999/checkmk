<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed } from 'vue'

import CmkGhostWidth from '@/components/CmkGhostWidth.vue'

import type { ItemId } from '../../types'

/** Widest uppercase glyphs in the UI fonts. */
const WIDE_GLYPHS = ['W', 'M']

const { id } = defineProps<{ id: ItemId }>()

/** Same-length ids reserve the same width: that of the widest possible id of that length. */
const ghostVariants = computed(() => WIDE_GLYPHS.map((glyph) => glyph.repeat(id.length)))
</script>

<template>
  <CmkGhostWidth class="graphing-metric-id-label" :variants="ghostVariants">
    <span class="graphing-metric-id-label__id">{{ id }}</span>
  </CmkGhostWidth>
</template>

<style scoped>
.graphing-metric-id-label {
  font-size: var(--font-size-normal);
  font-weight: var(--font-weight-bold);
  line-height: 1;
}

.graphing-metric-id-label__id {
  text-align: center;
}
</style>
