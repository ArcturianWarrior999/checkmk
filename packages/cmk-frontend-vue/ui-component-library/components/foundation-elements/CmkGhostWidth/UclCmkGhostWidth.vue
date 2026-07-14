<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script lang="ts">
import { type PanelConfigFor } from '@ucl/_ucl/components/detail-page'

import codeExample from './UclCmkGhostWidthCodeExample.vue?raw'

export const panelConfig = {
  variants: {
    type: 'string-array' as const,
    title: 'Variants',
    help: 'Candidate strings the content cycles through; the widest one reserves the inline size.',
    initialState: ['AM', 'PM']
  }
} satisfies PanelConfigFor<typeof CmkGhostWidth>
</script>

<script setup lang="ts">
import {
  PanelStateCreator,
  UclDetailPageAccessibility,
  UclDetailPageCodeExample,
  UclDetailPageComponent,
  UclDetailPageHeader,
  UclDetailPageLayout,
  UclPropertiesPanel
} from '@ucl/_ucl/components/detail-page'
import { computed, ref } from 'vue'

import CmkButton from '@/components/CmkButton'
import CmkGhostWidth from '@/components/CmkGhostWidth.vue'

defineProps<{ screenshotMode: boolean }>()

const propState = new PanelStateCreator<typeof CmkGhostWidth>().createRef(panelConfig)

const variantIndex = ref(0)
const currentVariant = computed(
  () => propState.value.variants[variantIndex.value % propState.value.variants.length] ?? ''
)
</script>

<template>
  <UclDetailPageLayout>
    <UclDetailPageHeader>CmkGhostWidth</UclDetailPageHeader>

    <UclDetailPageComponent>
      <div class="ucl-cmk-ghost-width">
        <p>
          The wrapper reserves the width of the widest variant, so the text after the highlighted
          value keeps its position while the value cycles:
        </p>
        <p>
          Doors open at 9:30
          <CmkGhostWidth :variants="propState.variants" class="ucl-cmk-ghost-width__value">
            <span>{{ currentVariant }}</span>
          </CmkGhostWidth>
          — sharp!
        </p>
        <CmkButton size="small" @click="variantIndex++">Show next variant</CmkButton>
      </div>

      <template #properties>
        <UclPropertiesPanel v-model="propState" :config="panelConfig" />
      </template>
    </UclDetailPageComponent>

    <UclDetailPageCodeExample :code="codeExample" />

    <UclDetailPageAccessibility :data="[]" />
  </UclDetailPageLayout>
</template>

<style scoped>
.ucl-cmk-ghost-width {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--dimension-4);

  > p {
    margin: 0;
  }
}

/* The reserved width is measured in the wrapper's font, so styling must go on the
   wrapper — never on the slotted content alone. */
.ucl-cmk-ghost-width__value {
  font-weight: var(--font-weight-bold);
}
</style>
