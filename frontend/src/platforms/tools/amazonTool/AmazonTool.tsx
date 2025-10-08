import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import { AMAZON_MARKETPLACES } from '../../data/amazonMarketplaces'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const MARKETPLACES = AMAZON_MARKETPLACES

const AmazonTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, country, ui } = props
  const normalizedKeyword = keyword ?? ''
  const [marketplace, setMarketplace] = useState(() => {
    const preferred = (country ?? '').toUpperCase()
    return MARKETPLACES.some((m) => m.code === preferred) ? preferred : 'US'
  })
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const initialFetchRef = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])

  const selectedMarketplace = useMemo(() => {
    return MARKETPLACES.find((m) => m.code === marketplace) ?? MARKETPLACES[0]
  }, [marketplace])

  const performSearch = useCallback(
    async (term: string) => {
      const query = term.trim()
      if (!query) {
        setResults([])
        return
      }
      setLoading(true)
      setError(null)
      try {
        const params = new URLSearchParams({
          q: query,
          country: selectedMarketplace.code,
          alias: 'aps'
        })
        const response = await fetch(`/api/platforms/amazon?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.amazon.error.fetch'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((suggestion, index) => ({
          title: suggestion,
          subtitle: t('platform.amazon.subtitle', {
            marketplace: selectedMarketplace.label
          }),
          metric: t('platform.amazon.metric.rank', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.amazon.error.none'))
        }
      } catch (fetchError) {
        const message = fetchError instanceof Error ? fetchError.message : t('platform.amazon.error.generic')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [selectedMarketplace.code, selectedMarketplace.label, t]
  )

  useEffect(() => {
    if (initialFetchRef.current) return
    if (!normalizedKeyword.trim()) return
    initialFetchRef.current = true
    void performSearch(normalizedKeyword)
  }, [normalizedKeyword, performSearch])

  useEffect(() => {
    if (normalizedKeyword.trim()) return
    setResults([])
    setError(null)
    initialFetchRef.current = false
  }, [normalizedKeyword])

  const filters = (
    <div className="platform-tool__filters">
      <label htmlFor="amazon-marketplace">
  {t('platform.amazon.filters.marketplace')}
        <select
          id="amazon-marketplace"
          value={marketplace}
          onChange={(event) => {
            setMarketplace(event.target.value)
            initialFetchRef.current = false
          }}
        >
          {MARKETPLACES.map((item) => (
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
  platformName={t('platform.amazon.meta.name')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
  description={t('platform.amazon.description')}
      extraFilters={filters}
      results={results}
  placeholder={t('platform.amazon.placeholder')}
      loading={loading}
      error={error}
  emptyState={t('platform.amazon.empty')}
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
      translate={t}
    />
  )
}

export default AmazonTool
