/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import CmkTrendChart from './CmkTrendChart.vue'

export default CmkTrendChart
export type { ChartColor } from '../colors'
export type {
  CmkTrendChartProps,
  TrendChartDisplayMode,
  TrendChartSeries,
  TrendChartSeriesWithColor
} from './types'
