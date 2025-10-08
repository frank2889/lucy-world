import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const YANDEX_REGIONS: Array<{ code: string; labelKey: string; countries: string[] }> = [
  { code: '213', labelKey: 'platform.yandex.regions.213', countries: ['RU'] },
  { code: '2', labelKey: 'platform.yandex.regions.2', countries: ['RU'] },
  { code: '187', labelKey: 'platform.yandex.regions.187', countries: ['UA'] },
  { code: '157', labelKey: 'platform.yandex.regions.157', countries: ['BY'] },
  { code: '163', labelKey: 'platform.yandex.regions.163', countries: ['KZ'] },
  { code: '225', labelKey: 'platform.yandex.regions.225', countries: ['RU'] },
  { code: '0', labelKey: 'platform.yandex.regions.0', countries: [] }
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
  const [region, setRegion] = useState<string>(() => defaultRegionForCountry(country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])

  const translateRegionLabel = useCallback(
    (code: string) => {
      switch (code) {
        case '213':
          return t('platform.yandex.regions.213')
        case '2':
          return t('platform.yandex.regions.2')
        case '187':
          return t('platform.yandex.regions.187')
        case '157':
          return t('platform.yandex.regions.157')
        case '163':
          return t('platform.yandex.regions.163')
        case '225':
          return t('platform.yandex.regions.225')
        case '0':
        default:
          return t('platform.yandex.regions.0')
      }
    },
    [t]
  )

  const availableRegions = useMemo(
    () =>
      YANDEX_REGIONS.map((item) => ({
        code: item.code,
        label: translateRegionLabel(item.code)
      })),
    [translateRegionLabel]
  )

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
          throw new Error(payload?.error || t('platform.yandex.errors.fetch'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.yandex.results.subtitle', {
            region: payload?.region || region || 'all'
          }),
          metric: t('platform.yandex.results.rank', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.yandex.errors.noneFound'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.yandex.errors.generic')
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
        {t('platform.yandex.filters.region')}
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
      platformName={t('platform.yandex.meta.name')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description={t('platform.yandex.description')}
      extraFilters={filters}
      results={results}
      placeholder={t('platform.yandex.placeholder')}
      loading={loading}
      error={error}
      emptyState={t('platform.yandex.emptyState')}
      controls={locationControls}
      onGlobalSearch={onGlobalSearch}
      globalLoading={globalLoading}
      translate={t}
    />
  )
}

export default YandexTool
