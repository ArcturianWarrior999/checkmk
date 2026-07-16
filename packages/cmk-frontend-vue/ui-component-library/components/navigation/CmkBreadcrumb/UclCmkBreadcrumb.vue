<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script lang="ts">
import codeExample from './UclCmkBreadcrumbCodeExample.vue?raw'
</script>

<script setup lang="ts">
import {
  UclDetailPageAccessibility,
  UclDetailPageCodeExample,
  UclDetailPageComponent,
  UclDetailPageHeader,
  UclDetailPageLayout
} from '@ucl/_ucl/components/detail-page'

import CmkBreadcrumb from '@/components/CmkBreadcrumb'

defineProps<{ screenshotMode: boolean }>()
</script>

<template>
  <UclDetailPageLayout>
    <UclDetailPageHeader>CmkBreadcrumb</UclDetailPageHeader>

    <UclDetailPageComponent>
      <CmkBreadcrumb
        :items="[
          { title: 'Monitor', link: null },
          { title: 'Other', link: null },
          { title: 'Linked', link: '#' },
          { title: 'Fixed again', link: null }
        ]"
      />
    </UclDetailPageComponent>

    <UclDetailPageCodeExample :code="codeExample" />

    <UclDetailPageAccessibility :data="[]" />
  </UclDetailPageLayout>
</template>
