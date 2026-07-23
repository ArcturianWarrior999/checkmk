/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'
import { expect, test, vi } from 'vitest'
import { defineComponent, h } from 'vue'

import { Response } from '@/components/CmkSuggestions'

import MetricBackendForm from '@/graphing/designer/components/forms/MetricBackendForm.vue'
import { useGraphItems } from '@/graphing/designer/composables/useGraphItems'
import { type DraftMetricBackendItem, newMetricBackendDraft } from '@/graphing/designer/drafts'

const mocks = vi.hoisted(() => ({ fetchSuggestions: vi.fn(), fetchRestAPIDeprecated: vi.fn() }))

vi.mock(import('@/form/private/FormAutocompleter/autocompleter'), async (importOriginal) => {
  const mod = await importOriginal()
  return { ...mod, fetchSuggestions: mocks.fetchSuggestions }
})

vi.mock(import('@/lib/cmkFetch'), async (importOriginal) => {
  const mod = await importOriginal()
  return { ...mod, fetchRestAPIDeprecated: mocks.fetchRestAPIDeprecated }
})

const PALETTE: readonly string[] = ['#28a2f3', '#ff8400']

function renderForm(seed: DraftMetricBackendItem) {
  mocks.fetchSuggestions.mockResolvedValue(new Response([]))
  mocks.fetchRestAPIDeprecated.mockResolvedValue({
    raiseForStatus: async () => {},
    json: async () => ({ choices: [] })
  })
  const store = useGraphItems(PALETTE, [seed])
  const harness = defineComponent({
    setup() {
      return () => {
        const item = store.items.value.find((candidate) => candidate.id === seed.id)
        return item?.type === 'metric_backend' ? h(MetricBackendForm, { item, store }) : null
      }
    }
  })
  render(harness)
  return store
}

test('composes the metric, attributes and consolidation sections', async () => {
  renderForm(newMetricBackendDraft('A'))

  expect(await screen.findByText('Metric')).toBeInTheDocument()
  expect(screen.getByText('Attributes')).toBeInTheDocument()
  expect(screen.getByText('Consolidation')).toBeInTheDocument()
})
