/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */

/** CLDR ordinal categories. `zero` is deliberately excluded, it is a cardinal-only */
export type OrdinalCategory = Exclude<Intl.LDMLPluralRule, 'zero'>

/** The CLDR plural category `Intl.PluralRules` selects for `n` in `locale`. */
function pluralCategory(
  n: number,
  locale: string | null,
  type: Intl.PluralRuleType
): Intl.LDMLPluralRule {
  // Intl needs BCP-47 hyphens (`pt-PT`)
  const bcp47 = (locale ?? 'en').replace('_', '-')
  return new Intl.PluralRules(bcp47, { type }).select(n)
}

/**
 * Pick the correct ordinal wording for a number in a given locale.
 *
 * @param n the number to render an ordinal for
 * @param locale the target language (accepts our underscore locale keys, e.g. `pt_PT`)
 * @param forms per-category phrase builders, one for every ordinal category
 */
export function selectOrdinalForm<T>(
  n: number,
  locale: string | null,
  forms: Record<OrdinalCategory, () => T>
): T {
  const category = pluralCategory(n, locale, 'ordinal')
  // `zero` cannot occur for ordinals, default to `other` just in case
  return forms[category === 'zero' ? 'other' : category]()
}
