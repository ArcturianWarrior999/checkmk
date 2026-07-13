/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render, screen } from '@testing-library/vue'
import { defineComponent, h } from 'vue'

import VisibilityCell from '@/monitoring/shared/components/cell/VisibilityCell.vue'

function mountCell(visible: boolean, onUpdate: (value: boolean) => void = () => {}) {
  return render(
    defineComponent({
      render() {
        return h('table', [
          h('tbody', [
            h('tr', [h(VisibilityCell, { modelValue: visible, 'onUpdate:modelValue': onUpdate })])
          ])
        ])
      }
    })
  )
}

test('reflects the visible state via aria-pressed', () => {
  mountCell(true)

  expect(screen.getByRole('button', { name: 'Toggle visibility' })).toHaveAttribute(
    'aria-pressed',
    'true'
  )
})

test('clicking the toggle emits the inverted value', async () => {
  const onUpdate = vi.fn()
  mountCell(true, onUpdate)

  await fireEvent.click(screen.getByRole('button', { name: 'Toggle visibility' }))

  expect(onUpdate).toHaveBeenCalledWith(false)
})

test('clicking the toggle on a hidden row emits true', async () => {
  const onUpdate = vi.fn()
  mountCell(false, onUpdate)

  await fireEvent.click(screen.getByRole('button', { name: 'Toggle visibility' }))

  expect(onUpdate).toHaveBeenCalledWith(true)
})
