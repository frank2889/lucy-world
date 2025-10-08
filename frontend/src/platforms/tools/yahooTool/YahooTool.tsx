import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const LIMIT_OPTIONS = [5, 10, 15, 20]

const resolveDefaultLimit = (raw?: string) => {
  const parsed = Number(raw)
  if (!Number.isFinite(parsed)) return 10
  return Math.min(Math.max(Math.round(parsed), 1), 20)
}

const YahooTool: React.FC<PlatformToolProps> = (props) => {
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
  const [limit, setLimit] = useState(() => resolveDefaultLimit(undefined))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])

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
          lang: (searchLanguage || '').toLowerCase(),
          country: (country || '').toUpperCase(),
          limit: String(limit)
        })
        const response = await fetch(`/api/platforms/yahoo?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.yahoo.errors.fetch'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.yahoo.results.subtitle', {
            country: payload?.country || country || 'global'
          }),
          metric: t('platform.yahoo.results.rank', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.yahoo.errors.noneFound'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.yahoo.errors.generic')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [limit, searchLanguage, country, t]
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
  }, [limit, normalizedKeyword, performSearch])

  const filters = useMemo(() => (
    <div className="platform-tool__filters">
      <label htmlFor="yahoo-limit">
  {t('platform.yahoo.filters.limit')}
        <select
          id="yahoo-limit"
          value={limit}
          onChange={(event) => {
            setLimit(Number(event.target.value))
            hasFetched.current = false
          }}
        >
          {LIMIT_OPTIONS.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>
    </div>
  ), [limit, t])

  return (
    <PlatformToolLayout
  platformName={t('platform.yahoo.meta.name')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
  description={t('platform.yahoo.description')}
      extraFilters={filters}
      results={results}
  placeholder={t('platform.yahoo.placeholder')}
      loading={loading}
      error={error}
  emptyState={t('platform.yahoo.emptyState')}
      controls={locationControls}
      onGlobalSearch={onGlobalSearch}
      globalLoading={globalLoading}
      translate={t}
    />
  )
}

export default YahooTool
