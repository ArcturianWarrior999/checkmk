<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import CmkMultitoneIcon from '@/components/CmkIcon/CmkMultitoneIcon.vue'

defineProps<{
  hidden: boolean
  ariaLabel?: string | undefined
}>()

defineEmits<{
  toggle: []
}>()
</script>

<template>
  <button
    type="button"
    class="graphing-graph-legend-eye-button"
    :aria-pressed="!hidden"
    :aria-label="ariaLabel"
    @click="$emit('toggle')"
  >
    <CmkMultitoneIcon
      :name="hidden ? 'eye-crossed-out' : 'eye'"
      primary-color="font"
      size="small"
    />
  </button>
</template>

<style scoped lang="scss">
.graphing-graph-legend-eye-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: inherit;
  border-radius: var(--border-radius);

  &:hover {
    background: rgb(0 0 0 / 8%);
  }
}
</style>
