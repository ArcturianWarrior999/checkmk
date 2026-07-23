/**
 * Copyright (C) 2026 Checkmk GmbH - License: Checkmk Enterprise License
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { ConsolidationFunction as WireConsolidationFunction } from 'cmk-shared-typing/typescript/graph_designer'

import { staticAssertNever } from '@/lib/typeUtils'

import type { ConsolidationFunction } from '@/metric-backend/consolidation/types'

export const DEFAULT_HISTOGRAM_PERCENTILE = 90

export function consolidationFunctionFromWire(
  wire: WireConsolidationFunction
): ConsolidationFunction {
  switch (wire.type) {
    case 'gauge':
      return { type: 'gauge', function: wire.function }
    case 'sum':
      return { type: 'sum', function: wire.function }
    case 'histogram':
      return { type: 'histogram', function: wire.function }
    default:
      staticAssertNever(wire)
      throw new Error(`unhandled consolidation type: ${JSON.stringify(wire)}`)
  }
}

export function buildConsolidationFunction(
  consolidationFunction: ConsolidationFunction | null,
  lookbackSeconds: number,
  percentile: number
): WireConsolidationFunction {
  switch (consolidationFunction?.function) {
    case 'gauge_max':
      return { type: 'gauge', function: 'gauge_max', lookback_seconds: lookbackSeconds }
    case 'gauge_avg':
      return { type: 'gauge', function: 'gauge_avg', lookback_seconds: lookbackSeconds }
    case 'gauge_min':
      return { type: 'gauge', function: 'gauge_min', lookback_seconds: lookbackSeconds }
    case 'sum_rate':
      return { type: 'sum', function: 'sum_rate', lookback_seconds: lookbackSeconds }
    case 'sum_last_raw':
      return { type: 'sum', function: 'sum_last_raw', lookback_seconds: lookbackSeconds }
    case 'sum_delta':
      return { type: 'sum', function: 'sum_delta', lookback_seconds: lookbackSeconds }
    case 'histogram_quantile':
      return {
        type: 'histogram',
        function: 'histogram_quantile',
        lookback_seconds: lookbackSeconds,
        percentile
      }
    case 'histogram_count_delta':
      return {
        type: 'histogram',
        function: 'histogram_count_delta',
        lookback_seconds: lookbackSeconds,
        percentile: 0
      }
    case 'histogram_count_rate':
      return {
        type: 'histogram',
        function: 'histogram_count_rate',
        lookback_seconds: lookbackSeconds,
        percentile: 0
      }
    case 'gauge_last':
    default:
      return { type: 'gauge', function: 'gauge_last', lookback_seconds: lookbackSeconds }
  }
}
