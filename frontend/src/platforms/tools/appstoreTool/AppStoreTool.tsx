import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const APP_STORE_COUNTRIES = [
  { code: 'US', label: 'United States' },
  { code: 'GB', label: 'United Kingdom' },
  { code: 'CA', label: 'Canada' },
  { code: 'AU', label: 'Australia' },
  { code: 'DE', label: 'Germany' },
  { code: 'FR', label: 'France' },
  { code: 'ES', label: 'Spain' },
  { code: 'IT', label: 'Italy' },
  { code: 'NL', label: 'Netherlands' },
  { code: 'BE', label: 'Belgium' },
  { code: 'JP', label: 'Japan' }
]

const resolveDefaultStore = (country?: string) => {
  const normalized = (country || '').toUpperCase()
  const match = APP_STORE_COUNTRIES.find((item) => item.code === normalized)
  return match?.code ?? 'US'
}

type ITunesApp = {
  trackName?: string
  artistName?: string
  primaryGenreName?: string
  averageUserRating?: number
  userRatingCount?: number
  formattedPrice?: string
  price?: number
  currency?: string
}

const AppStoreTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, country, ui } = props
  const normalizedKeyword = keyword ?? ''
  const [store, setStore] = useState(() => resolveDefaultStore(country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])

  const storeOptions = useMemo(() => APP_STORE_COUNTRIES, [])

  useEffect(() => {
    setStore(resolveDefaultStore(country))
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
          country: store,
          limit: '15'
        })
        const response = await fetch(`/api/platforms/appstore?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.appstore.error.fetch'))
        }
        const payload = await response.json()
        const apps: ITunesApp[] = Array.isArray(payload?.results) ? payload.results : []
        const mapped: PlatformResultItem[] = apps.map((app, index) => {
          const title = app.trackName || query
          const subtitleParts = [app.artistName, app.primaryGenreName].filter(Boolean)
          const rating = typeof app.averageUserRating === 'number'
            ? `${app.averageUserRating.toFixed(1)}★${app.userRatingCount ? ` (${app.userRatingCount.toLocaleString()})` : ''}`
            : null
          const price = app.formattedPrice
            || (typeof app.price === 'number'
              ? (app.price === 0
                ? t('platform.appstore.price.included')
                : `${app.price} ${app.currency || ''}`)
              : null)
          const metricParts = [rating, price].filter(Boolean)
          return {
            title,
            subtitle: subtitleParts.join(' • ') || undefined,
            metric: metricParts.join(' • ') || t('platform.appstore.metric.rank', { rank: index + 1 })
          }
        })
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.appstore.error.none'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.appstore.error.generic')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [store, t]
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
  }, [store, normalizedKeyword, performSearch])

  const filters = (
    <div className="platform-tool__filters">
      <label htmlFor="appstore-country">
  {t('platform.appstore.filters.store')}
        <select
          id="appstore-country"
          value={store}
          onChange={(event) => {
            setStore(event.target.value)
            hasFetched.current = false
          }}
        >
          {storeOptions.map((item) => (
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
  platformName={t('platform.appstore.meta.name')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
  description={t('platform.appstore.description')}
      extraFilters={filters}
      results={results}
  placeholder={t('platform.appstore.placeholder')}
      loading={loading}
      error={error}
  emptyState={t('platform.appstore.empty')}
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
      translate={t}
    />
  )
}

export default AppStoreTool
