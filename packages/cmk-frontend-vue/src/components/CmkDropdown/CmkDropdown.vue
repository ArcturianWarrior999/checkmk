<!--
Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import { PopoverAnchor, PopoverContent, PopoverPortal, PopoverRoot } from 'reka-ui'
import { computed, nextTick, ref, useSlots, useTemplateRef } from 'vue'

import { untranslated } from '@/lib/i18n'
import type { TranslatedString } from '@/lib/i18nString'
import useClickOutside from '@/lib/useClickOutside'
import { useFloatingTarget } from '@/lib/useFloatingTarget'
import { immediateWatch } from '@/lib/watch'

import CmkLoading from '@/components/CmkLoading.vue'
import CmkSuggestions, {
  ErrorResponse,
  NoSelection,
  Selection,
  SelectionWithTitle,
  type Suggestion,
  type SuggestionValue,
  type Suggestions,
  flattenSuggestions
} from '@/components/CmkSuggestions'
import ArrowDown from '@/components/graphics/ArrowDown.vue'
import CmkLabelRequired from '@/components/user-input/CmkLabelRequired.vue'

import CmkInlineValidation from '../user-input/CmkInlineValidation.vue'
import CmkDropdownButton, { type ButtonVariants } from './CmkDropdownButton.vue'
import TruncateText from './TruncateText.vue'

export interface DropdownOption {
  name: string
  title: string
}

const {
  inputHint = untranslated(''),
  noResultsHint = '',
  disabled = false,
  componentId = null,
  noElementsText = untranslated(''),
  required = false,
  width,
  options,
  label,
  formValidation = false,
  floating = false
} = defineProps<{
  options: Suggestions
  inputHint?: TranslatedString
  noResultsHint?: TranslatedString
  disabled?: boolean
  componentId?: string | null
  noElementsText?: TranslatedString
  required?: boolean
  label: TranslatedString
  width?: ButtonVariants['width']
  formValidation?: boolean
  floating?: boolean
}>()

const selectedOptionPublic = defineModel<string | null>({ default: null })

const vClickOutside = useClickOutside()

const floatingTarget = useFloatingTarget()

const buttonLabel = ref<TranslatedString>(inputHint)
const callbackFilteredErrorMessage = ref<string | null>(null)
const callbackFilteredLoading = ref<boolean>(false)
const internallyDisabled = ref<boolean>(false)

const selectedOption = ref<SuggestionValue>(new NoSelection())

immediateWatch(
  () => ({
    newValue: selectedOptionPublic.value,
    newOptions: options
  }),
  async ({ newValue, newOptions }) => {
    callbackFilteredLoading.value = false
    if (newOptions.type === 'callback-filtered' && newValue !== null) {
      internallyDisabled.value = true
      callbackFilteredLoading.value = true
    }
    const currentSelectionState = await getCurrentSelectionState(newOptions, newValue)
    callbackFilteredLoading.value = false
    internallyDisabled.value = false
    // Only update if the selected option hasn't changed again while awaiting
    if (newValue === selectedOptionPublic.value) {
      buttonLabel.value = currentSelectionState.buttonLabel
      selectedOption.value = currentSelectionState.value
    }
  }
)

/**
 * This function might have a performance impact as it might trigger a callback to fetch
 * suggestions. It should only be called when necessary.
 */
async function getCurrentSelectionState(
  options: Suggestions,
  selected: string | null
): Promise<{ value: SuggestionValue; buttonLabel: TranslatedString }> {
  let currentOptions: Suggestion[]
  switch (options.type) {
    case 'filtered':
    case 'fixed': {
      if (options.suggestions.length === 0) {
        return { value: new NoSelection(), buttonLabel: noElementsText || inputHint }
      } else if (selected === null) {
        return { value: new NoSelection(), buttonLabel: inputHint }
      }
      currentOptions = flattenSuggestions(options.suggestions)
      break
    }
    case 'callback-filtered': {
      if (selected === null) {
        return { value: new NoSelection(), buttonLabel: inputHint }
      }
      const result = await options.querySuggestions(selected)

      if (result instanceof ErrorResponse) {
        callbackFilteredErrorMessage.value = result.error
        return { value: new Selection(selected), buttonLabel: untranslated(selected) }
      } else {
        callbackFilteredErrorMessage.value = null
        currentOptions = flattenSuggestions(result.choices)
      }
      break
    }
  }
  if (currentOptions.length === 0) {
    return { value: new NoSelection(), buttonLabel: noElementsText }
  } else {
    const selectedSuggestion = currentOptions.find((s: Suggestion) => s.name === selected)
    if (selectedSuggestion) {
      if (selectedSuggestion.name === null) {
        return {
          value: new NoSelection(),
          buttonLabel: inputHint
        }
      }
      return {
        value: new SelectionWithTitle(selectedSuggestion.name, selectedSuggestion.title),
        buttonLabel: selectedSuggestion.title
      }
    } else {
      return { value: new Selection(selected), buttonLabel: untranslated(selected) }
    }
  }
}

