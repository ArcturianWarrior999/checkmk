<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { markRaw, ref } from 'vue'

import CmkButton from '@/components/CmkButton'
import CmkSlideInTabbed, { type SlideInTab } from '@/components/CmkSlideInTabbed'

import CmkSlideInTabbedDemoTab from './CmkSlideInTabbedDemoTab.vue'

defineProps<{ screenshotMode: boolean }>()

const demoTab = markRaw(CmkSlideInTabbedDemoTab)
const isOpen = ref(false)

const tabs: SlideInTab[] = [
  {
    id: 'overview',
    title: 'Overview',
    component: demoTab,
    props: { label: 'Overview' },
    load: () => Promise.resolve({ loadedAt: new Date().toLocaleTimeString() })
  },
  {
    id: 'details',
    title: 'Details',
    component: demoTab,
    props: { label: 'Details' },
    load: () => Promise.reject(new Error('Simulated load failure'))
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
  />
</template>
