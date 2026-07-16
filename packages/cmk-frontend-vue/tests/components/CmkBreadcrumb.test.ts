/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'

import CmkBreadcrumb from '@/components/CmkBreadcrumb'

const items = [
  { title: 'Customize', link: null },
  { title: 'Custom graphs', link: '/custom_graphs.py' },
  { title: 'My graph', link: null }
]

test('renders linked items as anchors and unlinked items as static text', () => {
  render(CmkBreadcrumb, { props: { items } })

  expect(screen.getByRole('link', { name: 'Custom graphs' }).getAttribute('href')).toBe(
    '/custom_graphs.py'
  )
  expect(screen.queryByRole('link', { name: 'Customize' })).toBeNull()
  expect(screen.queryByRole('link', { name: 'My graph' })).toBeNull()
})

test('marks the last item as final and adds separators to the rest', () => {
  const { container } = render(CmkBreadcrumb, { props: { items } })

  const finals = container.querySelectorAll('.cmk-breadcrumb__item-final')
  expect(finals.length).toBe(1)
  expect(finals[0]?.textContent?.trim()).toBe('My graph')
  expect(container.querySelectorAll('.cmk-breadcrumb__item').length).toBe(2)
})
