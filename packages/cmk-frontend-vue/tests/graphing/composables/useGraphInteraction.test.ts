/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { beforeEach, describe, expect, test, vi } from 'vitest'
import { nextTick, ref } from 'vue'

import { saveGraphPin } from '@/graphing/api/graphPin'
import type { TimeRange } from '@/graphing/components/TimeSeriesGraph'
import { useGraphInteraction } from '@/graphing/composables/useGraphInteraction'

vi.mock('@/graphing/api/graphPin', () => ({
  saveGraphPin: vi.fn(() => Promise.resolve())
}))

const BASELINE: TimeRange = { start: 1000, end: 2000, step: 60 }
const ZOOMED: TimeRange = { start: 1200, end: 1500, step: 60 }

describe('useGraphInteraction', () => {
  beforeEach(() => {
    vi.mocked(saveGraphPin).mockClear()
  })

  test('starts on the baseline with time-zoom mode and no pin', () => {
    const graph = useGraphInteraction(() => BASELINE)

    expect(graph.viewTimeRange.value).toEqual(BASELINE)
    expect(graph.viewValueRange.value).toBeNull()
    expect(graph.inspectionActive.value).toBe(false)
    expect(graph.zoomMode.value).toBe('time')
    expect(graph.pinTime.value).toBeNull()
  })

  test('a zoom intent overlays the view and activates inspection', () => {
    const graph = useGraphInteraction(() => BASELINE)

    graph.onZoom({ timeRange: ZOOMED })

    expect(graph.viewTimeRange.value).toEqual(ZOOMED)
    expect(graph.inspectionActive.value).toBe(true)
  })

  test('a pan intent shifts the view', () => {
    const graph = useGraphInteraction(() => BASELINE)
    const shifted: TimeRange = { start: 1100, end: 2100, step: 60 }

    graph.onPan({ timeRange: shifted })

    expect(graph.viewTimeRange.value).toEqual(shifted)
    expect(graph.inspectionActive.value).toBe(true)
  })

  test('a reset intent restores the baseline', () => {
    const graph = useGraphInteraction(() => BASELINE)
    graph.onZoom({ timeRange: ZOOMED })

    graph.onReset()

    expect(graph.viewTimeRange.value).toEqual(BASELINE)
    expect(graph.inspectionActive.value).toBe(false)
  })

  test('a changed baseline commits and clears an active inspection', async () => {
    const baseline = ref<TimeRange>(BASELINE)
    const graph = useGraphInteraction(() => baseline.value)
    graph.onZoom({ timeRange: ZOOMED })
    const committed: TimeRange = { start: 5000, end: 6000, step: 60 }

    baseline.value = committed
    await nextTick()

    expect(graph.viewTimeRange.value).toEqual(committed)
    expect(graph.inspectionActive.value).toBe(false)
  })

  test('a baseline arriving after an initial undefined becomes the view', async () => {
    const baseline = ref<TimeRange | undefined>(undefined)
    const graph = useGraphInteraction(() => baseline.value)

    baseline.value = BASELINE
    await nextTick()

    expect(graph.viewTimeRange.value).toEqual(BASELINE)
  })

  test('creating a pin sets the pin time and persists it', () => {
    const graph = useGraphInteraction(() => BASELINE)

    graph.onPinCreate({ time: 4242 })

    expect(graph.pinTime.value).toBe(4242)
    expect(saveGraphPin).toHaveBeenCalledWith(4242)
  })

  test('clearing a pin removes it and persists the removal', () => {
    const graph = useGraphInteraction(() => BASELINE)
    graph.onPinCreate({ time: 4242 })

    graph.clearPin()

    expect(graph.pinTime.value).toBeNull()
    expect(saveGraphPin).toHaveBeenLastCalledWith(null)
  })
})
