/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fromDate, getLocalTimeZone } from '@internationalized/date'
import { type Ref, ref, watch } from 'vue'

import type { DateTimeRange } from '@/components/date-time'

import { useGlobalTimeRange } from '../GlobalTimePicker/useGlobalTimeRange'
import type { RequestedTimeRange } from '../types'

function toRequestedTimeRange(range: DateTimeRange): RequestedTimeRange {
  return {
    start: Math.floor(range.from.toDate().getTime() / 1000),
    end: Math.floor(range.to.toDate().getTime() / 1000)
  }
}

// The reverse of toRequestedTimeRange. A RequestedTimeRange has no timezone of its own
// (it's plain unix seconds), so the currently active range's zone is reused for round-
// tripping; falls back to the browser zone if the picker hasn't published one yet.
function toDateTimeRange(range: RequestedTimeRange, timeZone: string): DateTimeRange {
  return {
    from: fromDate(new Date(range.start * 1000), timeZone),
    to: fromDate(new Date(range.end * 1000), timeZone)
  }
}

const DEFAULT_RANGE_SECONDS = 4 * 3600

/**
 * The requested (user-chosen) time range for a graph data fetch owner.
 *
 * Seeded from the page's global time picker if one has already published a range,
 * otherwise from `initial` (default: the last four hours); follows every subsequent
 * picker change. The returned ref stays writable: local interactions (e.g. brush zoom)
 * can update it directly, and doing so publishes the new range to the global picker in
 * turn, which every other graph/graph-group on the page follows the same way.
 *
 * Call this from the component that owns the data fetch (e.g. a graph group or a
 * standalone panel host), not from presentational components like GraphPanel.
 */
export function useRequestedTimeRange(initial?: RequestedTimeRange): Ref<RequestedTimeRange> {
  const { activeTimeRange, setActiveTimeRange } = useGlobalTimeRange()

  function fallbackRange(): RequestedTimeRange {
    const now = Math.floor(Date.now() / 1000)
    return { start: now - DEFAULT_RANGE_SECONDS, end: now }
  }

  const requestedTimeRange = ref<RequestedTimeRange>(
    activeTimeRange.value === null
      ? initial === undefined
        ? fallbackRange()
        : { ...initial }
      : toRequestedTimeRange(activeTimeRange.value)
  )
  // Mount order of the picker and the fetch owner is DOM-driven: if the picker mounts
  // later, its initial publish arrives through this watch and replaces the seed.
  watch(activeTimeRange, (val) => {
    if (val === null) {
      return
    }
    const next = toRequestedTimeRange(val)
    if (
      next.start === requestedTimeRange.value.start &&
      next.end === requestedTimeRange.value.end
    ) {
      return
    }
    requestedTimeRange.value = next
  })

  watch(requestedTimeRange, (val) => {
    if (activeTimeRange.value !== null) {
      const current = toRequestedTimeRange(activeTimeRange.value)
      if (val.start === current.start && val.end === current.end) {
        return
      }
    }
    const timeZone = activeTimeRange.value?.from.timeZone ?? getLocalTimeZone()
    setActiveTimeRange(toDateTimeRange(val, timeZone))
  })

  return requestedTimeRange
}
