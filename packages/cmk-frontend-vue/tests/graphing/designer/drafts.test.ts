/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import {
  type DesignerItem,
  isComplete,
  newConstantDraft,
  newMetricBackendDraft,
  newRrdMetricDraft,
  newRrdQueryDraft,
  newScalarDraft,
  rrdMetricToQueryDraft,
  rrdQueryToMetricDraft,
  scalarColor,
  toApiDataSources
} from '@/graphing/designer/drafts'
import { DEFAULT_TITLE_MACRO } from '@/graphing/designer/types'

import {
  constantItem,
  formulaItem,
  metricBackendItem,
  rrdMetricItem,
  rrdQueryItem,
  scalarItem
} from './fixtures'

const THRESHOLDS = { warning: '#ffd000', critical: '#ff3232' }

describe('isComplete', () => {
  test('a fresh RRD metric draft is incomplete until host, service and metric are set', () => {
    const draft = newRrdMetricDraft('A', '#123456')
    expect(isComplete(draft)).toBe(false)
    expect(isComplete({ ...draft, host_name: 'h' })).toBe(false)
    expect(isComplete({ ...draft, host_name: 'h', service_name: 's' })).toBe(false)
    expect(isComplete({ ...draft, host_name: 'h', service_name: 's', metric_name: 'm' })).toBe(true)
  })

  test('a fresh constant draft is incomplete until it has a value', () => {
    const draft = newConstantDraft('A', '#123456')
    expect(isComplete(draft)).toBe(false)
    expect(isComplete({ ...draft, value: 0 })).toBe(true)
  })

  test('a fresh RRD query draft is incomplete until a metric is set (filters stay optional)', () => {
    const draft = newRrdQueryDraft('A')
    expect(isComplete(draft)).toBe(false)
    expect(isComplete({ ...draft, metric_name: 'util' })).toBe(true)
  })

  test('a scalar needs host, service and metric', () => {
    expect(isComplete(newScalarDraft('A', '#123456'))).toBe(false)
    expect(isComplete(scalarItem('A'))).toBe(true)
  })

  test('a fresh metric backend draft is incomplete until a metric is set', () => {
    const draft = newMetricBackendDraft('A')
    expect(isComplete(draft)).toBe(false)
    expect(isComplete({ ...draft, metric_name: 'span.latency' })).toBe(true)
  })

  test('wire items are always complete', () => {
    for (const item of [
      rrdMetricItem('A'),
      rrdQueryItem('B'),
      metricBackendItem('C'),
      constantItem('D'),
      formulaItem('E'),
      scalarItem('F')
    ]) {
      expect(isComplete(item)).toBe(true)
    }
  })
})

describe('toApiDataSources', () => {
  test('keeps complete rows in table order and drops incomplete ones', () => {
    const items: DesignerItem[] = [
      rrdMetricItem('A'),
      newRrdMetricDraft('B', '#123456'),
      constantItem('C')
    ]
    expect(toApiDataSources(items).map((source) => source.id)).toEqual(['A', 'C'])
  })

  test('drops formulas whose refs reach an incomplete row, transitively', () => {
    const items: DesignerItem[] = [
      newConstantDraft('A', '#123456'),
      formulaItem('B', { ast: { op: 'ref', id: 'A' } }),
      formulaItem('C', { ast: { op: 'ref', id: 'B' } }),
      formulaItem('D', { ast: { op: 'num', value: 1 } })
    ]
    expect(toApiDataSources(items).map((source) => source.id)).toEqual(['D'])
  })
})

describe('drafts and converters', () => {
  test('new drafts start with the default title macro and defaults', () => {
    const draft = newRrdMetricDraft('A', '#123456')
    expect(draft.title).toBe(DEFAULT_TITLE_MACRO)
    expect(draft.line_type).toBe('line')
    expect(draft.mirrored).toBe(false)
    expect(draft.visible).toBe(true)
    expect(draft.color).toBe('#123456')
    expect(draft.consolidation).toBe('avg')
  })

  test('a fresh scalar draft starts as a warning threshold with an empty selection', () => {
    const draft = newScalarDraft('A', '#123456')
    expect(draft).toEqual({
      id: 'A',
      type: 'scalar',
      title: DEFAULT_TITLE_MACRO,
      line_type: 'line',
      mirrored: false,
      visible: true,
      color: '#123456',
      host_name: null,
      service_name: null,
      metric_name: null,
      scalar_type: 'warning'
    })
  })

  test('a fresh RRD query draft starts empty with the default title and no color', () => {
    const draft = newRrdQueryDraft('A')
    expect(draft).toEqual({
      id: 'A',
      type: 'rrd_query',
      title: DEFAULT_TITLE_MACRO,
      line_type: 'line',
      mirrored: false,
      visible: true,
      context: {},
      metric_name: null,
      consolidation: 'avg'
    })
  })

  test('switching a single metric to a query keeps metric and consolidation, drops color and host/service', () => {
    const metric = {
      ...newRrdMetricDraft('A', '#123456'),
      title: 'T',
      line_type: 'area' as const,
      mirrored: true,
      visible: false,
      host_name: 'h',
      service_name: 's',
      metric_name: 'util',
      consolidation: 'max' as const
    }
    const query = rrdMetricToQueryDraft(metric)
    expect(query).toEqual({
      id: 'A',
      type: 'rrd_query',
      title: 'T',
      line_type: 'area',
      mirrored: true,
      visible: false,
      context: {},
      metric_name: 'util',
      consolidation: 'max'
    })
    expect('color' in query).toBe(false)
  })

  test('switching a query back to a single metric assigns a color and clears host/service', () => {
    const query = {
      ...newRrdQueryDraft('A'),
      metric_name: 'util',
      consolidation: 'min' as const,
      context: { host: { host: 'h' } }
    }
    expect(rrdQueryToMetricDraft(query, '#abcdef')).toEqual({
      id: 'A',
      type: 'rrd_metric',
      title: DEFAULT_TITLE_MACRO,
      line_type: 'line',
      mirrored: false,
      visible: true,
      color: '#abcdef',
      host_name: null,
      service_name: null,
      metric_name: 'util',
      consolidation: 'min'
    })
  })

  test('warning and critical scalars get the fixed threshold colors', () => {
    expect(scalarColor('warning', '#123456', THRESHOLDS)).toBe(THRESHOLDS.warning)
    expect(scalarColor('warning_lower', '#123456', THRESHOLDS)).toBe(THRESHOLDS.warning)
    expect(scalarColor('critical', '#123456', THRESHOLDS)).toBe(THRESHOLDS.critical)
    expect(scalarColor('critical_lower', '#123456', THRESHOLDS)).toBe(THRESHOLDS.critical)
    expect(scalarColor('min', '#123456', THRESHOLDS)).toBe('#123456')
    expect(scalarColor('max', '#123456', THRESHOLDS)).toBe('#123456')
  })
})
