/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type {
  ConsolidationFn,
  HorizontalLine,
  Metric,
  TimeRange
} from './components/TimeSeriesGraph'

export type { ConsolidationFn, HorizontalLine, Metric, TimeRange }

// What the user has chosen (drives GraphDateTimeRangePicker).
// Distinct from TimeRange, which is what the RRD actually returned.
export interface RequestedTimeRange {
  start: number // unix seconds
  end: number // unix seconds
}

interface BurgerMenuAction {
  label: string
  onClick: () => void
}

export interface BurgerMenuGroup {
  heading: string
  actions: BurgerMenuAction[]
}

// Props shared by GraphFigure and (via extension) GraphPanel.
export interface GraphFigureProps {
  metrics: Metric[]
  // Absent until the first data fetch completes. Explicit undefined is accepted
  // so that parent components can forward their own optional timeRange prop directly.
  timeRange?: TimeRange | undefined
  interactive?: boolean
  title?: string
  showTitle?: boolean
  showTimestamp?: boolean
  horizontalLines?: HorizontalLine[]
  canvasWidth?: number
  canvasHeight?: number
}

// GraphPanel adds the optional footer zone (legend, time ranges) and the
// export/action burger menu.
export interface GraphPanelProps extends GraphFigureProps {
  requestedTimeRange: RequestedTimeRange
  burgerMenuGroups?: BurgerMenuGroup[]
  showBurgerMenu?: boolean
  showLegend?: boolean
  legendPosition?: 'bottom' | 'right'
  // TODO: add property showPanningBrush?: boolean; or similar
}

export type GraphPanelEmits = {
  'update:requestedTimeRange': [value: RequestedTimeRange]
  'update:consolidationFn': [value: ConsolidationFn]
}
