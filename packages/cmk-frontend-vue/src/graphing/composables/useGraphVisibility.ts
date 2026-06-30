/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { computed, ref } from 'vue'

import type { ConsolidationFn, HorizontalLine, Metric } from '../components/TimeSeriesGraph'

export function useGraphVisibility(
  getMetrics: () => Metric[],
  getHorizontalLines: () => HorizontalLine[],
  defaultConsolidationFunction: ConsolidationFn = 'max'
) {
  const hiddenMetricNames = ref<string[]>([])
  const hiddenLineNames = ref<string[]>([])
  const highlightedMetricName = ref<string | null>(null)
  const activeConsolidationFunction = ref<ConsolidationFn>(defaultConsolidationFunction)

  const visibleMetrics = computed(() =>
    getMetrics().filter((m) => !hiddenMetricNames.value.includes(m.metadata.name))
  )

  const visibleHorizontalLines = computed(() =>
    getHorizontalLines().filter((l) => !hiddenLineNames.value.includes(l.name))
  )

  function setConsolidationFunction(val: ConsolidationFn) {
    activeConsolidationFunction.value = val
  }

  return {
    hiddenMetricNames,
    hiddenLineNames,
    highlightedMetricName,
    activeConsolidationFunction,
    visibleMetrics,
    visibleHorizontalLines,
    setConsolidationFunction
  }
}
