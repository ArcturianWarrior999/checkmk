/**
 * Copyright (C) 2026 Checkmk GmbH - License: Checkmk Enterprise License
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import usei18n from '@/lib/i18n'
import type { TranslatedString } from '@/lib/i18nString'

import { operatorTakesValue } from './types'
import type { AttributeCondition, AttributeKind, Operator } from './types'

export const ATTRIBUTE_KIND_LABELS: Record<Exclude<AttributeKind, null>, string> = {
  resource: 'Resource',
  scope: 'Scope',
  datapoint: 'Data point'
}

function attributeKindPrefixes(): Record<Exclude<AttributeKind, null>, TranslatedString> {
  const { _t } = usei18n()
  return {
    resource: _t('[Resource]'),
    scope: _t('[Scope]'),
    datapoint: _t('[Data point]')
  }
}

function operatorPhrases(): Record<Operator, TranslatedString> {
  const { _t } = usei18n()
  return {
    eq: _t('is'),
    neq: _t('is not'),
    contains: _t('contains'),
    not_contains: _t('does not contain'),
    starts_with: _t('starts with'),
    not_starts_with: _t('does not start with'),
    ends_with: _t('ends with'),
    not_ends_with: _t('does not end with'),
    regex: _t('matches regex'),
    not_regex: _t('does not match regex'),
    exists: _t('exists'),
    not_exists: _t('does not exist')
  }
}

export function attributeKindPrefix(attributeKind: AttributeKind): string {
  return attributeKind === null ? '' : `${attributeKindPrefixes()[attributeKind]} `
}

export function operatorPhrase(operator: Operator): TranslatedString {
  return operatorPhrases()[operator]
}

export function pillLabel(condition: AttributeCondition): string {
  const prefix = attributeKindPrefix(condition.attributeKind)
  const phrase = operatorPhrase(condition.operator)
  const key = condition.key ?? ''
  if (operatorTakesValue(condition.operator)) {
    return `${prefix}${key} ${phrase} ${condition.value}`
  }
  return `${prefix}${key} ${phrase}`
}
