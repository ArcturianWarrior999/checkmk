<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { computed } from 'vue'

import usei18n from '@/lib/i18n'
import type { TranslatedString } from '@/lib/i18nString'

import { type Domain, type GraphItem, type ItemId, domainOf, isFormula } from '../../types'
import ItemListSection, { type SectionAlert } from './ItemListSection.vue'

const { _t } = usei18n()

const {
  items,
  domain,
  actionLabel,
  isItemDisabled,
  alert = null
} = defineProps<{
  items: readonly GraphItem[]
  domain: Domain
  actionLabel: (id: ItemId) => TranslatedString
  isItemDisabled?: ((item: GraphItem) => boolean) | undefined
  alert?: SectionAlert | null | undefined
}>()

const emit = defineEmits<{
  insertId: [id: ItemId]
  edit: [id: ItemId]
  delete: [id: ItemId]
  dismissAlert: []
}>()

const inDomain = computed(() => items.filter((item) => domainOf(item.type) === domain))
const calculations = computed(() => inDomain.value.filter(isFormula))
const sourceMetrics = computed(() => inDomain.value.filter((item) => !isFormula(item)))
</script>

<template>
  <div class="graphing-item-list-panel">
    <ItemListSection
      :heading="_t('Calculations')"
      :empty-text="_t('No calculations yet.')"
      :items="calculations"
      :action-label="actionLabel"
      :is-item-disabled="isItemDisabled"
      :alert="alert"
      show-actions
      @insert-id="emit('insertId', $event)"
      @edit="emit('edit', $event)"
      @delete="emit('delete', $event)"
      @dismiss-alert="emit('dismissAlert')"
    />
    <ItemListSection
      :heading="_t('Source metrics')"
      :empty-text="_t('No metrics available.')"
      :items="sourceMetrics"
      :action-label="actionLabel"
      :is-item-disabled="isItemDisabled"
      @insert-id="emit('insertId', $event)"
    />
  </div>
</template>

<style scoped>
.graphing-item-list-panel {
  display: flex;
  flex-direction: column;
  gap: var(--dimension-7);
}
</style>
