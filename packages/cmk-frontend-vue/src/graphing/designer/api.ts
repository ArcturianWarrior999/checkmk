/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { components } from 'cmk-shared-typing/typescript/openapi_internal'

import client, { unwrap } from '@/lib/rest-api-client/client'

/** Request body for previewing an unsaved custom-graph definition. */
export type FetchCustomGraphDataRequest = components['schemas']['FetchCustomGraphData']
/** One evaluated series with the id of the data source that produced it. */
export type CustomGraphMetric = components['schemas']['CustomGraphMetric']

const CONTENT_TYPE_HEADER = { 'Content-Type': 'application/json' } as const

/** Evaluate an unsaved custom-graph definition over a time range (preview). */
export async function fetchCustomGraphData(body: FetchCustomGraphDataRequest) {
  return unwrap(
    await client.POST('/domain-types/custom_graph/actions/fetch_data/invoke', {
      params: { header: CONTENT_TYPE_HEADER },
      body
    })
  )
}
