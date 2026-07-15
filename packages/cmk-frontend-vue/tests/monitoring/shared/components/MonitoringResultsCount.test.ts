/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'
import { ref } from 'vue'

import MonitoringResultsCount from '@/monitoring/shared/components/MonitoringResultsCount.vue'
import { MONITORING_SERVICE } from '@/monitoring/shared/components/MonitoringTableContext'
import type { FetchState, MonitoringService } from '@/monitoring/shared/services/MonitoringService'

function makeServiceStub(
  matched = 0,
  total = 0,
  committedSearchQuery = '',
  activeFilterCount = 0,
  { resultsTruncated = false, fetchState = 'idle' as FetchState } = {}
) {
  return {
    matched: ref(matched),
    total: ref(total),
    committedSearchQuery: ref(committedSearchQuery),
    filters: { activeFilterCount },
    resultsTruncated: ref(resultsTruncated),
    fetchState: ref(fetchState)
  }
}

function renderCount(stub: ReturnType<typeof makeServiceStub>) {
  return render(MonitoringResultsCount, {
    global: {
      provide: { [MONITORING_SERVICE as symbol]: stub as unknown as MonitoringService<unknown> }
    }
  })
}

test('shows the total row count when nothing narrows the results', () => {
  renderCount(makeServiceStub(42, 42))

  expect(screen.getByText('Total rows: 42')).toBeInTheDocument()
})

test('shows no count text when there are no matches', () => {
  renderCount(makeServiceStub(0, 0))

  expect(screen.queryByText('Total rows: 0')).not.toBeInTheDocument()
})

test('shows the criteria wording when only a search is active', () => {
  renderCount(makeServiceStub(3, 10, 'web'))

  expect(screen.getByText('Rows matching your criteria: 3 | Total rows: 10')).toBeInTheDocument()
})

test('shows the criteria wording when a filter is active', () => {
  renderCount(makeServiceStub(3, 10, '', 1))

  expect(screen.getByText('Rows matching your criteria: 3 | Total rows: 10')).toBeInTheDocument()
})

test('keeps the line in the layout so the table does not jump', () => {
  const { container } = renderCount(makeServiceStub(0, 0))

  expect(container.querySelector('.monitoring-results-count')).toBeInTheDocument()
})

test('steps aside for the truncation notice when the result set is capped', () => {
  const { container } = renderCount(makeServiceStub(4851, 4851, '', 0, { resultsTruncated: true }))

  expect(container.querySelector('.monitoring-results-count')).not.toBeInTheDocument()
})
