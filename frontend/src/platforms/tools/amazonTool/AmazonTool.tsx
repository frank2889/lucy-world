import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

const MARKETPLACES = [
  { code: 'US', label: 'Amazon.com (US)' },
  { code: 'CA', label: 'Amazon.ca (CA)' },
  { code: 'GB', label: 'Amazon.co.uk (UK)' },
  { code: 'DE', label: 'Amazon.de (DE)' },
  { code: 'FR', label: 'Amazon.fr (FR)' },
  { code: 'IT', label: 'Amazon.it (IT)' },
  { code: 'ES', label: 'Amazon.es (ES)' },
  { code: 'NL', label: 'Amazon.nl (NL)' },
  { code: 'SE', label: 'Amazon.se (SE)' },
  { code: 'PL', label: 'Amazon.pl (PL)' },
  { code: 'BE', label: 'Amazon.be (BE)' },
  { code: 'AU', label: 'Amazon.com.au (AU)' },
  { code: 'JP', label: 'Amazon.co.jp (JP)' },
  { code: 'IN', label: 'Amazon.in (IN)' }
]

const AmazonTool: React.FC<PlatformToolProps> = ({ keyword, setKeyword, country }) => {
  const normalizedKeyword = keyword ?? ''
  const [marketplace, setMarketplace] = useState(() => {
    const preferred = (country ?? '').toUpperCase()
    return MARKETPLACES.some((m) => m.code === preferred) ? preferred : 'US'
  })
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const initialFetchRef = useRef(false)

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
          throw new Error(payload?.error || 'Onbekende fout bij Amazon data')
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((suggestion, index) => ({
          title: suggestion,
          subtitle: `Suggestie voor ${selectedMarketplace.label}`,
          metric: `Populariteit #${index + 1}`
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError('Geen Amazon suggesties gevonden voor dit zoekwoord.')
        }
      } catch (fetchError) {
        const message = fetchError instanceof Error ? fetchError.message : 'Onbekende fout'
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [selectedMarketplace.code, selectedMarketplace.label]
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
        Marketplace
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
      platformName="Amazon"
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description="Productzoekwoorden en listing-optimalisatie voor Amazon."
      extraFilters={filters}
      results={results}
      placeholder="Welke producten verkoop je?"
      loading={loading}
      error={error}
      emptyState="Voer een zoekwoord in om Amazon inzichten te zien."
    />
  )
}

export default AmazonTool
