/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render } from '@testing-library/vue'
import { defineComponent, h } from 'vue'

import ColorPickerCell from '@/monitoring/shared/components/cell/ColorPickerCell.vue'

function mountCell(color: string, onUpdate: (value: string) => void = () => {}) {
  return render(
    defineComponent({
      render() {
        return h('table', [
          h('tbody', [
            h('tr', [h(ColorPickerCell, { modelValue: color, 'onUpdate:modelValue': onUpdate })])
          ])
        ])
      }
    })
  )
}

test('renders a color input with the current color', () => {
  const { container } = mountCell('#ff8800')

  const input = container.querySelector<HTMLInputElement>('input[type="color"]')
  expect(input).not.toBeNull()
  expect(input!.value).toBe('#ff8800')
})

test('changing the color emits the new value', async () => {
  const onUpdate = vi.fn()
  const { container } = mountCell('#ff8800', onUpdate)

  const input = container.querySelector<HTMLInputElement>('input[type="color"]')!
  await fireEvent.update(input, '#00ff00')

  expect(onUpdate).toHaveBeenCalledWith('#00ff00')
})
