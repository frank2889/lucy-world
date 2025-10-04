import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const CLIENT_OPTIONS = [
  { value: 'opensearch', label: 'OpenSearch' },
  { value: 'toolbar', label: 'Toolbar' },
  { value: 'mobile', label: 'Mobile' }
]

const QwantTool: React.FC<PlatformToolProps> = (props) => {
  const {
    keyword,
    setKeyword,
    searchLanguage,
    ui,
    locationControls,
    onGlobalSearch,
    globalLoading
  } = props
  const normalizedKeyword = keyword ?? ''
  const [client, setClient] = useState<string>('opensearch')
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])
  const clientOptions = useMemo(
    () =>
      CLIENT_OPTIONS.map((item) => ({
        ...item,
        label: t(`platform.qwant.client.${item.value}`, item.label)
      })),
    [t]
  )

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
          throw new Error(payload?.error || t('platform.qwant.errors.fetch', 'Unable to fetch Qwant suggestions'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.qwant.results.subtitle', 'Qwant ({{client}})', {
            client: payload?.metadata?.client || client
          }),
          metric: t('platform.qwant.results.rank', 'Suggestion #{{rank}}', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.qwant.errors.noneFound', 'No Qwant suggestions found for this keyword.'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.qwant.errors.generic', 'Unknown error')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [client, searchLanguage, t]
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
        {t('platform.qwant.filters.client', 'Client')}
        <select
          id="qwant-client"
          value={client}
          onChange={(event) => {
            setClient(event.target.value)
            hasFetched.current = false
          }}
        >
          {clientOptions.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  ), [client, clientOptions, t])

  return (
    <PlatformToolLayout
      platformName={t('platform.qwant.meta.name', 'Qwant')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description={t('platform.qwant.description', 'European search engine Qwant autocomplete.')}
      extraFilters={filters}
      results={results}
      placeholder={t('platform.qwant.placeholder', 'Which search term would you like to inspect?')}
      loading={loading}
      error={error}
      emptyState={t('platform.qwant.emptyState', 'Enter a keyword to see Qwant suggestions.')}
      controls={locationControls}
      onGlobalSearch={onGlobalSearch}
      globalLoading={globalLoading}
      translate={t}
    />
  )
}

export default QwantTool
