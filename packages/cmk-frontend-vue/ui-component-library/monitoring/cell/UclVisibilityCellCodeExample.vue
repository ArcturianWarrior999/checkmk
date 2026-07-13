<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { ref } from 'vue'

import VisibilityCell from '@/monitoring/shared/components/cell/VisibilityCell.vue'

const visible = ref(true)
</script>

<template>
  <table>
    <tbody>
      <tr>
        <VisibilityCell v-model="visible" />
      </tr>
    </tbody>
  </table>
</template>
