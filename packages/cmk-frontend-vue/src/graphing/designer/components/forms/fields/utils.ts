/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { ConfiguredFilters } from '@/components/filter'

/** Builds a filter context from single host/service names, dropping the unset ones. */
export function hostServiceContext(
  hostName: string | null,
  serviceName: string | null
): ConfiguredFilters {
  return {
    ...(hostName === null ? {} : { host: { host: hostName } }),
    ...(serviceName === null ? {} : { service: { service: serviceName } })
  }
}
