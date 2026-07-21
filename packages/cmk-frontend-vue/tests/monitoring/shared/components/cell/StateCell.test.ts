/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'
import { defineComponent, h } from 'vue'

import StateCell, { type StateCellProps } from '@/monitoring/shared/components/cell/StateCell.vue'

function mountCell(props: StateCellProps) {
  return render(
    defineComponent({
      render() {
        return h('table', [h('tbody', [h('tr', [h(StateCell, props)])])])
      }
    })
  )
}

test('renders the host state by default', () => {
  mountCell({ state: 'DOWN' })

  expect(screen.getByText('DOWN')).toBeInTheDocument()
})

test('renders the service state when kind is service', () => {
  mountCell({ kind: 'service', state: 'CRIT' })

  expect(screen.getByText('CRIT')).toBeInTheDocument()
})

test('forwards the pending flag to the service state', () => {
  mountCell({ kind: 'service', state: 'CRIT', pending: true })

  expect(screen.getByText('PEND')).toBeInTheDocument()
  expect(screen.queryByText('CRIT')).not.toBeInTheDocument()
})

test('renders the stale indicator when stale', () => {
  mountCell({ kind: 'service', state: 'OK', stale: true })

  expect(screen.getByTitle('Stale state')).toBeInTheDocument()
})
