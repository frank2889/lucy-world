import type { UIState } from '../platforms/types'

type Replacements = Record<string, string | number>

const PLACEHOLDER_PATTERN = /{{\s*([a-zA-Z0-9_.-]+)\s*}}/g

function applyReplacements(template: string, replacements?: Replacements): string {
  if (!replacements) {
    return template
  }
  return template.replace(PLACEHOLDER_PATTERN, (_, token: string) => {
    if (Object.prototype.hasOwnProperty.call(replacements, token)) {
      const value = replacements[token]
      return value === undefined || value === null ? '' : String(value)
    }
    return ''
  })
}

export function createTranslator(ui?: UIState | null) {
  const strings = ui?.strings ?? {}
  return (key: string, replacements?: Replacements): string => {
    // Only use the current language - no fallbacks!
    // If key is missing, return [MISSING: key] to make it visible
    const template = strings[key] ?? `[MISSING: ${key}]`
    return applyReplacements(template, replacements)
  }
}

export type Translator = ReturnType<typeof createTranslator>
