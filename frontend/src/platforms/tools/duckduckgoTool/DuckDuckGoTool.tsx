import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

type DuckDuckGoSuggestion = {
  phrase: string
  snippet?: string | null
  score?: number | null
  type?: string | null
  image?: string | null
}

const DUCKDUCKGO_REGIONS = [
  { code: 'wt-wt', label: 'Wereldwijd' },
  { code: 'us-en', label: 'United States (English)' },
  { code: 'uk-en', label: 'United Kingdom (English)' },
  { code: 'nl-nl', label: 'Nederland (Nederlands)' },
  { code: 'de-de', label: 'Deutschland (Deutsch)' },
  { code: 'fr-fr', label: 'France (Français)' },
  { code: 'es-es', label: 'España (Español)' },
  { code: 'it-it', label: 'Italia (Italiano)' },
  { code: 'jp-jp', label: '日本 (日本語)' },
  { code: 'in-en', label: 'India (English)' },
  { code: 'br-pt', label: 'Brasil (Português)' }
]

const REGION_SET = new Set(DUCKDUCKGO_REGIONS.map((region) => region.code.toLowerCase()))
const FALLBACK_REGION = 'wt-wt'

const resolveDefaultRegion = (language?: string, country?: string) => {
  const lang = (language || '').split('-')[0].toLowerCase()
  const ctry = (country || '').split('-')[0].toLowerCase()
  if (lang && ctry) {
    const candidate = `${ctry}-${lang}`
    if (REGION_SET.has(candidate)) return candidate
  }
  if (lang) {
    for (const region of DUCKDUCKGO_REGIONS) {
      const code = region.code.toLowerCase()
      if (code.endsWith(`-${lang}`) || code.startsWith(`${lang}-`)) return code
    }
  }
  return FALLBACK_REGION
}

const DuckDuckGoTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, searchLanguage, country, ui } = props
  const normalizedKeyword = keyword ?? ''
  const [region, setRegion] = useState(() => resolveDefaultRegion(searchLanguage, country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])
  const regionOptions = useMemo(
    () => DUCKDUCKGO_REGIONS.map((item) => ({
      ...item,
      label: t(`platform.duckduckgo.region.${item.code}`, item.label)
    })),
    [t]
  )

  useEffect(() => {
    setRegion(resolveDefaultRegion(searchLanguage, country))
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
          kl: region,
          lang: (searchLanguage || '').toLowerCase(),
          country: (country || '').toUpperCase()
        })
        const response = await fetch(`/api/platforms/duckduckgo?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.duckduckgo.error.fetch', 'Unable to fetch DuckDuckGo suggestions'))
        }
        const payload = await response.json()
        const suggestions: DuckDuckGoSuggestion[] = Array.isArray(payload?.suggestions)
          ? (payload.suggestions as DuckDuckGoSuggestion[])
          : []
        const mapped: PlatformResultItem[] = suggestions
          .filter((item) => typeof item?.phrase === 'string' && item.phrase.trim().length > 0)
          .map((item, index) => ({
            title: item.phrase,
            subtitle: item.snippet
              || t('platform.duckduckgo.subtitle', 'DuckDuckGo ({{region}})', {
                region: payload?.kl || region
              }),
            metric: typeof item.score === 'number' && Number.isFinite(item.score)
              ? t('platform.duckduckgo.metric.score', 'Relevance score {{score}}', { score: item.score })
              : t('platform.duckduckgo.metric.rank', 'Suggestion #{{rank}}', { rank: index + 1 })
          }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.duckduckgo.error.none', 'No DuckDuckGo suggestions found for this keyword.'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.duckduckgo.error.generic', 'Unknown error')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [region, searchLanguage, country, t]
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
  }, [region, normalizedKeyword, performSearch])

  const filters = useMemo(() => (
    <div className="platform-tool__filters">
      <label htmlFor="duckduckgo-region">
        {t('platform.duckduckgo.filters.region', 'Region')}
        <select
          id="duckduckgo-region"
          value={region}
          onChange={(event) => {
            setRegion(event.target.value)
            hasFetched.current = false
          }}
        >
          {regionOptions.map((item) => (
            <option key={item.code} value={item.code}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  ), [region, regionOptions, t])

  return (
    <PlatformToolLayout
      platformName={t('platform.duckduckgo.meta.name', 'DuckDuckGo')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description={t('platform.duckduckgo.description', 'Discover privacy-friendly queries with DuckDuckGo autocomplete.')}
      extraFilters={filters}
      results={results}
      placeholder={t('platform.duckduckgo.placeholder', 'Which query do you want to explore?')}
      loading={loading}
      error={error}
      emptyState={t('platform.duckduckgo.empty', 'Enter a keyword to see DuckDuckGo suggestions.')}
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
      translate={t}
    />
  )
}

export default DuckDuckGoTool
