/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'
import { computed, ref } from 'vue'

import { MONITORING_SERVICE } from '@/monitoring/shared/components/MonitoringTableContext'
import MonitoringTruncationNotice from '@/monitoring/shared/components/MonitoringTruncationNotice.vue'
import type { FetchState, MonitoringService } from '@/monitoring/shared/services/MonitoringService'

function makeServiceStub({
  limit = 1000,
  matched = 2171,
  fetchState = 'idle' as FetchState,
  committedSearchQuery = '',
  activeFilterCount = 0
} = {}) {
  const limitRef = ref(limit)
  const matchedRef = ref(matched)
  return {
    limit: limitRef,
    matched: matchedRef,
    fetchState: ref(fetchState),
    resultsTruncated: computed(() => limitRef.value > 0 && matchedRef.value > limitRef.value),
    committedSearchQuery: ref(committedSearchQuery),
    filters: { activeFilterCount }
  }
}

function renderNotice(stub: ReturnType<typeof makeServiceStub>) {
  return render(MonitoringTruncationNotice, {
    global: {
      provide: { [MONITORING_SERVICE as symbol]: stub as unknown as MonitoringService<unknown> }
    }
  })
}

test('shows a single info line when the result set is capped', () => {
  renderNotice(makeServiceStub())

  expect(
    screen.getByText('Showing 1000 of 2171 hosts. Narrow your search to see the rest.')
  ).toBeInTheDocument()
})

test('says "matching hosts" when a search or filter is active', () => {
  renderNotice(makeServiceStub({ committedSearchQuery: 'web' }))

  expect(
    screen.getByText('Showing 1000 of 2171 matching hosts. Narrow your search to see the rest.')
  ).toBeInTheDocument()
})

test('is not shown when the result set is not truncated', () => {
  renderNotice(makeServiceStub({ limit: 1000, matched: 500 }))

  expect(screen.queryByRole('status')).not.toBeInTheDocument()
})

test('is not shown while a foreground fetch is in flight', () => {
  renderNotice(makeServiceStub({ fetchState: 'foreground' }))

  expect(screen.queryByRole('status')).not.toBeInTheDocument()
})

test('offers a contextual help tooltip about the pre-sort truncation', () => {
  renderNotice(makeServiceStub())

  expect(screen.getByRole('button', { name: '?' })).toBeInTheDocument()
})
