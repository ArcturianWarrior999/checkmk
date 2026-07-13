/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { fireEvent, render, screen } from '@testing-library/vue'
import { defineComponent, h } from 'vue'

import { untranslated } from '@/lib/i18n'

import type { Suggestions } from '@/components/CmkSuggestions'

import DropdownCell from '@/monitoring/shared/components/cell/DropdownCell.vue'

const OPTIONS: Suggestions = {
  type: 'fixed',
  suggestions: [
    { name: 'rrd', title: untranslated('CMK RRD') },
    { name: 'backend', title: untranslated('Metrics backend') }
  ]
}

function mountCell(selected: string | null, onUpdate: (value: string | null) => void = () => {}) {
  return render(
    defineComponent({
      render() {
        return h('table', [
          h('tbody', [
            h('tr', [
              h(DropdownCell, {
                options: OPTIONS,
                label: untranslated('Source'),
                modelValue: selected,
                'onUpdate:modelValue': onUpdate
              })
            ])
          ])
        ])
      }
    })
  )
}

test('shows the title of the selected option', async () => {
  mountCell('rrd')

  // The dropdown resolves its button label asynchronously and truncates it,
  // so match on the title attribute instead of the (split-up) text.
  expect(await screen.findByTitle('CMK RRD')).toBeInTheDocument()
})

test('selecting another option emits its name', async () => {
  const onUpdate = vi.fn()
  mountCell('rrd', onUpdate)

  await fireEvent.click(screen.getByRole('combobox', { name: 'Source' }))
  await fireEvent.click(await screen.findByText('Metrics backend'))

  expect(onUpdate).toHaveBeenCalledWith('backend')
})