const canOpenDropdown = computed(() => {
  if (internallyDisabled.value === true) {
    return false
  }
  if (options.type === 'filtered' || options.type === 'fixed') {
    if (!noResultsHint && options.suggestions.length === 0) {
      return false
    }
    return true
  }
  return true // assume something is available via callback/backend
  // we don't know the number of available suggestions, as this is handled by CmkSuggestions,
  // so we just assume we have something to display, although maybe, we don't have.
})

const suggestionsShown = ref(false)
const suggestionsRef = ref<InstanceType<typeof CmkSuggestions> | null>(null)
const comboboxButtonRef =
  useTemplateRef<InstanceType<typeof CmkDropdownButton>>('comboboxButtonRef')
const rootRef = ref<HTMLElement | null>(null)

// Swallow the click-outside fired by the in-flight bubble when open() is
// called from a sibling's click handler.
const suppressNextClickOutside = ref(false)

defineExpose({
  open: () => {
    if (suggestionsShown.value) {
      return
    }
    suppressNextClickOutside.value = true
    showSuggestions()
    // We use setTimeout here instead of nextTick because
    // the reset must outlive the entire click dispatch.
    setTimeout(() => {
      suppressNextClickOutside.value = false
    }, 0)
  },
  focus: () => {
    comboboxButtonRef.value?.focus()
  },
  isOpen: () => suggestionsShown.value
})

