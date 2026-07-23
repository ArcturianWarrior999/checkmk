<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import type { TranslatedString } from '@/lib/i18nString'

import { CmkAddDropdown } from '@/components/CmkDropdown'
import CmkLabel from '@/components/CmkLabel.vue'
import type { Suggestions } from '@/components/CmkSuggestions'
import {
  CmkFilterInputItem,
  CmkRemoveFilterButton,
  type ConfiguredValues,
  type FilterDefinitions
} from '@/components/filter'

defineProps<{
  title: TranslatedString
  addLabel: TranslatedString
  activeFilterIds: string[]
  getFilterValues: (filterId: string) => ConfiguredValues | null
  addSuggestions: Suggestions
  filterDefinitions: FilterDefinitions
}>()

defineEmits<{
  'add-filter': [filterId: string]
  'update-filter': [filterId: string, values: ConfiguredValues]
  'remove-filter': [filterId: string]
}>()
</script>

<template>
  <div class="graphing-filter-query-section">
    <CmkLabel variant="subtitle">{{ title }}</CmkLabel>
    <div class="graphing-filter-query-section__container">
      <div
        v-for="filterId in activeFilterIds"
        :key="filterId"
        class="graphing-filter-query-section__filter"
      >
        <CmkFilterInputItem
          class="graphing-filter-query-section__filter-input"
          :filter-id="filterId"
          :configured-filter-values="getFilterValues(filterId)"
          @update-filter-values="(id, values) => $emit('update-filter', id, values)"
        />
        <CmkRemoveFilterButton
          :filter-name="filterDefinitions[filterId]?.title ?? ''"
          @remove="$emit('remove-filter', filterId)"
        />
      </div>
      <div class="graphing-filter-query-section__add">
        <CmkAddDropdown
          width="fill"
          floating
          :options="addSuggestions"
          :label="addLabel"
          @select="(id) => $emit('add-filter', id)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.graphing-filter-query-section {
  display: flex;
  flex-direction: column;
  gap: var(--dimension-3);

  --graphing-filter-query-section-border: var(--color-mid-grey-10);
}

body[data-theme='modern-dark'] .graphing-filter-query-section {
  --graphing-filter-query-section-border: var(--color-mid-grey-90);
}

.graphing-filter-query-section__container {
  overflow: hidden;
  border: 1px solid var(--graphing-filter-query-section-border);
  border-radius: var(--border-radius);
}

.graphing-filter-query-section__filter {
  display: flex;
  align-items: flex-start;
  gap: var(--dimension-4);
  padding: var(--dimension-7);
  border-bottom: 1px solid var(--graphing-filter-query-section-border);
}

.graphing-filter-query-section__filter-input {
  flex: 1;
  min-width: 0;
}

.graphing-filter-query-section__add {
  padding: var(--dimension-5);
}
</style>
