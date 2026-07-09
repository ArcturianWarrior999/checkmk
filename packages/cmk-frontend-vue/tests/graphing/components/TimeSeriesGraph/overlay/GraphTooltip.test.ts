/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'
import { describe, expect, test } from 'vitest'

import type {
  HoverSample,
  HoverState
} from '@/graphing/components/TimeSeriesGraph/interaction/hover'
import GraphTooltip from '@/graphing/components/TimeSeriesGraph/overlay/GraphTooltip.vue'

function makeSample(overrides: Partial<HoverSample>): HoverSample {
  return {
    metricName: 'cpu',
    label: 'CPU',
    color: '#ff0000',
    formattedValue: '42 %',
    pixelY: 10,
    snapTime: 1000,
    isClosest: false,
    ...overrides
  }
}

function renderGraphTooltip(hoverState: HoverState | null): ReturnType<typeof render> {
  return render(GraphTooltip, {
    props: { hoverState },
    global: {
      stubs: {
        CmkTooltipProvider: { template: '<div><slot /></div>' },
        CmkTooltip: { template: '<div><slot /></div>' },
        CmkTooltipTrigger: { template: '<div><slot /></div>' },
        CmkTooltipContent: { template: '<div><slot /></div>' }
      }
    }
  })
}

describe('GraphTooltip', () => {
  test('renders one sample per metric with label and formatted value', () => {
    const hoverState: HoverState = {
      cursorX: 5,
      cursorY: 5,
      snapX: 5,
      snapTime: 1000,
      samples: [
        makeSample({ metricName: 'cpu', label: 'CPU', formattedValue: '42 %' }),
        makeSample({ metricName: 'mem', label: 'Memory', formattedValue: '1.5 GB' })
      ]
    }

    renderGraphTooltip(hoverState)

    expect(screen.getByText('CPU')).toBeInTheDocument()
    expect(screen.getByText('42 %')).toBeInTheDocument()
    expect(screen.getByText('Memory')).toBeInTheDocument()
    expect(screen.getByText('1.5 GB')).toBeInTheDocument()
  })

  test('marks only the closest sample with the emphasis class', () => {
    const hoverState: HoverState = {
      cursorX: 5,
      cursorY: 5,
      snapX: 5,
      snapTime: 1000,
      samples: [
        makeSample({ metricName: 'cpu', label: 'CPU', isClosest: false }),
        makeSample({ metricName: 'mem', label: 'Memory', isClosest: true })
      ]
    }

    const { container } = renderGraphTooltip(hoverState)

    const emphasized = container.querySelectorAll('.graphing-graph-tooltip__row--is-closest')
    expect(emphasized).toHaveLength(1)
    expect(emphasized[0]!.textContent).toContain('Memory')
  })

  test('shows the snap time as weekday, ISO date and 24h clock time', () => {
    const snapTime = 1781526896
    const hoverState: HoverState = {
      cursorX: 5,
      cursorY: 5,
      snapX: 5,
      snapTime,
      samples: [makeSample({})]
    }

    renderGraphTooltip(hoverState)

    expect(screen.getByText(/, \d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}/)).toBeInTheDocument()
  })

  test('renders no samples without a hover state', () => {
    const { container } = renderGraphTooltip(null)

    expect(container.querySelectorAll('.graphing-graph-tooltip__row')).toHaveLength(0)
  })
})
