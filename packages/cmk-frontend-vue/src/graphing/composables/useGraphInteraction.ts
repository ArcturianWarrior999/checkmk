/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { ref, watch } from 'vue'

import type { PinPayload, TimeRange, ZoomMode, ZoomPayload } from '../components/TimeSeriesGraph'
import { useGlobalPin } from './useGlobalPin'
import { useGraphView } from './useGraphView'

// Stands in for the baseline until the first data fetch delivers one; hosts gate
// their renderer on their own timeRange, so this view is never rendered.
const EMPTY_TIME_RANGE: TimeRange = { start: 0, end: 0, step: 1 }

// The per-graph interaction owner: the renderer is view-only (emit-and-wait) and this
// composable holds everything that moves it — the view state machine, the zoom mode,
// and the pin — plus the handlers that route the renderer's intents into the machine.
export function useGraphInteraction(
  getBaseline: () => TimeRange | undefined,
  getShowPin: () => boolean = () => false
) {
  const {
    timeRange: viewTimeRange,
    valueRange: viewValueRange,
    inspectionActive,
    handleIntent
  } = useGraphView(() => getBaseline() ?? EMPTY_TIME_RANGE)

  const zoomMode = ref<ZoomMode>('time')

  const { pinTime, ensurePinLoaded, setPin, clearPin } = useGlobalPin()

  watch(
    getShowPin,
    (showPin) => {
      if (showPin) {
        ensurePinLoaded()
      }
    },
    { immediate: true }
  )

  watch(getBaseline, (baseline) => {
    if (baseline !== undefined) {
      handleIntent({ kind: 'rangeCommit', timeRange: baseline })
    }
  })

  function onZoom(payload: ZoomPayload): void {
    handleIntent({ kind: 'zoomTransient', ...payload })
  }

  function onPan(payload: { timeRange: TimeRange }): void {
    handleIntent({ kind: 'pan', timeRange: payload.timeRange })
  }

  function onReset(): void {
    handleIntent({ kind: 'reset' })
  }

  function onPinCreate(payload: PinPayload): void {
    setPin(payload.time)
  }

  return {
    viewTimeRange,
    viewValueRange,
    inspectionActive,
    zoomMode,
    pinTime,
    onZoom,
    onPan,
    onReset,
    onPinCreate,
    clearPin
  }
}
