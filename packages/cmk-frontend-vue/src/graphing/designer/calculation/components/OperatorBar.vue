<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import usei18n from '@/lib/i18n'
import type { TranslatedString } from '@/lib/i18nString'

import CmkButton from '@/components/CmkButton'

import type { FunctionName, OperatorSymbol } from '../formula'

const { _t } = usei18n()

const emit = defineEmits<{
  insert: [symbol: OperatorSymbol]
  wrap: [name: FunctionName]
}>()

const operators: [OperatorSymbol, TranslatedString][] = [
  ['+', _t('Add')],
  ['-', _t('Subtract')],
  ['*', _t('Multiply')],
  ['/', _t('Divide')]
]

const functions: [FunctionName, { label: TranslatedString; title: TranslatedString }][] = [
  ['avg', { label: _t('Average'), title: _t('Wrap the whole formula in an average') }],
  ['min', { label: _t('Min'), title: _t('Wrap the whole formula in a minimum') }],
  ['max', { label: _t('Max'), title: _t('Wrap the whole formula in a maximum') }],
  ['sum', { label: _t('Sum'), title: _t('Wrap the whole formula in a sum') }]
]
</script>

<template>
  <div class="graphing-operator-bar">
    <div class="graphing-operator-bar__group">
      <CmkButton
        v-for="[symbol, title] in operators"
        :key="symbol"
        variant="optional"
        class="graphing-operator-bar__operator"
        :title="title"
        :aria-label="title"
        @click="emit('insert', symbol)"
      >
        {{ symbol }}
      </CmkButton>
    </div>
    <div class="graphing-operator-bar__group">
      <CmkButton
        v-for="[name, { label, title }] in functions"
        :key="name"
        variant="optional"
        :title="title"
        @click="emit('wrap', name)"
      >
        {{ label }}
      </CmkButton>
    </div>
  </div>
</template>

<style scoped>
.graphing-operator-bar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--dimension-4);
  align-items: center;
}

.graphing-operator-bar__group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--dimension-3);
}

.graphing-operator-bar__operator {
  width: var(--dimension-10);
  min-width: var(--dimension-10);
  padding: 0;
}
</style>
