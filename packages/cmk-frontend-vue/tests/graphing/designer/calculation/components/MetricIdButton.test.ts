/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render, screen } from '@testing-library/vue'

import { untranslated } from '@/lib/i18n'

import MetricIdButton from '@/graphing/designer/calculation/components/MetricIdButton.vue'

const DARK_TEXT = 'rgb(30, 38, 46)'
const LIGHT_TEXT = 'rgb(255, 255, 255)'

function renderButton(props: Record<string, unknown> = {}) {
  const rendered = render(MetricIdButton, {
    props: { id: 'A', label: untranslated('Insert A'), ...props }
  })
  return {
    ...rendered,
    chip: rendered.container.querySelector('.graphing-metric-id-button__chip') as HTMLElement
  }
}

test.each([
  ['#ffe000', 'rgb(255, 224, 0)', DARK_TEXT],
  ['#0667c1', 'rgb(6, 103, 193)', LIGHT_TEXT]
])(
  'the chip text contrasts with the item color %s',
  (color, expectedBackground, expectedContrast) => {
    const { chip } = renderButton({ color })
    expect(chip.style.backgroundColor).toBe(expectedBackground)
    expect(chip.style.color).toBe(expectedContrast)
  }
)

test('falls back to the grey placeholder without an item color', () => {
  const { chip } = renderButton()
  expect(chip.style.backgroundColor).toBe('var(--color-mid-grey-50)')
  expect(chip.style.color).toBe('var(--color-conference-grey-100)')
})

test('emits click and takes its accessible name from the label', async () => {
  const { emitted } = renderButton()
  await fireEvent.click(screen.getByRole('button', { name: 'Insert A' }))
  expect(emitted('click')).toHaveLength(1)
})

test('can be disabled', () => {
  renderButton({ disabled: true })
  expect(screen.getByRole('button', { name: 'Insert A' })).toBeDisabled()
})
