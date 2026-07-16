<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import type { BreadcrumbItem } from './types'

defineProps<{
  items: BreadcrumbItem[]
}>()
</script>

<template>
  <div class="cmk-breadcrumb">
    <div
      v-for="(item, index) in items"
      :key="item.link ?? index"
      :class="`cmk-breadcrumb__item${index === items.length - 1 ? '-final' : ''}`"
    >
      <a v-if="item.link" :href="item.link" class="cmk-breadcrumb__interactive-item">
        {{ item.title }}
      </a>
      <span v-else class="cmk-breadcrumb__static-item">
        {{ item.title }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.cmk-breadcrumb {
  white-space: nowrap;
  font-size: var(--font-size-normal);
}

.cmk-breadcrumb__static-item {
  color: var(--font-color-breadcrumb-inactive);
  text-decoration: none;
}

.cmk-breadcrumb__interactive-item {
  color: var(--font-color-breadcrumb-interactive);
  text-decoration: underline;
}

.cmk-breadcrumb__interactive-item:hover {
  color: var(--font-color-breadcrumb-hover);
}

.cmk-breadcrumb__item,
.cmk-breadcrumb__item-final {
  display: inline-block;
}

.cmk-breadcrumb__item::after {
  color: var(--font-color-breadcrumb-inactive);
  content: '>';
  cursor: default;
  display: inline-block;
  padding: 0 var(--spacing-half);
  text-decoration: none;
}

.cmk-breadcrumb__item-final::after {
  content: '';
}
</style>
