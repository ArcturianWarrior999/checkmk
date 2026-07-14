<!--
Copyright (C) 2025 Checkmk GmbH - License: Checkmk Enterprise License
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<script setup lang="ts">
import type { GraphLineQueryAttributes } from 'cmk-shared-typing/typescript/graph_designer'
import type { Autocompleter } from 'cmk-shared-typing/typescript/vue_formspec_components'
import { ref, watch } from 'vue'

import usei18n, { untranslated } from '@/lib/i18n'
import type { TranslatedString } from '@/lib/i18nString'
import { randomId } from '@/lib/randomId'
import { immediateWatch } from '@/lib/watch'

import CmkIndent from '@/components/CmkIndent.vue'
import {
  ErrorResponse,
  Response,
  type Section,
  type Suggestion,
  flattenSuggestions
} from '@/components/CmkSuggestions'
import FormValidation from '@/components/user-input/CmkInlineValidation.vue'

import type { ValidationMessages } from '@/form'
import { fetchSuggestions } from '@/form/private/FormAutocompleter/autocompleter'

import FormAttributeFilter from './attribute-filter/FormAttributeFilter.vue'
import type { AttributeFilterModel, AttributeKind, Condition } from './attribute-filter/types'
import {
  ATTRIBUTE_KIND_ORDER,
  type AttributeKindKey,
  KEY_IDENTS,
  type ThreeLists,
  VALUE_IDENTS,
  buildAutocompleteContext,
  fromModel,
  toModel
} from './attributeFilterAdapter'

const { _t } = usei18n()

const props = withDefaults(
  defineProps<{
    metricName?: string | null
    staticResourceAttributeKeys?: string[] | null
    indent?: boolean
  }>(),
  {
    metricName: null,
    staticResourceAttributeKeys: null,
    indent: false
  }
)

const backendValidation = defineModel<ValidationMessages>('backendValidation', { default: [] })

const resourceAttributes = defineModel<GraphLineQueryAttributes>('resourceAttributes', {
  default: []
})
const scopeAttributes = defineModel<GraphLineQueryAttributes>('scopeAttributes', {
  default: []
})
const dataPointAttributes = defineModel<GraphLineQueryAttributes>('dataPointAttributes', {
  default: []
})

const LOCATION_TO_KIND: Record<string, AttributeKindKey> = {
  resource_attributes: 'resource',
  scope_attributes: 'scope',
  data_point_attributes: 'datapoint'
}

const SECTION_TITLES: Record<AttributeKindKey, TranslatedString> = {
  resource: _t('Resource'),
  scope: _t('Scope'),
  datapoint: _t('Data point')
}

// The flat pill model is the single source of truth; the three list models are
// kept in sync from it.
const filterModel = ref<AttributeFilterModel>(
  toModel(
    {
      resource: resourceAttributes.value,
      scope: scopeAttributes.value,
      datapoint: dataPointAttributes.value
    },
    () => randomId()
  )
)
// A key may be offered under more than one attribute kind, so record the set of
// kinds each suggested key belongs to (see `resolveAttributeKind`).
const keyKindCache = new Map<string, Set<AttributeKindKey>>()
const validationMessages = ref<string[]>([])

function cacheKeyKind(name: string, attributeKind: AttributeKindKey): void {
  const kinds = keyKindCache.get(name)
  if (kinds) {
    kinds.add(attributeKind)
  } else {
    keyKindCache.set(name, new Set([attributeKind]))
  }
}

function attributesEqual(a: GraphLineQueryAttributes, b: GraphLineQueryAttributes): boolean {
  return (
    a.length === b.length &&
    a.every((attr, i) => attr.key === b[i]!.key && attr.value === b[i]!.value)
  )
}

// Only reassign a list model when its derived content actually changed, so an
// in-progress (key-less) pill or an unrelated edit does not churn the parent
// models with fresh array references on every keystroke.
watch(
  filterModel,
  (model) => {
    const lists = fromModel(model)
    if (!attributesEqual(lists.resource, resourceAttributes.value)) {
      resourceAttributes.value = lists.resource
    }
    if (!attributesEqual(lists.scope, scopeAttributes.value)) {
      scopeAttributes.value = lists.scope
    }
    if (!attributesEqual(lists.datapoint, dataPointAttributes.value)) {
      dataPointAttributes.value = lists.datapoint
    }
  },
  { deep: true }
)

watch(
  () => props.metricName,
  () => {
    filterModel.value = []
  }
)

immediateWatch(
  () => backendValidation.value,
  (newValidation: ValidationMessages | undefined) => {
    validationMessages.value = []
    if (!newValidation || newValidation.length === 0) {
      return
    }
    const lists: ThreeLists = fromModel(filterModel.value)
    newValidation.forEach((message) => {
      validationMessages.value.push(message.message)
      const attributeKind = LOCATION_TO_KIND[message.location[0] ?? '']
      if (attributeKind !== undefined) {
        lists[attributeKind] = message.replacement_value as GraphLineQueryAttributes
      }
    })
    filterModel.value = toModel(lists, () => randomId())
  }
)

