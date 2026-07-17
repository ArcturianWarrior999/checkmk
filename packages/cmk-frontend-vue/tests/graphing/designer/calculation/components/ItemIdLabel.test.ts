/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render } from '@testing-library/vue'

import ItemIdLabel from '@/graphing/designer/calculation/components/ItemIdLabel.vue'

// The label contains hidden ghost text nodes (W/M repetitions) besides the visible id, so
// tests should query the id span instead of using getByText on bare glyphs.
function renderLabel(id: string) {
  const { container } = render(ItemIdLabel, { props: { id } })
  return {
    id: container.querySelector('.graphing-item-id-label__id') as HTMLElement,
    ghosts: Array.from(container.querySelectorAll<HTMLElement>('.cmk-ghost-width__ghost')).map(
      (ghost) => ghost.textContent
    )
  }
}

test('shows the id', () => {
  expect(renderLabel('AB').id).toHaveTextContent('AB')
})

test.each([
  ['A', ['W', 'M']],
  ['AA', ['WW', 'MM']]
])('reserves the width of the widest possible id of the same length as %s', (id, ghosts) => {
  expect(renderLabel(id).ghosts).toEqual(ghosts)
})

test('same-length ids reserve identical widths', () => {
  expect(renderLabel('I').ghosts).toEqual(renderLabel('W').ghosts)
})
