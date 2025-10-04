import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const YANDEX_REGIONS = [
  { code: '213', label: 'Россия — Москва', countries: ['RU'] },
  { code: '2', label: 'Россия — Санкт-Петербург', countries: ['RU'] },
  { code: '187', label: 'Україна', countries: ['UA'] },
  { code: '157', label: 'Беларусь', countries: ['BY'] },
  { code: '163', label: 'Қазақстан', countries: ['KZ'] },
  { code: '225', label: 'Россия — вся страна', countries: ['RU'] },
  { code: '0', label: 'Все регионы', countries: [] }
]

const defaultRegionForCountry = (country?: string) => {
  const normalized = (country || '').toUpperCase()
  const match = YANDEX_REGIONS.find((item) => item.countries.includes(normalized))
  if (match) return match.code
  return '225'
}

const YandexTool: React.FC<PlatformToolProps> = (props) => {
  const {
    keyword,
    setKeyword,
    searchLanguage,
    country,
    ui,
    locationControls,
    onGlobalSearch,
    globalLoading
  } = props
  const normalizedKeyword = keyword ?? ''
  const [region, setRegion] = useState(() => defaultRegionForCountry(country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])

  const availableRegions = useMemo(() => {
    const uniq = new Map<string, { code: string; label: string }>()
    for (const item of YANDEX_REGIONS) {
      if (!uniq.has(item.code)) {
        uniq.set(item.code, {
          code: item.code,
          label: t(`platform.yandex.regions.${item.code}`, item.label)
        })
      }
    }
    return Array.from(uniq.values())
  }, [t])

  useEffect(() => {
    setRegion(defaultRegionForCountry(country))
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
          lr: region
        })
        if (searchLanguage) {
          params.set('lang', searchLanguage.toLowerCase())
        }
        const response = await fetch(`/api/platforms/yandex?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.yandex.errors.fetch', 'Unable to fetch Yandex suggestions'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.yandex.results.subtitle', 'Query ({{region}})', {
            region: payload?.region || region || 'all'
          }),
          metric: t('platform.yandex.results.rank', 'Popularity #{{rank}}', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.yandex.errors.noneFound', 'No Yandex suggestions found for this keyword.'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.yandex.errors.generic', 'Unknown error')
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
      <label htmlFor="yandex-region">
        {t('platform.yandex.filters.region', 'Region')}
        <select
          id="yandex-region"
          value={region}
          onChange={(event) => {
            setRegion(event.target.value)
            hasFetched.current = false
          }}
        >
          {availableRegions.map((item) => (
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
      platformName={t('platform.yandex.meta.name', 'Yandex')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description={t('platform.yandex.description', 'Local search terms for the Yandex ecosystem.')}
      extraFilters={filters}
      results={results}
      placeholder={t('platform.yandex.placeholder', 'Which Russian search term are you researching?')}
      loading={loading}
      error={error}
      emptyState={t('platform.yandex.emptyState', 'Enter a keyword for Yandex insights.')}
      controls={locationControls}
      onGlobalSearch={onGlobalSearch}
      globalLoading={globalLoading}
      translate={t}
    />
  )
}

export default YandexTool
