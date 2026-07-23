/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'
import { ref } from 'vue'

import { MONITORING_SERVICE } from '@/monitoring/shared/components/MonitoringTableContext'
import MonitoringTotalCount from '@/monitoring/shared/components/MonitoringTotalCount.vue'
import type { MonitoringService } from '@/monitoring/shared/services/MonitoringService'

function makeServiceStub(total = 0) {
  return { total: ref(total) }
}

function renderTotal(stub: ReturnType<typeof makeServiceStub>) {
  return render(MonitoringTotalCount, {
    global: {
      provide: { [MONITORING_SERVICE as symbol]: stub as unknown as MonitoringService<unknown> }
    }
  })
}

test('shows the total row count', () => {
  renderTotal(makeServiceStub(5151))

  expect(screen.getByText('Total rows: 5151')).toBeInTheDocument()
})

test('shows nothing when there are no rows at all', () => {
  const { container } = renderTotal(makeServiceStub(0))

  expect(container.querySelector('.monitoring-total-count')).not.toBeInTheDocument()
})
