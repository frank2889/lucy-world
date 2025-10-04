import React, { useCallback, useMemo, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

const YouTubeTool: React.FC<PlatformToolProps> = ({ keyword, setKeyword, searchLanguage, ui }) => {
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const resolvedLanguage = useMemo(() => {
    return (searchLanguage || ui?.lang || 'en').split('-')[0].toLowerCase()
  }, [searchLanguage, ui?.lang])

  const performSearch = useCallback(async (term: string) => {
    const trimmed = term.trim()
    if (!trimmed) {
      setResults([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ q: trimmed, lang: resolvedLanguage })
      const response = await fetch(`/api/platforms/youtube?${params.toString()}`)
      const payload = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(payload?.error || 'Kon YouTube suggesties niet ophalen')
      }
      const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
      const mapped: PlatformResultItem[] = suggestions.map((suggestion) => ({
        title: suggestion,
        subtitle: 'YouTube zoek suggestie',
        metric: payload?.metadata?.approx_volume ? `Populariteit: ${payload.metadata.approx_volume}` : undefined
      }))
      setResults(mapped)
    } catch (err: any) {
      setError(err?.message || 'Kon YouTube suggesties niet ophalen')
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [resolvedLanguage])

  const handleSearch = useCallback((term: string) => {
    performSearch(term)
  }, [performSearch])

  return (
    <PlatformToolLayout
      platformName="YouTube"
      keyword={keyword || ''}
      onKeywordChange={setKeyword}
      onSearch={handleSearch}
      description="Video zoekwoorden gericht op YouTube content."
      results={results}
      placeholder="Waar wil je video-content over maken?"
      emptyState="Voer een zoekwoord in om YouTube suggesties te ontvangen."
      loading={loading}
      error={error}
    />
  )
}

export default YouTubeTool