async function querySuggestions(query: string): Promise<Response | ErrorResponse> {
  // The three key autocompleters are independent, so fetch them concurrently.
  const responses = await Promise.all(
    ATTRIBUTE_KIND_ORDER.map((attributeKind) => {
      const autocompleter: Autocompleter = {
        fetch_method: 'rest_autocomplete',
        data: {
          ident: KEY_IDENTS[attributeKind],
          params: {
            context: buildAutocompleteContext(filterModel.value, {
              metricName: props.metricName,
              staticResourceAttributeKeys: props.staticResourceAttributeKeys
            })
          }
        }
      }
      return fetchSuggestions(autocompleter, query)
    })
  )
  const sections: Section[] = []
  ATTRIBUTE_KIND_ORDER.forEach((attributeKind, index) => {
    const response = responses[index]
    if (!response || response instanceof ErrorResponse) {
      return
    }
    // The backend echoes the typed text as a leading (query, query) choice; a real
    // key equal to the query is indistinguishable from the echo and is dropped too,
    // falling into the section-less user entry below (its type stays unresolved).
    const suggestions = flattenSuggestions(response.choices).filter(
      (s: Suggestion) =>
        s.name !== query && (s.name === null || (s.name.length > 0 && s.title.length > 0))
    )
    for (const suggestion of suggestions) {
      if (suggestion.name) {
        cacheKeyKind(suggestion.name, attributeKind)
      }
    }
    if (suggestions.length > 0) {
      sections.push({ title: SECTION_TITLES[attributeKind], suggestions })
    }
  })
  const userEntry: Section[] = query
    ? [{ title: untranslated(''), suggestions: [{ name: query, title: untranslated(query) }] }]
    : []
  return new Response([...userEntry, ...sections])
}

async function queryValueSuggestions(
  condition: Condition,
  query: string
): Promise<Response | ErrorResponse> {
  if (condition.attributeKind === null || !condition.key) {
    return new Response([])
  }
  const autocompleter: Autocompleter = {
    fetch_method: 'rest_autocomplete',
    data: {
      ident: VALUE_IDENTS[condition.attributeKind],
      params: {
        context: buildAutocompleteContext(filterModel.value, {
          metricName: props.metricName,
          staticResourceAttributeKeys: props.staticResourceAttributeKeys,
          attributeKey: condition.key,
          excludeId: condition.id
        })
      }
    }
  }
  const response = await fetchSuggestions(autocompleter, query)
  if (response instanceof ErrorResponse) {
    return response
  }
  return new Response(
    flattenSuggestions(response.choices).filter(
      (s: Suggestion) => s.name === null || (s.name.length > 0 && s.title.length > 0)
    )
  )
}

function resolveAttributeKind(key: string): AttributeKind {
  // A key offered under more than one attribute kind is ambiguous: leave it
  // unresolved so the attribute-kind dropdown opens for the user to choose.
  const kinds = keyKindCache.get(key)
  return kinds?.size === 1 ? [...kinds][0]! : null
}

function clearAttributeSelection(): void {
  filterModel.value = []
}

function hasInvalidAttributes(): boolean {
  return (
    resourceAttributes.value.some((attr) => attr.value.trim() === '') ||
    scopeAttributes.value.some((attr) => attr.value.trim() === '') ||
    dataPointAttributes.value.some((attr) => attr.value.trim() === '')
  )
}

function getValidationMessages(): ValidationMessages {
  const messages: ValidationMessages = []
  if (resourceAttributes.value.some((attr) => attr.value.trim() === '')) {
    messages.push({
      message: 'Resource attribute values cannot be empty.',
      location: ['resource_attributes'],
      replacement_value: resourceAttributes.value
    })
  }
  if (scopeAttributes.value.some((attr) => attr.value.trim() === '')) {
    messages.push({
      message: 'Scope attribute values cannot be empty.',
      location: ['scope_attributes'],
      replacement_value: scopeAttributes.value
    })
  }
  if (dataPointAttributes.value.some((attr) => attr.value.trim() === '')) {
    messages.push({
      message: 'Data point attribute values cannot be empty.',
      location: ['data_point_attributes'],
      replacement_value: dataPointAttributes.value
    })
  }
  return messages
}

defineExpose({ clearAttributeSelection, hasInvalidAttributes, getValidationMessages })
</script>

<template>
  <tr>
    <td class="metric-backend-form-metric-backend-attributes__label-cell">
      {{ _t('Attributes') }}
    </td>
    <td>
      <FormValidation :validation="validationMessages" />
      <component :is="props.indent ? CmkIndent : 'div'">
        <FormAttributeFilter
          v-model="filterModel"
          :allow-or="false"
          :operators="['eq']"
          :query-suggestions="querySuggestions"
          :query-value-suggestions="queryValueSuggestions"
          :resolve-attribute-kind="resolveAttributeKind"
          :aria-label="_t('Attributes')"
        />
      </component>
    </td>
  </tr>
</template>

<style scoped>
.metric-backend-form-metric-backend-attributes__label-cell {
  vertical-align: top;
}
</style>
