import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const EBAY_SITES = [
  { country: 'US', siteId: '0', label: 'United States (eBay.com)' },
  { country: 'CA', siteId: '2', label: 'Canada (eBay.ca)' },
  { country: 'GB', siteId: '3', label: 'United Kingdom (eBay.co.uk)' },
  { country: 'AU', siteId: '15', label: 'Australia (eBay.com.au)' },
  { country: 'AT', siteId: '16', label: 'Austria (eBay.at)' },
  { country: 'FR', siteId: '71', label: 'France (eBay.fr)' },
  { country: 'DE', siteId: '77', label: 'Germany (eBay.de)' },
  { country: 'BE', siteId: '23', label: 'Belgium (eBay.be)' },
  { country: 'IT', siteId: '101', label: 'Italy (eBay.it)' },
  { country: 'NL', siteId: '146', label: 'Netherlands (eBay.nl)' },
  { country: 'ES', siteId: '186', label: 'Spain (eBay.es)' }
]

const DEFAULT_SITE_ID = '0'

const resolveDefaultSite = (country?: string) => {
  const normalized = (country || '').toUpperCase()
  const match = EBAY_SITES.find((item) => item.country === normalized)
  return match?.siteId ?? DEFAULT_SITE_ID
}

const EbayTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, country, ui } = props
  const normalizedKeyword = keyword ?? ''
  const [siteId, setSiteId] = useState(() => resolveDefaultSite(country))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])

  const selectedSite = useMemo(() => EBAY_SITES.find((item) => item.siteId === siteId) ?? EBAY_SITES[0], [siteId])

  useEffect(() => {
    setSiteId(resolveDefaultSite(country))
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
          siteId,
          country: (country || '').toUpperCase(),
          max: '10'
        })
        const response = await fetch(`/api/platforms/ebay?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.ebay.error.fetch'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.ebay.subtitle', {
            marketplace: selectedSite.label
          }),
          metric: t('platform.ebay.metric.rank', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.ebay.error.none'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.ebay.error.generic')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [siteId, country, selectedSite.label, t]
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
  }, [siteId, normalizedKeyword, performSearch])

  const filters = (
    <div className="platform-tool__filters">
      <label htmlFor="ebay-site">
  {t('platform.ebay.filters.marketplace')}
        <select
          id="ebay-site"
          value={siteId}
          onChange={(event) => {
            setSiteId(event.target.value)
            hasFetched.current = false
          }}
        >
          {EBAY_SITES.map((item) => (
            <option key={item.siteId} value={item.siteId}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  )

  return (
    <PlatformToolLayout
  platformName={t('platform.ebay.meta.name')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
  description={t('platform.ebay.description')}
      extraFilters={filters}
      results={results}
  placeholder={t('platform.ebay.placeholder')}
      loading={loading}
      error={error}
  emptyState={t('platform.ebay.empty')}
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
      translate={t}
    />
  )
}

export default EbayTool
