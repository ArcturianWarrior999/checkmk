/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import client, { unwrap } from '@/lib/rest-api-client/client'

export async function loadGraphPin(): Promise<number | null> {
  return unwrap(await client.GET('/domain-types/graph/actions/get_pin/invoke')).pin_time
}

export async function saveGraphPin(pinTime: number | null): Promise<void> {
  unwrap(
    await client.POST('/domain-types/graph/actions/set_pin/invoke', {
      params: { header: { 'Content-Type': 'application/json' } },
      body: { pin_time: pinTime }
    })
  )
}
