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

export function createTranslator(ui?: UIState | null, fallbackUi?: UIState | null) {
  const primaryStrings = ui?.strings ?? {}
  const fallbackStrings = fallbackUi?.strings ?? {}
  return (key: string, replacements?: Replacements): string => {
    const template = primaryStrings[key] ?? fallbackStrings[key] ?? key
    return applyReplacements(template, replacements)
  }
}

export type Translator = ReturnType<typeof createTranslator>
