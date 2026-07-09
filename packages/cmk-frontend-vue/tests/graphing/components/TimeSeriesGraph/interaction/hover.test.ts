/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { describe, expect, test } from 'vitest'

import { metricHitDistance } from '@/graphing/components/TimeSeriesGraph/interaction/hover'

describe('metricHitDistance', () => {
  test('line: distance is measured to the drawn edge, ignoring the lower edge', () => {
    expect(metricHitDistance(100, 80, 0, false)).toBe(20)
    expect(metricHitDistance(60, 80, 0, false)).toBe(20)
    expect(metricHitDistance(80, 80, 999, false)).toBe(0)
  })

  test('filled: cursor inside the band is a zero distance', () => {
    expect(metricHitDistance(50, 40, 80, true)).toBe(0)
    expect(metricHitDistance(40, 40, 80, true)).toBe(0)
    expect(metricHitDistance(80, 40, 80, true)).toBe(0)
  })

  test('filled: cursor outside the band measures to the nearer edge', () => {
    expect(metricHitDistance(30, 40, 80, true)).toBe(10)
    expect(metricHitDistance(95, 40, 80, true)).toBe(15)
  })

  test('filled: edges may arrive in either order (inverse metric mirrored below zero)', () => {
    expect(metricHitDistance(60, 80, 40, true)).toBe(0)
    expect(metricHitDistance(30, 80, 40, true)).toBe(10)
    expect(metricHitDistance(95, 80, 40, true)).toBe(15)
  })
})
