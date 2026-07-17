<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { DialogTitle } from 'reka-ui'

import usei18n from '@/lib/i18n'

import CmkButton from '@/components/CmkButton'
import CmkPopup from '@/components/CmkPopup.vue'
import CmkHeading from '@/components/typography/CmkHeading.vue'
import CmkParagraph from '@/components/typography/CmkParagraph.vue'

import { useItemDescription } from './composables/useItemDescription'
import type { GraphItem, ItemId } from './types'

const { _t } = usei18n()

const { calculationId, dependents } = defineProps<{
  open: boolean
  /** The calculation the user asked to delete. */
  calculationId: ItemId
  /** Formulas that (transitively) reference it; they are deleted along with it on confirm. */
  dependents: GraphItem[]
}>()

const emit = defineEmits<{
  /** Delete the calculation and all its dependents. */
  confirm: []
  close: []
}>()

const { describeItem } = useItemDescription()
</script>

<template>
  <CmkPopup :open="open" @close="emit('close')">
    <div class="graphing-delete-calculation-popup">
      <DialogTitle>
        <CmkHeading type="h2">
          {{ _t('Delete calculation %{id}?', { id: calculationId }) }}
        </CmkHeading>
      </DialogTitle>
      <CmkParagraph>
        {{ _t('The following calculations reference it and will be deleted as well:') }}
      </CmkParagraph>
      <ul class="graphing-delete-calculation-popup__dependents">
        <li v-for="dependent in dependents" :key="dependent.id">
          {{ dependent.id }} — {{ describeItem(dependent) }}
        </li>
      </ul>
      <div class="graphing-delete-calculation-popup__buttons">
        <CmkButton variant="danger" @click="emit('confirm')">
          {{ _t('Delete all') }}
        </CmkButton>
        <CmkButton variant="secondary" @click="emit('close')">
          {{ _t('Cancel') }}
        </CmkButton>
      </div>
    </div>
  </CmkPopup>
</template>

<style scoped>
.graphing-delete-calculation-popup {
  display: flex;
  flex-direction: column;
  gap: var(--dimension-6);
}

.graphing-delete-calculation-popup__dependents {
  margin: 0;
  padding-left: var(--dimension-8);
}

.graphing-delete-calculation-popup__buttons {
  display: flex;
  gap: var(--dimension-4);
}
</style>
