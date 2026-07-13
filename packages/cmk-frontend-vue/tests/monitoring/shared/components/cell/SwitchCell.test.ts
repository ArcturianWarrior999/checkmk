/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render, screen } from '@testing-library/vue'
import { defineComponent, h } from 'vue'

import SwitchCell from '@/monitoring/shared/components/cell/SwitchCell.vue'

function mountCell(value: boolean, onUpdate: (value: boolean) => void = () => {}) {
  return render(
    defineComponent({
      render() {
        return h('table', [
          h('tbody', [
            h('tr', [h(SwitchCell, { modelValue: value, 'onUpdate:modelValue': onUpdate })])
          ])
        ])
      }
    })
  )
}

test('renders the switch in the checked state', () => {
  mountCell(true)

  expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'true')
})

test('renders the switch in the unchecked state', () => {
  mountCell(false)

  expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'false')
})

test('toggling an unchecked switch emits true', async () => {
  const onUpdate = vi.fn()
  mountCell(false, onUpdate)

  await fireEvent.click(screen.getByRole('switch'))

  expect(onUpdate).toHaveBeenCalledWith(true)
})

test('toggling a checked switch emits false', async () => {
  const onUpdate = vi.fn()
  mountCell(true, onUpdate)

  await fireEvent.click(screen.getByRole('switch'))

  expect(onUpdate).toHaveBeenCalledWith(false)
})
