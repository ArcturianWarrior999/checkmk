/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render, screen } from '@testing-library/vue'
import { describe, expect, test } from 'vitest'

import PinHandle from '@/graphing/components/TimeSeriesGraph/overlay/PinHandle.vue'

describe('PinHandle', () => {
  test('the add variant is a labeled button with a "+" glyph (two bars)', () => {
    const { container } = render(PinHandle, { props: { variant: 'add' } })

    expect(screen.getByRole('button', { name: 'Add pin' })).toBeInTheDocument()
    expect(container.querySelectorAll('.graphing-pin-handle__glyph')).toHaveLength(2)
  })

  test('the remove variant is a labeled button with a "−" glyph (one bar)', () => {
    const { container } = render(PinHandle, { props: { variant: 'remove' } })

    expect(screen.getByRole('button', { name: 'Remove pin' })).toBeInTheDocument()
    expect(container.querySelectorAll('.graphing-pin-handle__glyph')).toHaveLength(1)
  })

  test('a click emits action', async () => {
    const { emitted } = render(PinHandle, { props: { variant: 'remove' } })

    await fireEvent.click(screen.getByRole('button', { name: 'Remove pin' }))

    expect(emitted()).toHaveProperty('action')
  })
})
