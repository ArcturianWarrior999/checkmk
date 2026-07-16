<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import CmkBreadcrumb from '@/components/CmkBreadcrumb'
</script>

<template>
  <CmkBreadcrumb
    :items="[
      { title: 'Monitor', link: null },
      { title: 'Other', link: null },
      { title: 'Linked', link: '#' },
      { title: 'Fixed again', link: null }
    ]"
  />
</template>
