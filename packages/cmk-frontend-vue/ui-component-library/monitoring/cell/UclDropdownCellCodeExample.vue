<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { ref } from 'vue'

import { untranslated } from '@/lib/i18n'

import type { Suggestions } from '@/components/CmkSuggestions'

import DropdownCell from '@/monitoring/shared/components/cell/DropdownCell.vue'

const options: Suggestions = {
  type: 'fixed',
  suggestions: [
    { name: 'line', title: untranslated('Line') },
    { name: 'area', title: untranslated('Area') },
    { name: 'stack', title: untranslated('Stack') }
  ]
}

const selected = ref<string | null>('line')
</script>

<template>
  <table>
    <tbody>
      <tr>
        <DropdownCell v-model="selected" :options="options" :label="untranslated('Line style')" />
      </tr>
    </tbody>
  </table>
</template>
