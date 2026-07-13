<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import CmkColorPicker from '@/components/CmkColorPicker.vue'

import BaseCell, { type CellVerticalAlign } from './BaseCell.vue'

defineProps<{
  columnId?: string | undefined
  verticalAlign?: CellVerticalAlign | undefined
}>()

const color = defineModel<string>({ required: true })
</script>

<template>
  <BaseCell :column-id="columnId" :vertical-align="verticalAlign">
    <CmkColorPicker v-model="color" boxed />
  </BaseCell>
</template>