function showSuggestions(): void {
  if (!disabled && canOpenDropdown.value) {
    suggestionsShown.value = !suggestionsShown.value
    if (!suggestionsShown.value) {
      return
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    nextTick(async () => {
      if (suggestionsRef.value) {
        if (!floating) {
          const suggestionsRect = suggestionsRef.value.$el.getBoundingClientRect()
          if (window.innerHeight - suggestionsRect.bottom < suggestionsRect.height) {
            suggestionsRef.value.$el.style.bottom = `calc(2 * var(--spacing))`
          } else {
            suggestionsRef.value.$el.style.removeProperty('bottom')
          }
        }
        await suggestionsRef.value.focus()
      }
    })
  }
}

function hideSuggestions(): void {
  suggestionsShown.value = false
  comboboxButtonRef.value?.focus()
}

function onClickOutside(): void {
  if (floating) {
    return
  }
  if (suppressNextClickOutside.value) {
    return
  }
  if (suggestionsShown.value) {
    suggestionsShown.value = false
  }
}

function onFloatingOpenChange(open: boolean): void {
  if (!open) {
    suggestionsShown.value = false
  }
}

function onFloatingInteractOutside(event: Event): void {
  const originalEvent = (event as CustomEvent<{ originalEvent: Event }>).detail?.originalEvent
  if (originalEvent?.target instanceof Node && rootRef.value?.contains(originalEvent.target)) {
    event.preventDefault()
  }
}

function handleUpdate(selected: Suggestion | null): void {
  // Only write the model; the internal state syncs back from the watch, so a
  // controlled parent that keeps its value (e.g. an add-control pinned to
  // null) keeps the dropdown unselected and repeated picks emit again.
  selectedOptionPublic.value = selected === null || selected.name === null ? null : selected.name
  callbackFilteredErrorMessage.value = null
  hideSuggestions()
}

const slots = useSlots()
const group = computed<ButtonVariants['group']>(() => {
  const hasButtonsStart = !!slots['buttons-start']
  const hasButtonsEnd = !!slots['buttons-end']
  if (hasButtonsStart && hasButtonsEnd) {
    return 'center'
  } else if (hasButtonsStart) {
    return 'end'
  } else if (hasButtonsEnd) {
    return 'start'
  } else {
    return 'no'
  }
})
</script>

<template>
  <div
    ref="rootRef"
    v-click-outside="onClickOutside"
    class="cmk-dropdown"
    :class="{ 'cmk-dropdown__fill': width === 'fill' }"
  >
    <CmkInlineValidation
      v-if="callbackFilteredErrorMessage !== null"
      :validation="[callbackFilteredErrorMessage]"
    ></CmkInlineValidation>
    <slot name="buttons-start"></slot>
    <CmkDropdownButton
      v-bind="componentId!! ? { id: componentId } : {}"
      ref="comboboxButtonRef"
      :aria-label="label"
      :aria-expanded="suggestionsShown"
      :disabled="disabled"
      :multiple-choices-available="canOpenDropdown"
      :value-is-selected="!(selectedOption instanceof NoSelection)"
      :group="group"
      :width="width"
      :class="{ 'cmk-dropdown__validation-error': formValidation }"
      @click="showSuggestions"
    >
      <span v-if="!!slots['button-prefix']" class="cmk-dropdown--button-prefix">
        <slot name="button-prefix"></slot>
      </span>
      <template v-if="callbackFilteredLoading">
        <CmkLoading />
      </template>
      <span v-if="!callbackFilteredLoading && buttonLabel" style="display: contents"
        ><TruncateText :text="buttonLabel" /></span
      ><CmkLabelRequired
        :show="required && selectedOption instanceof NoSelection"
        :space="'before'" />
      <template v-if="!callbackFilteredLoading && !buttonLabel">&nbsp;</template>
      <ArrowDown
        class="cmk-dropdown--arrow"
        :class="{ rotated: suggestionsShown, disabled: disabled || !canOpenDropdown }"
        aria-hidden="true"
    /></CmkDropdownButton>
    <slot name="buttons-end"></slot>
    <CmkSuggestions
      v-if="!!suggestionsShown && !floating"
      ref="suggestionsRef"
      role="option"
      :suggestions="options"
      :selected-suggestion="selectedOption"
      :no-results-hint="noResultsHint"
      @request-close-suggestions="hideSuggestions"
      @select-suggestion="handleUpdate"
    />
    <PopoverRoot
      v-if="floating"
      :open="!!suggestionsShown"
      :modal="false"
      @update:open="onFloatingOpenChange"
    >
      <PopoverAnchor v-bind="rootRef ? { reference: rootRef } : {}" class="cmk-dropdown__anchor" />
      <PopoverPortal :to="floatingTarget ?? 'body'">
        <PopoverContent
          side="bottom"
          align="start"
          class="cmk-dropdown__floating"
          :style="{ position: 'relative', zIndex: 'var(--z-index-dropdown-offset)' }"
          @open-auto-focus.prevent
          @close-auto-focus.prevent
          @interact-outside="onFloatingInteractOutside"
        >
          <CmkSuggestions
            ref="suggestionsRef"
            role="option"
            :suggestions="options"
            :selected-suggestion="selectedOption"
            :no-results-hint="noResultsHint"
            @request-close-suggestions="hideSuggestions"
            @select-suggestion="handleUpdate"
          />
        </PopoverContent>
      </PopoverPortal>
    </PopoverRoot>
  </div>
</template>

<style scoped>
.cmk-dropdown {
  display: inline-block;
  position: relative;
  white-space: nowrap;
  align-self: flex-start;

  .cmk-dropdown--button-prefix {
    display: flex;
    align-items: center;
    height: 1lh;
  }

  .cmk-dropdown--arrow {
    flex-shrink: 0;
    width: 0.7em;
    color: var(--dropdown-arrow-color);
    margin-left: auto;
    padding: 0 4px;
    margin-top: -1px;

    /* stylelint-disable-next-line checkmk/vue-bem-naming-convention */
    &.rotated {
      transform: rotate(180deg);
    }

    /* stylelint-disable-next-line checkmk/vue-bem-naming-convention */
    &.disabled {
      opacity: 0.4;
    }
  }
}

.cmk-dropdown__fill {
  width: 100%;
}

.cmk-dropdown__validation-error {
  border: 1px solid var(--inline-error-border-color);
}

.cmk-dropdown__anchor {
  display: contents;
}

/* stylelint-disable-next-line checkmk/vue-bem-naming-convention */
.cmk-dropdown__floating .cmk-suggestions {
  position: static;
  min-width: var(--reka-popper-anchor-width);
}
</style>
