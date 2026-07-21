/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'
import { ref } from 'vue'

import MonitoringResultsCount from '@/monitoring/shared/components/MonitoringResultsCount.vue'
import { MONITORING_SERVICE } from '@/monitoring/shared/components/MonitoringTableContext'
import type { MonitoringService } from '@/monitoring/shared/services/MonitoringService'

function makeServiceStub(matched = 0, committedSearchQuery = '', activeFilterCount = 0) {
  return {
    matched: ref(matched),
    committedSearchQuery: ref(committedSearchQuery),
    filters: { activeFilterCount }
  }
}

function renderCount(stub: ReturnType<typeof makeServiceStub>) {
  return render(MonitoringResultsCount, {
    global: {
      provide: { [MONITORING_SERVICE as symbol]: stub as unknown as MonitoringService<unknown> }
    }
  })
}

test('shows the matched row count when a search is active', () => {
  renderCount(makeServiceStub(3, 'web'))

  expect(screen.getByText('Rows matching your criteria: 3')).toBeInTheDocument()
})

test('shows the matched row count when a filter is active', () => {
  renderCount(makeServiceStub(3, '', 1))

  expect(screen.getByText('Rows matching your criteria: 3')).toBeInTheDocument()
})

test('shows no criteria text when neither a search nor a filter narrows the results', () => {
  renderCount(makeServiceStub(42))

  expect(screen.queryByText(/Rows matching your criteria/)).not.toBeInTheDocument()
})

test('keeps the line in the layout so the table does not jump', () => {
  const { container } = renderCount(makeServiceStub(42))

  expect(container.querySelector('.monitoring-results-count')).toBeInTheDocument()
})

test('shows no count when the criteria match no rows', () => {
  renderCount(makeServiceStub(0, 'nope'))

  expect(screen.queryByText(/Rows matching your criteria/)).not.toBeInTheDocument()
})
