import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

const LIMIT_OPTIONS = [5, 10, 15, 20]

const resolveDefaultLimit = (raw?: string) => {
  const parsed = Number(raw)
  if (!Number.isFinite(parsed)) return 10
  return Math.min(Math.max(Math.round(parsed), 1), 20)
}

const YahooTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, searchLanguage, country } = props
  const normalizedKeyword = keyword ?? ''
  const [limit, setLimit] = useState(() => resolveDefaultLimit(undefined))
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)

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
          throw new Error(payload?.error || 'Onbekende Yahoo fout')
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: `Yahoo (${payload?.country || country || 'global'})`,
          metric: `Suggestie #${index + 1}`
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError('Geen Yahoo suggesties gevonden voor dit zoekwoord.')
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Onbekende fout'
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [limit, searchLanguage, country]
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
        Resultaten
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
  ), [limit])

  return (
    <PlatformToolLayout
      platformName="Yahoo"
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description="Yahoo zoekopdrachten met autocomplete suggesties."
      extraFilters={filters}
      results={results}
      placeholder="Waar ben je naar op zoek?"
      loading={loading}
      error={error}
      emptyState="Voer een zoekwoord in om Yahoo suggesties te zien."
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
    />
  )
}

export default YahooTool
