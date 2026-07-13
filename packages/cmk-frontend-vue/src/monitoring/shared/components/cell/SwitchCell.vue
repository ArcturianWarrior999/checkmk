<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import CmkSwitch from '@/components/CmkSwitch.vue'

import BaseCell, { type CellVerticalAlign } from './BaseCell.vue'

defineProps<{
  columnId?: string | undefined
  verticalAlign?: CellVerticalAlign | undefined
}>()

const value = defineModel<boolean>({ required: false, default: false })
</script>

<template>
  <BaseCell class="monitoring-switch-cell" :column-id="columnId" :vertical-align="verticalAlign">
    <CmkSwitch v-model="value" />
  </BaseCell>
</template>
