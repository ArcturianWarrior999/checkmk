<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import usei18n from '@/lib/i18n'

import CmkMultitoneIcon from '@/components/CmkIcon/CmkMultitoneIcon.vue'

import type { HostState, ServiceState } from '../../api/types.ts'
import HostStateDisplay from '../HostStateDisplay.vue'
import ServiceStateDisplay from '../ServiceStateDisplay.vue'
import BaseCell from './BaseCell.vue'

interface BaseStateCellProps {
  stale?: boolean | undefined
  pending?: boolean | undefined
  columnId?: string | undefined
}

export type StateCellProps = BaseStateCellProps &
  ({ kind?: 'host'; state: HostState } | { kind: 'service'; state: ServiceState })

const { _t } = usei18n()

const props = defineProps<StateCellProps>()
</script>

<template>
  <BaseCell :column-id="columnId">
    <template #default>
      <div class="monitoring-state-cell">
        <ServiceStateDisplay
          v-if="props.kind === 'service'"
          :state="props.state"
          :pending="pending"
        />
        <HostStateDisplay v-else :state="props.state" :pending="pending" />
        <CmkMultitoneIcon
          v-if="stale"
          name="stale"
          primary-color="font"
          :title="_t('Stale state')"
        />
      </div>
    </template>
  </BaseCell>
</template>

<style scoped>
.monitoring-state-cell {
  display: flex;
  flex-direction: row;
  gap: var(--dimension-4);
  align-items: center;
  justify-content: center;
}
</style>
