<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import {
  UclDetailPageAccessibility,
  UclDetailPageCodeExample,
  UclDetailPageComponent,
  UclDetailPageHeader,
  UclDetailPageLayout
} from '@ucl/_ucl/components/detail-page'

import { SIFormatter } from '@/lib/unit-format/notationFormatter'

import CmkTrendChart from '@/network-flow/CmkTrendChart'
import type { TrendChartSeries } from '@/network-flow/CmkTrendChart'

import codeExample from './UclCmkTrendChartCodeExample.vue?raw'

defineProps<{ screenshotMode: boolean }>()

const throughput = new SIFormatter('bps', { type: 'strict', digits: 2 })
const formatValue = (value: number): string => throughput.render(value)

// Windows of per-minute throughput values, oldest first (as the compute
// endpoint delivers them). The scale here is bits per second.
function build(name: string, points: number[]): TrendChartSeries {
  return {
    name,
    dataPoints: points,
    minimum: Math.min(...points),
    maximum: Math.max(...points),
    average: points.reduce((sum, value) => sum + value, 0) / points.length,
    last: points[points.length - 1]!
  }
}

const SERIES: TrendChartSeries[] = [
  build('HTTP', [4.6e9, 5.1e9, 5.9e9, 5.4e9, 4.8e9, 5.6e9, 6.4e9, 6.0e9, 5.5e9, 6.1e9]),
  build('TLS', [2.1e9, 2.4e9, 2.0e9, 2.7e9, 3.0e9, 2.6e9, 2.3e9, 2.9e9, 3.2e9, 2.8e9]),
  build('DNS', [0.9e9, 1.1e9, 1.0e9, 1.3e9, 1.2e9, 1.0e9, 0.8e9, 1.1e9, 1.4e9, 1.2e9]),
  build('RDP', [0.4e9, 0.5e9, 0.6e9, 0.5e9, 0.4e9, 0.6e9, 0.7e9, 0.6e9, 0.5e9, 0.6e9])
]
</script>

<template>
  <UclDetailPageLayout>
    <UclDetailPageHeader>CmkTrendChart</UclDetailPageHeader>

    <UclDetailPageComponent>
      <div style="display: flex; flex-direction: column; gap: 32px">
        <!-- Stacked-area mode: cumulative bands, e.g. top applications. -->
        <div style="width: 640px; height: 320px">
          <CmkTrendChart :series="SERIES" display-mode="stacked_area" :format-value="formatValue" />
        </div>
        <!-- Line mode: one line per series, e.g. interfaces traffic. -->
        <div style="width: 640px; height: 320px">
          <CmkTrendChart :series="SERIES" display-mode="lines" :format-value="formatValue" />
        </div>
      </div>
    </UclDetailPageComponent>

    <UclDetailPageCodeExample :code="codeExample" />

    <UclDetailPageAccessibility :data="[]" />
  </UclDetailPageLayout>
</template>
