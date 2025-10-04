import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

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

const YandexTool: React.FC<PlatformToolProps> = ({ keyword, setKeyword, searchLanguage, country }) => {
  const normalizedKeyword = keyword ?? ''
  const [region, setRegion] = useState(() => defaultRegionForCountry(country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)

  const availableRegions = useMemo(() => {
    const uniq = new Map<string, { code: string; label: string }>()
    for (const item of YANDEX_REGIONS) {
      if (!uniq.has(item.code)) {
        uniq.set(item.code, { code: item.code, label: item.label })
      }
    }
    return Array.from(uniq.values())
  }, [])

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
          throw new Error(payload?.error || 'Onbekende Yandex fout')
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: `Запрос (${payload?.region || region || 'все регионы'})`,
          metric: `Популярность #${index + 1}`
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError('Geen Yandex suggesties gevonden voor dit zoekwoord.')
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Onbekende fout'
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [region, searchLanguage]
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
        Regio
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
      platformName="Yandex"
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description="Lokale zoektermen voor Yandex ecosysteem."
      extraFilters={filters}
      results={results}
      placeholder="Welke Russische zoekterm onderzoek je?"
      loading={loading}
      error={error}
      emptyState="Voer een zoekwoord in voor Yandex inzichten."
    />
  )
}

export default YandexTool
