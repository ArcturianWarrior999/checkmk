/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render, screen } from '@testing-library/vue'
import { defineComponent, h } from 'vue'

import RichTextCell from '@/monitoring/shared/components/cell/RichTextCell.vue'

function mountCell(props: Record<string, unknown>, slot?: () => unknown) {
  return render(
    defineComponent({
      render() {
        return h('table', [
          h('tbody', [h('tr', [h(RichTextCell, props, slot && { default: slot })])])
        ])
      }
    })
  )
}

test('renders the value as cell text', () => {
  mountCell({ value: 'web-1 is fine' })

  expect(screen.getByTitle('web-1 is fine')).toBeInTheDocument()
})

test('renders nested components passed via the default slot', () => {
  mountCell({}, () => [
    h('span', { 'data-testid': 'nested' }, 'CPU'),
    h('a', { href: '/x' }, 'details')
  ])

  expect(screen.getByTestId('nested')).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'details' })).toBeInTheDocument()
})

test('renders a placeholder when neither value nor slot is given', () => {
  const { container } = mountCell({})

  const cell = container.querySelector('td')
  expect(cell).not.toBeNull()
  expect(cell).toHaveTextContent('n/a')
})

test('renders a button and forwards its click when the button prop is set', async () => {
  const onClick = vi.fn()
  const { container } = mountCell({ value: 'web-1', button: true, onClick })

  const button = container.querySelector('button')
  expect(button).not.toBeNull()
  await fireEvent.click(button!)
  expect(onClick).toHaveBeenCalledTimes(1)
})
