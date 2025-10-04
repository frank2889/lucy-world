import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

const BING_MARKETS = [
  { code: 'en-US', label: 'United States (English)' },
  { code: 'en-GB', label: 'United Kingdom (English)' },
  { code: 'en-AU', label: 'Australia (English)' },
  { code: 'en-CA', label: 'Canada (English)' },
  { code: 'fr-FR', label: 'France (Français)' },
  { code: 'fr-CA', label: 'Canada (Français)' },
  { code: 'de-DE', label: 'Deutschland (Deutsch)' },
  { code: 'es-ES', label: 'España (Español)' },
  { code: 'es-MX', label: 'México (Español)' },
  { code: 'nl-NL', label: 'Nederland (Nederlands)' },
  { code: 'it-IT', label: 'Italia (Italiano)' },
  { code: 'pt-BR', label: 'Brasil (Português)' },
  { code: 'ja-JP', label: '日本 (日本語)' }
]

const fallbackMarket = 'en-US'

const resolveDefaultMarket = (language?: string, country?: string) => {
  const normalizedLang = (language || '').toLowerCase()
  const normalizedCountry = (country || '').toUpperCase()
  const candidate = `${normalizedLang}-${normalizedCountry}`.toLowerCase()
  if (BING_MARKETS.some((m) => m.code.toLowerCase() === candidate && normalizedLang && normalizedCountry)) {
    return candidate
  }
  // Try matching just language prefix
  if (normalizedLang) {
    const langMatch = BING_MARKETS.find((m) => m.code.toLowerCase().startsWith(`${normalizedLang}-`))
    if (langMatch) return langMatch.code
  }
  return fallbackMarket
}

const BingTool: React.FC<PlatformToolProps> = ({ keyword, setKeyword, searchLanguage, country }) => {
  const normalizedKeyword = keyword ?? ''
  const [market, setMarket] = useState(() => resolveDefaultMarket(searchLanguage, country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)

  useEffect(() => {
    setMarket(resolveDefaultMarket(searchLanguage, country))
  }, [searchLanguage, country])

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
          mkt: market,
          lang: (searchLanguage || '').toLowerCase()
        })
        const response = await fetch(`/api/platforms/bing?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || 'Onbekende Bing fout')
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: `Autocompletion (${payload?.market || market})`,
          metric: `Populariteit #${index + 1}`
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError('Geen Bing suggesties gevonden voor dit zoekwoord.')
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Onbekende fout'
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [market, searchLanguage]
  )

  useEffect(() => {
    if (!normalizedKeyword.trim()) {
      setResults([])
      setError(null)
      hasFetched.current = false
      return
    }
    if (hasFetched.current) return
    hasFetched.current = true
    void performSearch(normalizedKeyword)
  }, [normalizedKeyword, performSearch])

  useEffect(() => {
    if (!normalizedKeyword.trim()) return
    if (!hasFetched.current) return
    void performSearch(normalizedKeyword)
  }, [market, normalizedKeyword, performSearch])

  const filters = (
    <div className="platform-tool__filters">
      <label htmlFor="bing-market">
        Markt
        <select
          id="bing-market"
          value={market}
          onChange={(event) => {
            setMarket(event.target.value)
            hasFetched.current = false
          }}
        >
          {BING_MARKETS.map((item) => (
            <option key={item.code} value={item.code}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  )

  return (
    <PlatformToolLayout
      platformName="Bing"
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description="Zoekmachine optimalisatie voor Microsoft Bing."
      extraFilters={filters}
      results={results}
      placeholder="Welke zoekterm wil je in Bing ranken?"
      loading={loading}
      error={error}
      emptyState="Voer een zoekwoord in om Bing kansen te zien."
    />
  )
}

export default BingTool
