<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import { fromAbsolute, getLocalTimeZone } from '@internationalized/date'
import { computed } from 'vue'

import CmkTooltip, {
  CmkTooltipContent,
  CmkTooltipProvider,
  CmkTooltipTrigger
} from '@/components/CmkTooltip'

import { isoDate, isoTime, shortWeekday } from '../../../utils/timeFormat'
import type { HoverState } from '../interaction/hover'

const props = defineProps<{
  hoverState: HoverState | null
}>()

const formattedTime = computed(() => {
  if (!props.hoverState) {
    return ''
  }
  const timeZone = getLocalTimeZone()
  const zonedTime = fromAbsolute(props.hoverState.snapTime * 1000, timeZone)
  return `${shortWeekday(props.hoverState.snapTime, timeZone)}, ${isoDate(zonedTime)}  ${isoTime(zonedTime)}`
})

const anchorStyle = computed(() => ({
  left: `${props.hoverState?.cursorX ?? 0}px`,
  top: `${props.hoverState?.cursorY ?? 0}px`
}))
</script>

<template>
  <CmkTooltipProvider :delay-duration="0">
    <CmkTooltip :open="hoverState !== null">
      <CmkTooltipTrigger as-child>
        <div class="graphing-graph-tooltip__anchor" :style="anchorStyle" aria-hidden="true" />
      </CmkTooltipTrigger>
      <CmkTooltipContent
        class="graphing-graph-tooltip"
        side="right"
        align="center"
        :side-offset="16"
        :avoid-collisions="true"
        update-position-strategy="always"
        use-portal
      >
        <template v-if="hoverState">
          <div class="graphing-graph-tooltip__time">{{ formattedTime }}</div>
          <div class="graphing-graph-tooltip__rows">
            <div
              v-for="sample in hoverState.samples"
              :key="sample.metricName"
              class="graphing-graph-tooltip__row"
              :class="{ 'graphing-graph-tooltip__row--is-closest': sample.isClosest }"
            >
              <span class="graphing-graph-tooltip__swatch" :style="{ background: sample.color }" />
              <span class="graphing-graph-tooltip__label">{{ sample.label }}</span>
              <span class="graphing-graph-tooltip__value">{{ sample.formattedValue }}</span>
            </div>
          </div>
        </template>
      </CmkTooltipContent>
    </CmkTooltip>
  </CmkTooltipProvider>
</template>

<style scoped>
.graphing-graph-tooltip__anchor {
  position: absolute;
  width: 0;
  height: 0;
}

.graphing-graph-tooltip {
  z-index: var(--z-index-tooltip-offset);
  min-width: 280px;
  max-width: 420px;
  max-height: 360px;
  overflow-y: auto;
  padding: var(--spacing);
  background: var(--default-tooltip-background-color);
  border: 1px solid var(--ux-theme-6);
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgb(0 0 0 / 25%);
  font-family: Inter, Verdana, Arial, Helvetica, sans-serif;
  font-size: var(--font-size-normal);
  font-weight: var(--font-weight-default);
  line-height: normal;
  letter-spacing: 0.36px;
  color: color-mix(in srgb, var(--default-tooltip-text-color) 93%, transparent);
  pointer-events: none;
}

.graphing-graph-tooltip__time {
  margin-bottom: var(--spacing);
  padding: var(--spacing-half) 8px;
  color: var(--default-tooltip-text-color);
  font-variant-numeric: tabular-nums;
}

.graphing-graph-tooltip__rows {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.graphing-graph-tooltip__row {
  display: flex;
  align-items: center;
  gap: var(--spacing);
  padding: var(--spacing-half) 8px;
  border-radius: var(--border-radius);
}

.graphing-graph-tooltip__row--is-closest {
  background: color-mix(in srgb, var(--default-tooltip-text-color) 10%, transparent);
}

.graphing-graph-tooltip__swatch {
  flex: 0 0 auto;
  width: 4px;
  height: 16px;
  border-radius: var(--border-radius-half);
}

.graphing-graph-tooltip__label {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.graphing-graph-tooltip__value {
  flex: 0 0 auto;
  padding-left: var(--spacing);
  text-align: right;
  font-variant-numeric: tabular-nums;
}
</style>
