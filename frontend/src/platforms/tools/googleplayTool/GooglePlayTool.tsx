import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import { createTranslator } from '../../../i18n/translate'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

const GOOGLE_PLAY_REGIONS = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'ES', 'IT', 'NL', 'BR', 'IN'] as const

const resolveDefaultRegion = (country?: string) => {
  const normalized = (country || '').toUpperCase()
  const match = GOOGLE_PLAY_REGIONS.find((code) => code === normalized)
  return match ?? 'US'
}

const GooglePlayTool: React.FC<PlatformToolProps> = (props) => {
  const {
    keyword,
    setKeyword,
    searchLanguage,
    country,
    ui,
    
    locationControls,
    onGlobalSearch,
    globalLoading,
    getCountryName
  } = props
  const normalizedKeyword = keyword ?? ''
  const [region, setRegion] = useState<string>(() => resolveDefaultRegion(country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)

  const t = useMemo(() => createTranslator(ui), [ui])

  const regionOptions = useMemo(
    () => [
      { code: 'US', label: getCountryName?.('US') ?? t('platform.googlePlay.regions.US') },
      { code: 'GB', label: getCountryName?.('GB') ?? t('platform.googlePlay.regions.GB') },
      { code: 'CA', label: getCountryName?.('CA') ?? t('platform.googlePlay.regions.CA') },
      { code: 'AU', label: getCountryName?.('AU') ?? t('platform.googlePlay.regions.AU') },
      { code: 'DE', label: getCountryName?.('DE') ?? t('platform.googlePlay.regions.DE') },
      { code: 'FR', label: getCountryName?.('FR') ?? t('platform.googlePlay.regions.FR') },
      { code: 'ES', label: getCountryName?.('ES') ?? t('platform.googlePlay.regions.ES') },
      { code: 'IT', label: getCountryName?.('IT') ?? t('platform.googlePlay.regions.IT') },
      { code: 'NL', label: getCountryName?.('NL') ?? t('platform.googlePlay.regions.NL') },
      { code: 'BR', label: getCountryName?.('BR') ?? t('platform.googlePlay.regions.BR') },
      { code: 'IN', label: getCountryName?.('IN') ?? t('platform.googlePlay.regions.IN') }
    ],
    [getCountryName, t]
  )

  useEffect(() => {
    setRegion(resolveDefaultRegion(country))
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
          country: region,
          lang: (searchLanguage || '').toLowerCase(),
          limit: '10'
        })
        const response = await fetch(`/api/platforms/googleplay?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.googlePlay.errors.unknownResponse'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.googlePlay.results.subtitle', {
            country: (payload?.country?.toUpperCase() || region) ?? region
          }),
          metric: t('platform.googlePlay.results.rank', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.googlePlay.errors.noneFound'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.googlePlay.errors.generic')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [region, searchLanguage, t]
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
  }, [region, searchLanguage, normalizedKeyword, performSearch])

  const filters = (
    <div className="platform-tool__filters">
      <label htmlFor="google-play-region">
        {t('platform.googlePlay.filters.region')}
        <select
          id="google-play-region"
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
  )

  return (
    <PlatformToolLayout
      platformName={t('platform.googlePlay.meta.name')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description={t('platform.googlePlay.description')}
      extraFilters={filters}
      results={results}
      placeholder={t('platform.googlePlay.form.placeholder')}
      loading={loading}
      error={error}
      emptyState={t('platform.googlePlay.emptyState')}
      controls={locationControls}
      onGlobalSearch={onGlobalSearch}
      globalLoading={globalLoading}
      translate={t}
    />
  )
}

export default GooglePlayTool
