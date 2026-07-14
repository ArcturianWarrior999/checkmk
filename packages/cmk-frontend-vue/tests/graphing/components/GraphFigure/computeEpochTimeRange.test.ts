/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { computeEpochTimeRange } from '@/graphing/components/GraphFigure/computeEpochTimeRange'

// Wednesday 2026-07-08 14:30:00 local time
const NOW = new Date(2026, 6, 8, 14, 30, 0)
const NOW_SECONDS = Math.floor(NOW.getTime() / 1000)

const localEpoch = (...args: [number, number, number, number?, number?, number?]): number =>
  Math.floor(new Date(...args).getTime() / 1000)

describe('computeEpochTimeRange', () => {
  it('computes trailing windows from a graph duration', () => {
    expect(computeEpochTimeRange({ type: 'graph', duration: 3600 }, NOW)).toEqual({
      start: NOW_SECONDS - 3600,
      end: NOW_SECONDS
    })
  })

  it('computes trailing windows from an age', () => {
    expect(computeEpochTimeRange({ type: 'age', days: 1, hours: 2, minutes: 3 }, NOW)).toEqual({
      start: NOW_SECONDS - (86400 + 2 * 3600 + 3 * 60),
      end: NOW_SECONDS
    })
  })

  it('includes the end day of a fixed date range', () => {
    expect(
      computeEpochTimeRange({ type: 'date', start: '2026-07-01', end: '2026-07-02' }, NOW)
    ).toEqual({
      start: localEpoch(2026, 6, 1),
      end: localEpoch(2026, 6, 3)
    })
  })

  it.each([
    ['last_4_hours', NOW_SECONDS - 4 * 3600, NOW_SECONDS],
    ['last_25_hours', NOW_SECONDS - 25 * 3600, NOW_SECONDS],
    ['today', localEpoch(2026, 6, 8), NOW_SECONDS],
    ['yesterday', localEpoch(2026, 6, 7), localEpoch(2026, 6, 8)],
    ['7_days_ago', localEpoch(2026, 6, 1), localEpoch(2026, 6, 2)],
    // 2026-07-08 is a Wednesday; the week starts on Monday 2026-07-06
    ['this_week', localEpoch(2026, 6, 6), NOW_SECONDS],
    ['last_week', localEpoch(2026, 5, 29), localEpoch(2026, 6, 6)],
    ['this_month', localEpoch(2026, 6, 1), NOW_SECONDS],
    ['last_month', localEpoch(2026, 5, 1), localEpoch(2026, 6, 1)],
    ['this_year', localEpoch(2026, 0, 1), NOW_SECONDS],
    ['last_year', localEpoch(2025, 0, 1), localEpoch(2026, 0, 1)]
  ] as const)('computes the predefined range %s', (value, start, end) => {
    expect(computeEpochTimeRange({ type: 'predefined', value }, NOW)).toEqual({ start, end })
  })
})
