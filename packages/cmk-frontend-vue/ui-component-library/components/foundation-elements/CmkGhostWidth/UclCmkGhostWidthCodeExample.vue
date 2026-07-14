<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { ref } from 'vue'

import CmkGhostWidth from '@/components/CmkGhostWidth.vue'

const meridiem = ref<'AM' | 'PM'>('AM')
</script>

<template>
  <!-- The widest variant reserves the width, so toggling AM/PM never shifts the layout. -->
  9:30
  <CmkGhostWidth :variants="['AM', 'PM']">
    <span>{{ meridiem }}</span>
  </CmkGhostWidth>
</template>
