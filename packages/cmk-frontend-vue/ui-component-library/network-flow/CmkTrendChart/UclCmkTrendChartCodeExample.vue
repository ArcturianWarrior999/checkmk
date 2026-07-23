<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { SIFormatter } from '@/lib/unit-format/notationFormatter'

import CmkTrendChart from '@/network-flow/CmkTrendChart'

const throughput = new SIFormatter('bps', { type: 'strict', digits: 2 })

const series = [
  {
    name: 'HTTP',
    dataPoints: [62, 68, 75, 71, 66],
    minimum: 62,
    maximum: 75,
    average: 68.4,
    last: 66
  },
  {
    name: 'TLS',
    dataPoints: [30, 34, 31, 38, 40],
    minimum: 30,
    maximum: 40,
    average: 34.6,
    last: 40
  }
]
</script>

<template>
  <CmkTrendChart
    :series="series"
    display-mode="stacked_area"
    :format-value="(value: number) => throughput.render(value)"
  />
</template>
