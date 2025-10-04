import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

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

const BingTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, searchLanguage, country, ui } = props
  const normalizedKeyword = keyword ?? ''
  const [market, setMarket] = useState(() => resolveDefaultMarket(searchLanguage, country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])

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
          throw new Error(payload?.error || t('platform.bing.error.fetch', 'Unable to fetch Bing suggestions'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.bing.subtitle', 'Autocompletion ({{market}})', { market: payload?.market || market }),
          metric: t('platform.bing.metric.rank', 'Popularity #{{rank}}', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.bing.error.none', 'No Bing suggestions found for this keyword.'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.bing.error.generic', 'Unknown error')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [market, searchLanguage, t]
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
        {t('platform.bing.filters.market', 'Market')}
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
      platformName={t('platform.bing.meta.name', 'Bing')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description={t('platform.bing.description', 'Search optimization insights for Microsoft Bing.')}
      extraFilters={filters}
      results={results}
      placeholder={t('platform.bing.placeholder', 'Which keyword do you want to rank on Bing?')}
      loading={loading}
      error={error}
      emptyState={t('platform.bing.empty', 'Enter a keyword to uncover Bing opportunities.')}
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
      translate={t}
    />
  )
}

export default BingTool
