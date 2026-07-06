/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render } from '@testing-library/vue'

import CmkRankedTable from '@/components/CmkRankedTable/CmkRankedTable.vue'
import type { RankedTableColumn, RankedTableRow } from '@/components/CmkRankedTable/types'

const COLUMNS: RankedTableColumn[] = [
  { key: 'host', title: 'Host', render: 'text', bar: false },
  { key: 'ingress', title: 'Ingress', render: 'bytes', bar: false },
  { key: 'volume', title: 'Volume', render: 'bytes', bar: true }
]

const ROWS: RankedTableRow[] = [
  { host: 'B', ingress: 5e9, volume: 100e9 },
  { host: 'A', ingress: 10e9, volume: 40e9 },
  { host: 'C', ingress: 1e9, volume: 20e9 }
]

function renderTable(rows: RankedTableRow[] = ROWS) {
  return render(CmkRankedTable, {
    props: { columns: COLUMNS, rows, barColor: 'rgb(1, 2, 3)' }
  })
}

test('renders a header per column and a row per data entry', () => {
  const { container } = renderTable()

  expect(container.querySelectorAll('.cmk-ranked-table__th')).toHaveLength(3)
  expect(container.querySelector('thead')).toHaveTextContent('Host')
  expect(container.querySelectorAll('tbody tr')).toHaveLength(3)
})

test('keeps the row order provided by the caller', () => {
  const { container } = renderTable()

  const firstCells = [...container.querySelectorAll('tbody tr')].map(
    (tr) => tr.querySelector('td')?.textContent
  )
  expect(firstCells).toEqual(['B', 'A', 'C'])
})

test('scales inline bars to the column max and fills them with the accent color', () => {
  const { container } = renderTable()

  const fills = [...container.querySelectorAll<HTMLElement>('.cmk-ranked-table__bar-fill')]
  expect(fills.map((el) => el.style.width)).toEqual(['100%', '40%', '20%'])
  expect(fills[0]!.style.backgroundColor).toBe('rgb(1, 2, 3)')
})

test('formats byte columns as human-readable SI values', () => {
  const { container } = renderTable([
    { host: 'A', ingress: 10e9, volume: 90.4e9 },
    { host: 'B', ingress: 5e9, volume: 552.63e6 }
  ])

  const barValues = [...container.querySelectorAll('.cmk-ranked-table__bar-value')].map(
    (el) => el.textContent
  )
  // Scaled to GB / MB (the SI formatter trims trailing zeros: 90.4, not 90.40).
  expect(barValues).toEqual(['90.4 GB', '552.63 MB'])
})
