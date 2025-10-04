import React, { useCallback, useMemo, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

const GoogleTool: React.FC<PlatformToolProps> = ({ keyword, setKeyword, searchLanguage, country, ui }) => {
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const resolvedLanguage = useMemo(() => {
    return (searchLanguage || ui?.lang || 'en').split('-')[0].toLowerCase()
  }, [searchLanguage, ui?.lang])

  const resolvedCountry = useMemo(() => {
    return (country || '').trim().toUpperCase()
  }, [country])

  const performSearch = useCallback(
    async (term: string) => {
      const query = term.trim()
      if (!query) {
        setResults([])
        setError(null)
        return
      }

      setLoading(true)
      setError(null)

      try {
        const params = new URLSearchParams({
          q: query,
          lang: resolvedLanguage || 'en'
        })
        if (resolvedCountry) {
          params.set('country', resolvedCountry)
        }

        const response = await fetch(`/api/platforms/google?${params.toString()}`)
        const payload = await response.json().catch(() => ({}))

        if (!response.ok) {
          throw new Error(payload?.error || 'Kon Google suggesties niet ophalen')
        }

        const suggestionsRaw = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestionsRaw
          .map((item: any, index: number) => {
            let text: string | null = null
            if (typeof item === 'string') {
              text = item
            } else if (item && typeof item === 'object') {
              text = item.phrase || item.keyword || item.text || null
            }
            if (!text) return null
            const subtitleParts: string[] = []
            if (payload?.metadata?.hl) {
              subtitleParts.push(`Taal: ${(payload.metadata.hl as string).toUpperCase()}`)
            }
            if (payload?.metadata?.gl) {
              subtitleParts.push(`Land: ${payload.metadata.gl}`)
            }
            return {
              title: text,
              subtitle: subtitleParts.length ? subtitleParts.join(' • ') : 'Google suggestie',
              metric: `#${index + 1}`
            }
          })
          .filter(Boolean) as PlatformResultItem[]

        setResults(mapped)
        if (mapped.length === 0) {
          setError('Geen Google suggesties gevonden voor dit zoekwoord.')
        }
      } catch (err: any) {
        setError(err?.message || 'Kon Google suggesties niet ophalen')
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [resolvedLanguage, resolvedCountry]
  )

  const handleSearch = useCallback(
    (term: string) => {
      performSearch(term)
    },
    [performSearch]
  )

  return (
    <PlatformToolLayout
      platformName="Google"
      keyword={keyword || ''}
      onKeywordChange={setKeyword}
      onSearch={handleSearch}
      description="Directe autocomplete-suggesties uit Google Search."
      results={results}
      placeholder="Waar zoeken mensen naar op Google?"
      loading={loading}
      error={error}
      emptyState="Voer een zoekterm in om Google suggesties te zien."
    />
  )
}

export default GoogleTool
