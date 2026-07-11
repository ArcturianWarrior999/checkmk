/**
 * Copyright (C) 2026 Checkmk GmbH - License: Checkmk Enterprise License
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */

export type MetricType = 'gauge' | 'sum' | 'histogram'

export const METRIC_TYPES = ['gauge', 'sum', 'histogram'] as const

export type ConsolidationOutputType = 'float' | 'histogram'

export type ConsolidationFunction =
  | 'gauge_last'
  | 'gauge_avg'
  | 'gauge_max'
  | 'gauge_min'
  | 'sum_rate'
  | 'sum_delta'
  | 'sum_last_raw'
  | 'histogram_preserve'
  | 'histogram_count_rate'
  | 'histogram_count_delta'
  | 'histogram_sum_rate'
  | 'histogram_sum_delta'
  | 'histogram_quantile'
  | 'histogram_fraction_below'
  | 'histogram_fraction_between'
  | 'histogram_sum_raw'

export const DEFAULT_QUANTILE = 0.95

export interface ConsolidationParams {
  /** For 'histogram_quantile': the quantile in the range 0–1 (default 0.95). */
  quantile?: number
  /** For 'histogram_fraction_below': the upper threshold. */
  fractionBelowThreshold?: number
  /** For 'histogram_fraction_between': the lower threshold. */
  fractionLowerThreshold?: number
  /** For 'histogram_fraction_between': the upper threshold. */
  fractionUpperThreshold?: number
}

export interface ConsolidationModel {
  /** Effective metric type the selected function belongs to. */
  type: MetricType
  function: ConsolidationFunction
  params: ConsolidationParams
  lookbackSeconds: number
}

export interface FunctionSpec {
  fn: ConsolidationFunction
  /** Raw cumulative functions are marked "(raw)" and listed last. */
  raw: boolean
  output: ConsolidationOutputType
}

export const CONSOLIDATION_CATALOG: Record<MetricType, FunctionSpec[]> = {
  gauge: [
    { fn: 'gauge_last', raw: false, output: 'float' },
    { fn: 'gauge_avg', raw: false, output: 'float' },
    { fn: 'gauge_max', raw: false, output: 'float' },
    { fn: 'gauge_min', raw: false, output: 'float' }
  ],
  sum: [
    { fn: 'sum_rate', raw: false, output: 'float' },
    { fn: 'sum_delta', raw: false, output: 'float' },
    { fn: 'sum_last_raw', raw: true, output: 'float' }
  ],
  histogram: [
    { fn: 'histogram_preserve', raw: false, output: 'histogram' },
    { fn: 'histogram_count_delta', raw: false, output: 'float' },
    { fn: 'histogram_count_rate', raw: false, output: 'float' },
    { fn: 'histogram_sum_delta', raw: false, output: 'float' },
    { fn: 'histogram_sum_rate', raw: false, output: 'float' },
    { fn: 'histogram_quantile', raw: false, output: 'float' },
    { fn: 'histogram_fraction_below', raw: false, output: 'float' },
    { fn: 'histogram_fraction_between', raw: false, output: 'float' },
    { fn: 'histogram_sum_raw', raw: true, output: 'float' }
  ]
}

/** Allowlist restricting the offered functions per type; a missing entry offers all. */
export type AllowedFunctions = Partial<Record<MetricType, ConsolidationFunction[]>>

/**
 * Functions offered for a type, in catalog order. An allowlist filters them;
 * a filter that matches nothing falls back to the full catalog.
 */
export function functionSpecsForType(type: MetricType, allowed?: AllowedFunctions): FunctionSpec[] {
  const specs = CONSOLIDATION_CATALOG[type]
  const allowList = allowed?.[type]
  if (allowList === undefined) {
    return specs
  }
  const filtered = specs.filter((spec) => allowList.includes(spec.fn))
  return filtered.length > 0 ? filtered : specs
}

export function functionSpec(
  type: MetricType,
  fn: ConsolidationFunction
): FunctionSpec | undefined {
  return CONSOLIDATION_CATALOG[type].find((spec) => spec.fn === fn)
}

export function isFunctionValidForType(type: MetricType, fn: ConsolidationFunction): boolean {
  return functionSpec(type, fn) !== undefined
}

/** The default function for a type is the first it offers (catalog order, allowlist applied). */
export function defaultFunction(
  type: MetricType,
  allowed?: AllowedFunctions
): ConsolidationFunction {
  return functionSpecsForType(type, allowed)[0]!.fn
}

export function outputType(type: MetricType, fn: ConsolidationFunction): ConsolidationOutputType {
  return functionSpec(type, fn)?.output ?? 'float'
}
