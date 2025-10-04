import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'

const CLIENT_OPTIONS = [
  { value: 'opensearch', label: 'OpenSearch' },
  { value: 'toolbar', label: 'Toolbar' },
  { value: 'mobile', label: 'Mobile' }
]

const QwantTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, searchLanguage } = props
  const normalizedKeyword = keyword ?? ''
  const [client, setClient] = useState<string>('opensearch')
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
          client
        })
        const response = await fetch(`/api/platforms/qwant?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || 'Onbekende Qwant fout')
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: `Qwant (${payload?.metadata?.client || client})`,
          metric: `Suggestie #${index + 1}`
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError('Geen Qwant suggesties gevonden voor dit zoekwoord.')
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Onbekende fout'
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [client, searchLanguage]
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
  }, [client, normalizedKeyword, performSearch])

  const filters = useMemo(() => (
    <div className="platform-tool__filters">
      <label htmlFor="qwant-client">
        Client
        <select
          id="qwant-client"
          value={client}
          onChange={(event) => {
            setClient(event.target.value)
            hasFetched.current = false
          }}
        >
          {CLIENT_OPTIONS.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  ), [client])

  return (
    <PlatformToolLayout
      platformName="Qwant"
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description="Europese zoekmachine Qwant autocomplete."
      extraFilters={filters}
      results={results}
      placeholder="Welke zoekterm wil je bekijken?"
      loading={loading}
      error={error}
      emptyState="Voer een zoekwoord in om Qwant suggesties te zien."
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
    />
  )
}

export default QwantTool
