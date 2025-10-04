import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import { createTranslator } from '../../../i18n/translate'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

const GOOGLE_PLAY_REGIONS = [
  { code: 'US', label: 'United States' },
  { code: 'GB', label: 'United Kingdom' },
  { code: 'CA', label: 'Canada' },
  { code: 'AU', label: 'Australia' },
  { code: 'DE', label: 'Germany' },
  { code: 'FR', label: 'France' },
  { code: 'ES', label: 'Spain' },
  { code: 'IT', label: 'Italy' },
  { code: 'NL', label: 'Netherlands' },
  { code: 'BR', label: 'Brazil' },
  { code: 'IN', label: 'India' }
]

const resolveDefaultRegion = (country?: string) => {
  const normalized = (country || '').toUpperCase()
  const match = GOOGLE_PLAY_REGIONS.find((item) => item.code === normalized)
  return match?.code ?? 'US'
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
  const [region, setRegion] = useState(() => resolveDefaultRegion(country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)

  const t = useMemo(() => createTranslator(ui), [ui])

  const regionOptions = useMemo(
    () =>
      GOOGLE_PLAY_REGIONS.map((item) => ({
        code: item.code,
        label: getCountryName?.(item.code) ?? t(`platform.googlePlay.regions.${item.code}`, item.label)
      })),
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
          throw new Error(payload?.error || t('platform.googlePlay.errors.unknownResponse', 'Unknown Google Play error'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.googlePlay.results.subtitle', 'Search suggestion ({{country}})', {
            country: (payload?.country?.toUpperCase() || region) ?? region
          }),
          metric: t('platform.googlePlay.results.rank', 'Popularity #{{rank}}', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.googlePlay.errors.noneFound', 'No Google Play suggestions found for this keyword.'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.googlePlay.errors.generic', 'Unknown error')
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
  {t('platform.googlePlay.filters.region', 'Region')}
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
  platformName={t('platform.googlePlay.meta.name', 'Google Play')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
  description={t('platform.googlePlay.description', 'ASO for Android apps in Google Play.')}
      extraFilters={filters}
      results={results}
  placeholder={t('platform.googlePlay.form.placeholder', 'Which Android keyword are you researching?')}
      loading={loading}
      error={error}
  emptyState={t('platform.googlePlay.emptyState', 'Enter a keyword to see Google Play opportunities.')}
      controls={locationControls}
      onGlobalSearch={onGlobalSearch}
      globalLoading={globalLoading}
      translate={t}
    />
  )
}

export default GooglePlayTool
