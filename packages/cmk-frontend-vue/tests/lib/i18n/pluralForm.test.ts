/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { selectOrdinalForm } from '@/lib/i18n/pluralForm'

/** Resolve the CLDR ordinal category chosen for a number in a locale. */
function categoryOf(n: number, locale: string | null): string {
  return selectOrdinalForm(n, locale, {
    one: () => 'one',
    two: () => 'two',
    few: () => 'few',
    many: () => 'many',
    other: () => 'other'
  })
}

test('selects English ordinal categories, including the teens exception', () => {
  expect(categoryOf(1, 'en')).toBe('one')
  expect(categoryOf(2, 'en')).toBe('two')
  expect(categoryOf(3, 'en')).toBe('few')
  expect(categoryOf(4, 'en')).toBe('other')
  expect(categoryOf(11, 'en')).toBe('other')
  expect(categoryOf(12, 'en')).toBe('other')
  expect(categoryOf(13, 'en')).toBe('other')
  expect(categoryOf(21, 'en')).toBe('one')
})

test('collapses to "other" for languages without ordinal variation', () => {
  for (const n of [1, 2, 3, 8, 95]) {
    expect(categoryOf(n, 'de')).toBe('other')
    expect(categoryOf(n, 'ja')).toBe('other')
    expect(categoryOf(n, 'es')).toBe('other')
  }
})

test('selects French/Romanian ordinal categories (1 is special, the rest are "other")', () => {
  expect(categoryOf(1, 'fr')).toBe('one')
  expect(categoryOf(2, 'fr')).toBe('other')
  expect(categoryOf(1, 'ro')).toBe('one')
  expect(categoryOf(95, 'ro')).toBe('other')
})

test('selects the Italian "many" ordinal category (8, 11, 80, 800)', () => {
  expect(categoryOf(8, 'it')).toBe('many')
  expect(categoryOf(11, 'it')).toBe('many')
  expect(categoryOf(80, 'it')).toBe('many')
  expect(categoryOf(2, 'it')).toBe('other')
  expect(categoryOf(95, 'it')).toBe('other')
})

test('normalizes underscore locale keys and defaults null to English', () => {
  expect(categoryOf(1, 'pt_PT')).toBe('other') // Portuguese ordinals use only "other"
  expect(categoryOf(1, null)).toBe('one') // English
})

test('invokes only the selected form', () => {
  const forms = {
    one: vi.fn(() => 'one'),
    two: vi.fn(() => 'two'),
    few: vi.fn(() => 'few'),
    many: vi.fn(() => 'many'),
    other: vi.fn(() => 'other')
  }
  selectOrdinalForm(1, 'en', forms)
  expect(forms.one).toHaveBeenCalledOnce()
  expect(forms.two).not.toHaveBeenCalled()
  expect(forms.few).not.toHaveBeenCalled()
  expect(forms.many).not.toHaveBeenCalled()
  expect(forms.other).not.toHaveBeenCalled()
})
