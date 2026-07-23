/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */

export type ChartColor =
  | 'blue'
  | 'green'
  | 'grey'
  | 'magenta'
  | 'orange'
  | 'purple'
  | 'red'
  | 'yellow'

export const CHART_COLOR_CSS: Record<ChartColor, string> = {
  blue: 'var(--color-light-blue-50)',
  green: 'var(--color-corporate-green-50)',
  grey: 'var(--color-mid-grey-50)',
  magenta: 'var(--color-pink-50)',
  orange: 'var(--color-orange-50)',
  purple: 'var(--color-purple-50)',
  red: 'var(--color-light-red-50)',
  yellow: 'var(--color-yellow-50)'
}

export function chartColorCss(color: ChartColor): string {
  return CHART_COLOR_CSS[color]
}
