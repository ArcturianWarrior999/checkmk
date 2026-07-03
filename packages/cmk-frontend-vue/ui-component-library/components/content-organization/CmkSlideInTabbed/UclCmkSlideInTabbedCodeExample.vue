<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { ref } from 'vue'

import CmkButton from '@/components/CmkButton'
import CmkSlideInTabbed, { type SlideInTab } from '@/components/CmkSlideInTabbed'

// The page owns which components each tab renders, so the generic container
// never imports feature-specific code. Each tab loads its data lazily.
import OverviewTab from './CmkSlideInTabbedDemoTab.vue'

const isOpen = ref(false)

const tabs: SlideInTab[] = [
  {
    id: 'overview',
    title: 'Overview',
    component: OverviewTab,
    props: { label: 'Overview' },
    load: () => Promise.resolve({ loadedAt: new Date().toLocaleTimeString() })
  },
  {
    id: 'details',
    title: 'Details',
    component: OverviewTab,
    props: { label: 'Details' },
    load: () => Promise.resolve({ loadedAt: new Date().toLocaleTimeString() })
  }
]
</script>

<template>
  <CmkButton @click="isOpen = true">Open tabbed slide-in</CmkButton>

  <CmkSlideInTabbed
    :open="isOpen"
    :tabs="tabs"
    :header="{ title: 'Host overview', closeButton: true }"
    @close="isOpen = false"
  >
    <template #above-tabs>
      <p>Content placed above the tabs, e.g. a header or summary.</p>
    </template>
  </CmkSlideInTabbed>
</template>
