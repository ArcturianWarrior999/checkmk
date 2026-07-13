/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render, screen } from '@testing-library/vue'
import { defineComponent, h } from 'vue'

import CollapsibleCell from '@/monitoring/shared/components/cell/CollapsibleCell.vue'

function mountCell(
  expanded: boolean,
  onUpdate: (value: boolean) => void = () => {},
  controlsId?: string
) {
  return render(
    defineComponent({
      render() {
        return h('table', [
          h('tbody', [
            h('tr', [
              h(
                CollapsibleCell,
                { expanded, 'onUpdate:expanded': onUpdate, controlsId },
                { default: () => h('input', { 'data-testid': 'cell-content' }) }
              )
            ])
          ])
        ])
      }
    })
  )
}

test('renders the content slot next to the chevron', () => {
  mountCell(false)

  expect(screen.getByTestId('cell-content')).toBeInTheDocument()
})

test('reflects the expanded state via aria-expanded', () => {
  mountCell(true)

  expect(screen.getByRole('button', { name: 'Toggle details' })).toHaveAttribute(
    'aria-expanded',
    'true'
  )
})

test('reflects the collapsed state via aria-expanded', () => {
  mountCell(false)

  expect(screen.getByRole('button', { name: 'Toggle details' })).toHaveAttribute(
    'aria-expanded',
    'false'
  )
})

test('clicking the chevron while collapsed emits the expanded state', async () => {
  const onUpdate = vi.fn()
  mountCell(false, onUpdate)

  await fireEvent.click(screen.getByRole('button', { name: 'Toggle details' }))

  expect(onUpdate).toHaveBeenCalledWith(true)
})

test('clicking the chevron while expanded emits the collapsed state', async () => {
  const onUpdate = vi.fn()
  mountCell(true, onUpdate)

  await fireEvent.click(screen.getByRole('button', { name: 'Toggle details' }))

  expect(onUpdate).toHaveBeenCalledWith(false)
})

test('exposes the expansion content id via aria-controls', () => {
  mountCell(false, () => {}, 'expansion-a')

  expect(screen.getByRole('button', { name: 'Toggle details' })).toHaveAttribute(
    'aria-controls',
    'expansion-a'
  )
})
