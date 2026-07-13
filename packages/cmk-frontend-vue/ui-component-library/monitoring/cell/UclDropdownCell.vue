<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script lang="ts">
import { type PanelConfig } from '@ucl/_ucl/components/detail-page'

import codeExample from './UclDropdownCellCodeExample.vue?raw'

export const panelConfig = {
  label: {
    type: 'string' as const,
    title: 'label',
    initialState: 'Line style',
    help: 'Accessible label for the dropdown, also shown as the empty-state hint.'
  },
  inputHint: {
    type: 'string' as const,
    title: 'inputHint',
    initialState: '',
    help: 'Placeholder shown while no option is selected. Defaults to empty.'
  },
  disabled: {
    type: 'boolean' as const,
    title: 'disabled',
    initialState: false,
    help: 'Disable the dropdown.'
  },
  required: {
    type: 'boolean' as const,
    title: 'required',
    initialState: false,
    help: 'Mark the dropdown as required.'
  },
  width: {
    type: 'list' as const,
    title: 'width',
    options: [
      { title: 'default', name: 'default' },
      { title: 'wide', name: 'wide' },
      { title: 'fill', name: 'fill' }
    ],
    initialState: 'fill',
    help: 'Button width strategy passed to CmkDropdown. "fill" spans the column.'
  },
  justify: {
    type: 'list' as const,
    title: 'justify',
    options: [
      { title: 'left', name: 'left' },
      { title: 'center', name: 'center' },
      { title: 'right', name: 'right' }
    ],
    initialState: 'left',
    help: 'Horizontal alignment of the cell content.'
  },
  verticalAlign: {
    type: 'list' as const,
    title: 'verticalAlign',
    options: [
      { title: 'top', name: 'top' },
      { title: 'middle', name: 'middle' }
    ],
    initialState: 'middle',
    help: 'Vertical alignment of the cell content within the row.'
  }
} satisfies PanelConfig
</script>

<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'
import {
  UclDetailPageCodeExample,
  UclDetailPageComponent,
  UclDetailPageHeader,
  UclDetailPageLayout,
  UclPropertiesPanel
} from '@ucl/_ucl/components/detail-page'
import type { InferPanelState } from '@ucl/_ucl/types/prop-panel'
import { computed, ref } from 'vue'

import { untranslated } from '@/lib/i18n'
import type { TranslatedString } from '@/lib/i18nString'

import type { Suggestions } from '@/components/CmkSuggestions'

import EditableTable from '@/monitoring/shared/components/EditableTable.vue'
import type { ColumnJustify } from '@/monitoring/shared/components/MonitoringTableContext'
import type { CellVerticalAlign } from '@/monitoring/shared/components/cell/BaseCell.vue'
import DropdownCell from '@/monitoring/shared/components/cell/DropdownCell.vue'

defineProps<{ screenshotMode: boolean }>()

const propState = ref(
  Object.fromEntries(
    Object.entries(panelConfig).map(([key, def]) => [key, def.initialState])
  ) as InferPanelState<typeof panelConfig>
)

const OPTIONS: Suggestions = {
  type: 'fixed',
  suggestions: [
    { name: 'line', title: untranslated('Line') },
    { name: 'area', title: untranslated('Area') },
    { name: 'stack', title: untranslated('Stack') }
  ]
}

const selected = ref<string | null>('line')

const label = computed<TranslatedString>(() => untranslated(propState.value.label))
const inputHint = computed<TranslatedString>(() => untranslated(propState.value.inputHint))
const width = computed<'default' | 'wide' | 'fill'>(
  () => propState.value.width as 'default' | 'wide' | 'fill'
)
const justify = computed<ColumnJustify>(() => propState.value.justify as ColumnJustify)
const verticalAlign = computed<CellVerticalAlign>(
  () => propState.value.verticalAlign as CellVerticalAlign
)

interface DemoRow {
  id: string
}

const rows = ref<DemoRow[]>([{ id: 'demo' }])

const columns = computed<ColumnDef<DemoRow>[]>(() => [
  { id: 'line-style', header: 'Line style', meta: { justify: justify.value, stretch: true } }
])
</script>

<template>
  <UclDetailPageLayout>
    <UclDetailPageHeader>DropdownCell</UclDetailPageHeader>

    <UclDetailPageComponent>
      <div class="ucl-dropdown-cell__stack">
        <div class="ucl-dropdown-cell__viewport">
          <!-- EditableTable (unlike MonitoringTable) does not clip overflow, so the
               dropdown's inline popover is free to extend past the row when open. -->
          <EditableTable :rows="rows" :columns="columns" :get-row-key="(row) => row.id">
            <template #row>
              <DropdownCell
                v-model="selected"
                column-id="line-style"
                :options="OPTIONS"
                :label="label"
                :input-hint="inputHint"
                :disabled="propState.disabled"
                :required="propState.required"
                :width="width"
                :vertical-align="verticalAlign"
              />
            </template>
          </EditableTable>
        </div>

        <p class="ucl-dropdown-cell__hint">
          Selected value: <strong>{{ selected ?? '—' }}</strong>
        </p>
      </div>

      <template #properties>
        <UclPropertiesPanel v-model="propState" :config="panelConfig" />
      </template>
    </UclDetailPageComponent>

    <UclDetailPageCodeExample :code="codeExample" />
  </UclDetailPageLayout>
</template>

<style scoped>
.ucl-dropdown-cell__stack {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--dimension-4);
  width: 100%;
  min-width: 0;
}

.ucl-dropdown-cell__viewport {
  width: 360px;
  max-width: 100%;
}

.ucl-dropdown-cell__hint {
  margin: 0;
  font-style: italic;
  opacity: 0.7;
}
</style>
