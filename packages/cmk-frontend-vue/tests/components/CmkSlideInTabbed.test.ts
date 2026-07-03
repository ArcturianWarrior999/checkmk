/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import userEvent from '@testing-library/user-event'
import { render, screen } from '@testing-library/vue'
import { defineComponent, h, markRaw } from 'vue'

import CmkSlideInTabbed from '@/components/CmkSlideInTabbed/CmkSlideInTabbed.vue'
import type { SlideInTab } from '@/components/CmkSlideInTabbed/types'

const tabBody = markRaw(
  defineComponent({
    props: { data: { type: String, default: '' } },
    setup: (props) => () => h('div', { 'data-testid': 'tab-body' }, props.data)
  })
)

const header = { title: 'Host', closeButton: true }

test('loads and renders the active tab content', async () => {
  const load = vi.fn().mockResolvedValue('resolved content')
  const tabs: SlideInTab[] = [{ id: 'a', title: 'A', component: tabBody, load }]

  render(CmkSlideInTabbed, { props: { open: true, tabs, header } })

  await screen.findByText('resolved content')
  expect(load).toHaveBeenCalledTimes(1)
})

test('shows an error with a retry that reloads the tab', async () => {
  const load = vi
    .fn()
    .mockRejectedValueOnce(new Error('boom'))
    .mockResolvedValueOnce('recovered content')
  const tabs: SlideInTab[] = [{ id: 'a', title: 'A', component: tabBody, load }]

  render(CmkSlideInTabbed, { props: { open: true, tabs, header } })

  await screen.findByText('Could not load this content.')
  await userEvent.click(screen.getByRole('button', { name: 'Retry' }))

  await screen.findByText('recovered content')
  expect(load).toHaveBeenCalledTimes(2)
})

test('caches loaded tabs and re-fetches only on reopen', async () => {
  const loadA = vi.fn().mockResolvedValue('a-data')
  const loadB = vi.fn().mockResolvedValue('b-data')
  const tabs: SlideInTab[] = [
    { id: 'a', title: 'A', component: tabBody, load: loadA },
    { id: 'b', title: 'B', component: tabBody, load: loadB }
  ]

  const { rerender } = render(CmkSlideInTabbed, { props: { open: true, tabs, header } })

  await screen.findByText('a-data')
  await userEvent.click(screen.getByRole('tab', { name: 'B' }))
  await screen.findByText('b-data')
  await userEvent.click(screen.getByRole('tab', { name: 'A' }))
  await screen.findByText('a-data')
  expect(loadA).toHaveBeenCalledTimes(1)

  await rerender({ open: false, tabs, header })
  await rerender({ open: true, tabs, header })

  await screen.findByText('a-data')
  expect(loadA).toHaveBeenCalledTimes(2)
})
