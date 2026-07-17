/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import type { CustomGraphDesignerMode } from 'cmk-shared-typing/typescript/custom_graph_designer'

export interface DesignerUrlState {
  name: string
  owner: string
  mode: CustomGraphDesignerMode
}

function designerUrl(state: DesignerUrlState): URL {
  const url = new URL(window.location.href)
  url.searchParams.set('name', state.name)
  url.searchParams.set('owner', state.owner)
  if (state.mode === 'edit') {
    url.searchParams.set('mode', 'edit')
  } else {
    url.searchParams.delete('mode')
  }
  return url
}

/** Mirror a mode toggle into the URL without a history entry. */
export function replaceUrlState(state: DesignerUrlState): void {
  window.history.replaceState(null, '', designerUrl(state))
}

/** Mirror a graph switch into the URL as a new history entry. */
export function pushUrlState(state: DesignerUrlState): void {
  window.history.pushState(null, '', designerUrl(state))
}
