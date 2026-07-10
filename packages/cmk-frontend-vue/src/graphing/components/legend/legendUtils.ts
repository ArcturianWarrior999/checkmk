/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { Metric } from '../TimeSeriesGraph'

export function metricsInGraphTopToBottomOrder(metrics: Metric[]): Metric[] {
  return consecutiveStackGroups(metrics).flatMap(topmostSeriesFirst)
}

function consecutiveStackGroups(metrics: Metric[]): Metric[][] {
  const groups: Metric[][] = []
  for (const metric of metrics) {
    const currentGroup = groups[groups.length - 1]
    if (currentGroup !== undefined && belongsToSameStack(currentGroup, metric)) {
      currentGroup.push(metric)
    } else {
      groups.push([metric])
    }
  }
  return groups
}

function belongsToSameStack(group: Metric[], metric: Metric): boolean {
  return metric.render.stack !== null && metric.render.stack === group[0]!.render.stack
}

function topmostSeriesFirst(group: Metric[]): Metric[] {
  const stackedSeriesDrawBottomUp = group[0]!.render.stack !== null
  return stackedSeriesDrawBottomUp ? [...group].reverse() : group
}

export function withNameToggled(hiddenNames: string[], name: string): string[] {
  if (hiddenNames.includes(name)) {
    return hiddenNames.filter((hiddenName) => hiddenName !== name)
  }
  return [...hiddenNames, name]
}
