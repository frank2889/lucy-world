import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

const SOURCE_OPTIONS = [
  { value: 'web', label: 'Web' },
  { value: 'news', label: 'Nieuws' },
  { value: 'videos', label: 'Video' }
]

const BraveTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, searchLanguage, country } = props
  const normalizedKeyword = keyword ?? ''
  const [source, setSource] = useState<string>('web')
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
          source
        })
        const response = await fetch(`/api/platforms/brave?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || 'Onbekende Brave fout')
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: `Brave (${payload?.metadata?.source || source})`,
          metric: `Suggestie #${index + 1}`
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError('Geen Brave suggesties gevonden voor dit zoekwoord.')
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Onbekende fout'
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [source, searchLanguage]
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
  }, [source, normalizedKeyword, performSearch])

  const filters = useMemo(() => (
    <div className="platform-tool__filters">
      <label htmlFor="brave-source">
        Bron
        <select
          id="brave-source"
          value={source}
          onChange={(event) => {
            setSource(event.target.value)
            hasFetched.current = false
          }}
        >
          {SOURCE_OPTIONS.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  ), [source])

  return (
    <PlatformToolLayout
      platformName="Brave"
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description="Privacyvriendelijke Brave Search suggesties."
      extraFilters={filters}
      results={results}
      placeholder="Welke zoekterm wil je onderzoeken?"
      loading={loading}
      error={error}
      emptyState="Voer een zoekwoord in om Brave suggesties te zien."
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
    />
  )
}

export default BraveTool
