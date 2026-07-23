/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'

import type { ServiceState } from '@/monitoring/shared/api/types'
import ServiceStateDisplay from '@/monitoring/shared/components/ServiceStateDisplay.vue'

test.each<[ServiceState, string]>([
  ['OK', 'OK'],
  ['WARN', 'WARN'],
  ['CRIT', 'CRIT'],
  ['UNKNOWN', 'UNKN']
])('renders the short label for the %s state', (state, label) => {
  render(ServiceStateDisplay, { props: { state } })

  expect(screen.getByText(label)).toBeInTheDocument()
})

test('renders the pending label regardless of the state', () => {
  render(ServiceStateDisplay, { props: { state: 'CRIT', pending: true } })

  expect(screen.getByText('PEND')).toBeInTheDocument()
  expect(screen.queryByText('CRIT')).not.toBeInTheDocument()
})
