<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { ref } from 'vue'

import usei18n from '@/lib/i18n'

import CmkButton from '@/components/CmkButton'
import CmkSlideInDialog from '@/components/CmkSlideInDialog.vue'
import CmkTabs, { CmkTab, CmkTabContent } from '@/components/CmkTabs'

import type { FormulaDraft, GraphItem, ItemId } from '../types'
import RrdTab from './components/RrdTab.vue'
import type { RefVisibility } from './composables/useCalculationEditor'

const { _t } = usei18n()

const { open, items, nextId, nextColor } = defineProps<{
  open: boolean
  items: readonly GraphItem[]
  /** Id the next added item will get. */
  nextId: ItemId
  /** Default color for the next added item. */
  nextColor: string
}>()

const emit = defineEmits<{
  add: [draft: FormulaDraft, refVisibility: RefVisibility]
  update: [id: ItemId, draft: FormulaDraft, refVisibility: RefVisibility]
  delete: [id: ItemId]
  close: []
}>()

type Tab = 'rrd' | 'metric_backend'
const activeTab = ref<Tab>('rrd')

const rrdTabRef = ref<InstanceType<typeof RrdTab> | null>(null)

function onTabChange(value: string | number): void {
  if (value === 'rrd' || value === 'metric_backend') {
    activeTab.value = value
  }
}
</script>

<template>
  <CmkSlideInDialog
    :open="open"
    size="small"
    :header="{ title: _t('Calculate metrics'), closeButton: true }"
    :initial-focus-target="rrdTabRef ?? undefined"
    @close="emit('close')"
  >
    <div class="graphing-metrics-calculation-slideout">
      <div class="graphing-metrics-calculation-slideout__actions">
        <CmkButton variant="primary" @click="emit('close')">
          {{ _t('Preview in graph') }}
        </CmkButton>
      </div>
      <CmkTabs :model-value="activeTab" @update:model-value="onTabChange">
        <template #tabs>
          <CmkTab id="rrd">{{ _t('CMK RRD data') }}</CmkTab>
          <CmkTab id="metric_backend">{{ _t('Metrics backend queries') }}</CmkTab>
        </template>
        <template #tab-contents>
          <CmkTabContent id="rrd" spacing="none">
            <div class="graphing-metrics-calculation-slideout__tab">
              <RrdTab
                ref="rrdTabRef"
                :items="items"
                :next-id="nextId"
                :next-color="nextColor"
                @add="(draft, refVisibility) => emit('add', draft, refVisibility)"
                @update="(id, draft, refVisibility) => emit('update', id, draft, refVisibility)"
                @delete="emit('delete', $event)"
              />
            </div>
          </CmkTabContent>
          <CmkTabContent id="metric_backend" spacing="none">
            <div class="graphing-metrics-calculation-slideout__tab">
              <p class="graphing-metrics-calculation-slideout__placeholder">
                {{ _t('Metrics backend queries are not available yet.') }}
              </p>
            </div>
          </CmkTabContent>
        </template>
      </CmkTabs>
    </div>
  </CmkSlideInDialog>
</template>

<style scoped>
.graphing-metrics-calculation-slideout__actions {
  margin-bottom: var(--dimension-7);
}

.graphing-metrics-calculation-slideout__tab {
  padding: var(--dimension-7);
}

.graphing-metrics-calculation-slideout__placeholder {
  margin: 0;
  opacity: 0.6;
  font-style: italic;
}
</style>
