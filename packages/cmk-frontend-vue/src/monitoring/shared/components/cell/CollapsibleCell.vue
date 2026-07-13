<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import usei18n from '@/lib/i18n'

import CmkMultitoneIcon from '@/components/CmkIcon/CmkMultitoneIcon.vue'

import BaseCell, { type CellVerticalAlign } from './BaseCell.vue'

const { _t } = usei18n()

defineProps<{
  columnId?: string | undefined
  controlsId?: string | undefined
  verticalAlign?: CellVerticalAlign | undefined
}>()

const expanded = defineModel<boolean>('expanded', { required: false, default: false })
</script>

<template>
  <BaseCell
    class="monitoring-collapsible-cell"
    :column-id="columnId"
    :vertical-align="verticalAlign"
  >
    <div class="monitoring-collapsible-cell__layout">
      <button
        type="button"
        class="monitoring-collapsible-cell__toggle"
        :aria-expanded="expanded"
        :aria-controls="controlsId"
        :aria-label="_t('Toggle details')"
        @click="expanded = !expanded"
      >
        <CmkMultitoneIcon
          :name="expanded ? 'chevron-down' : 'chevron-right'"
          primary-color="font"
          size="small"
          aria-hidden="true"
        />
      </button>
      <div class="monitoring-collapsible-cell__content">
        <slot />
      </div>
    </div>
  </BaseCell>
</template>

<style scoped>
.monitoring-collapsible-cell__layout {
  display: flex;
  align-items: center;
  gap: var(--dimension-3);
}

.monitoring-collapsible-cell__toggle {
  margin: 0;
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
  display: inline-flex;
  flex: 0 0 auto;

  &:focus-visible {
    outline: revert;
  }
}

.monitoring-collapsible-cell__content {
  flex: 1 1 auto;
  min-width: 0;
}
</style>
