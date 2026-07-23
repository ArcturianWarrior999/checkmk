/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render, screen, waitFor } from '@testing-library/vue'

import MetricsTable from '@/graphing/designer/components/MetricsTable.vue'
import { useGraphItems } from '@/graphing/designer/composables/useGraphItems'
import type { DesignerItem } from '@/graphing/designer/drafts'

import { constantItem, formulaItem, metricBackendItem, rrdMetricItem } from '../fixtures'

const PALETTE: readonly string[] = ['#28a2f3', '#ff8400', '#ec48b6', '#ffd703']
const THRESHOLDS = { warning: '#ffd000', critical: '#ff3232' }
const TITLE_MACRO_HELP = 'Available title macros'

function renderTable(seed: DesignerItem[] = [], metricBackendAvailable = true) {
  const store = useGraphItems(PALETTE, seed)
  const utils = render(MetricsTable, {
    props: {
      store,
      thresholds: THRESHOLDS,
      metricBackendAvailable,
      titleMacroHelp: TITLE_MACRO_HELP
    }
  })
  return { store, ...utils }
}

test('adding a source appends an auto-expanded draft row', async () => {
  const { store } = renderTable([rrdMetricItem('A')])
  await fireEvent.click(screen.getByRole('combobox', { name: 'Add source' }))
  await fireEvent.click(await screen.findByRole('option', { name: 'Checkmk RRD' }))

  expect(store.items.value.map((item) => item.id)).toEqual(['A', 'B'])
  expect(store.items.value[1]).toMatchObject({ type: 'rrd_metric', host_name: null })
  // The new row opens expanded, showing its source configuration form.
  expect(await screen.findByText('Single metric')).toBeInTheDocument()
})

test('adding a constant line opens the constant form', async () => {
  const { store } = renderTable()
  await fireEvent.click(screen.getByRole('combobox', { name: 'Add source' }))
  await fireEvent.click(await screen.findByRole('option', { name: 'Constant line' }))

  expect(store.items.value[0]).toMatchObject({ type: 'constant', value: null })
  expect(await screen.findByPlaceholderText('Enter value')).toBeInTheDocument()
})

test('adding a service reference line opens the scalar form', async () => {
  const { store } = renderTable()
  await fireEvent.click(screen.getByRole('combobox', { name: 'Add source' }))
  await fireEvent.click(await screen.findByRole('option', { name: 'Service reference line' }))

  expect(store.items.value[0]).toMatchObject({
    type: 'scalar',
    scalar_type: 'warning',
    color: THRESHOLDS.warning,
    host_name: null
  })
  expect(await screen.findByRole('combobox', { name: 'Threshold type' })).toBeInTheDocument()
})

test('deleting an unreferenced row needs no confirmation', async () => {
  const { store } = renderTable([rrdMetricItem('A')])
  await fireEvent.click(screen.getByRole('button', { name: 'Delete' }))

  expect(store.items.value).toHaveLength(0)
  expect(screen.queryByText('Delete A?')).not.toBeInTheDocument()
})

test('deleting a referenced row asks and cascades to its dependents', async () => {
  const { store } = renderTable([
    rrdMetricItem('A'),
    formulaItem('B', { ast: { op: 'ref', id: 'A' } })
  ])
  const [deleteA] = screen.getAllByRole('button', { name: 'Delete' })
  await fireEvent.click(deleteA!)

  expect(await screen.findByText('Delete A?')).toBeInTheDocument()
  expect(store.items.value).toHaveLength(2)

  await fireEvent.click(screen.getByRole('button', { name: 'Delete all' }))
  expect(store.items.value).toHaveLength(0)
})

test('selecting rows reveals the bulk actions; bulk clone copies and clears the selection', async () => {
  const { store } = renderTable([rrdMetricItem('A'), constantItem('B')])
  expect(screen.queryByRole('button', { name: 'Clone selected sources' })).not.toBeInTheDocument()

  const [selectA] = screen.getAllByLabelText('Select row')
  await fireEvent.click(selectA!)

  await fireEvent.click(screen.getByRole('button', { name: 'Clone selected sources' }))
  expect(store.items.value.map((item) => item.id)).toEqual(['A', 'C', 'B'])
  expect(screen.queryByRole('button', { name: 'Clone selected sources' })).not.toBeInTheDocument()
})

test('bulk delete of a referenced row routes through the confirmation', async () => {
  const { store } = renderTable([
    rrdMetricItem('A'),
    formulaItem('B', { ast: { op: 'ref', id: 'A' } })
  ])
  const [selectA] = screen.getAllByLabelText('Select row')
  await fireEvent.click(selectA!)
  await fireEvent.click(screen.getByRole('button', { name: 'Delete selected sources' }))

  await fireEvent.click(await screen.findByRole('button', { name: 'Delete all' }))
  expect(store.items.value).toHaveLength(0)
})

test('a selected row deleted outside the table drops out of the bulk actions', async () => {
  const { store } = renderTable([rrdMetricItem('A'), constantItem('B')])
  const [selectA] = screen.getAllByLabelText('Select row')
  await fireEvent.click(selectA!)
  expect(screen.getByRole('button', { name: 'Delete selected sources' })).toBeInTheDocument()

  // E.g. deleted through the calculation slideout, which bypasses the table's own flow.
  store.remove('A')
  await waitFor(() => {
    expect(
      screen.queryByRole('button', { name: 'Delete selected sources' })
    ).not.toBeInTheDocument()
  })
})

test('title edits patch the row', async () => {
  const { store } = renderTable([rrdMetricItem('A')])
  await fireEvent.update(screen.getByLabelText('Title'), 'My title')
  expect(store.items.value[0]!.title).toBe('My title')
})

test('a formula row expands to the read-only formula form', async () => {
  renderTable([formulaItem('A', { ast: { op: 'num', value: 5 } })])
  await fireEvent.click(screen.getByRole('button', { name: 'Toggle details' }))
  expect(await screen.findByRole('button', { name: /= 5/ })).toBeInTheDocument()
})

test('a metric_backend row expands to the metric backend form', async () => {
  renderTable([metricBackendItem('A')])
  await fireEvent.click(screen.getByRole('button', { name: 'Toggle details' }))
  expect(await screen.findByText('Consolidation')).toBeInTheDocument()
})

test('the metric backend source is offered only when the feature is available', async () => {
  renderTable([], false)
  await fireEvent.click(screen.getByRole('combobox', { name: 'Add source' }))
  expect(screen.queryByRole('option', { name: 'Metrics backend' })).not.toBeInTheDocument()
})

test('adding a metric backend source opens its form', async () => {
  const { store } = renderTable([], true)
  await fireEvent.click(screen.getByRole('combobox', { name: 'Add source' }))
  await fireEvent.click(await screen.findByRole('option', { name: 'Metrics backend' }))

  expect(store.items.value[0]).toMatchObject({ type: 'metric_backend', metric_name: null })
  expect(await screen.findByText('Consolidation')).toBeInTheDocument()
})

test('the title column header exposes the macro help via a help tooltip', async () => {
  renderTable([rrdMetricItem('A')])
  await fireEvent.click(screen.getByRole('button', { name: 'Help for Title' }))
  expect(await screen.findByRole('tooltip')).toHaveTextContent(TITLE_MACRO_HELP)
})
