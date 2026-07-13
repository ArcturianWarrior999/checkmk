/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { type ComputedRef, computed, ref, watch } from 'vue'

const DEFAULT_INTERVAL_SECONDS = 30

const intervalSecondsState = ref(DEFAULT_INTERVAL_SECONDS)
const pausedState = ref(true)
const tickState = ref(0)

const refreshIntervalSeconds = computed(() => intervalSecondsState.value)
const refreshPaused = computed(() => pausedState.value)
const refreshTick = computed(() => tickState.value)

function setRefreshIntervalSeconds(seconds: number): void {
  intervalSecondsState.value = seconds
}

function setRefreshPaused(paused: boolean): void {
  pausedState.value = paused
}

function fireRefresh(): void {
  tickState.value += 1
}

let timerId: ReturnType<typeof setInterval> | null = null

watch(
  [intervalSecondsState, pausedState],
  ([intervalSeconds, paused], [, previouslyPaused]) => {
    if (timerId !== null) {
      clearInterval(timerId)
      timerId = null
    }
    if (paused) {
      return
    }
    if (previouslyPaused) {
      fireRefresh()
    }
    timerId = setInterval(fireRefresh, intervalSeconds * 1000)
  },
  { flush: 'sync' }
)

export interface GlobalRefresh {
  refreshIntervalSeconds: ComputedRef<number>
  refreshPaused: ComputedRef<boolean>
  refreshTick: ComputedRef<number>
  setRefreshIntervalSeconds: (seconds: number) => void
  setRefreshPaused: (paused: boolean) => void
}

export function useGlobalRefresh(): GlobalRefresh {
  return {
    refreshIntervalSeconds,
    refreshPaused,
    refreshTick,
    setRefreshIntervalSeconds,
    setRefreshPaused
  }
}
