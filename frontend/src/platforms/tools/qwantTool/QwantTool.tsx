import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const CLIENT_FALLBACK_LABELS: Record<string, string> = {
  opensearch: 'OpenSearch',
  toolbar: 'Toolbar',
  mobile: 'Mobile'
}

const QwantTool: React.FC<PlatformToolProps> = (props) => {
  const {
    keyword,
    setKeyword,
    searchLanguage,
    ui,
    uiFallback,
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
  const t = useMemo(() => createTranslator(ui, uiFallback), [ui, uiFallback])

  const clientOptions = useMemo(() => {
    const opensearch = t('platform.qwant.client.opensearch')
    const toolbar = t('platform.qwant.client.toolbar')
    const mobile = t('platform.qwant.client.mobile')
    return [
      {
        value: 'opensearch',
        label: opensearch === 'platform.qwant.client.opensearch' ? CLIENT_FALLBACK_LABELS.opensearch : opensearch
      },
      {
        value: 'toolbar',
        label: toolbar === 'platform.qwant.client.toolbar' ? CLIENT_FALLBACK_LABELS.toolbar : toolbar
      },
      {
        value: 'mobile',
        label: mobile === 'platform.qwant.client.mobile' ? CLIENT_FALLBACK_LABELS.mobile : mobile
      }
    ]
  }, [t])

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
          throw new Error(payload?.error || t('platform.qwant.errors.fetch'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.qwant.results.subtitle', {
            client: payload?.metadata?.client || client
          }),
          metric: t('platform.qwant.results.rank', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.qwant.errors.noneFound'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.qwant.errors.generic')
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
  {t('platform.qwant.filters.client')}
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
  platformName={t('platform.qwant.meta.name')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
  description={t('platform.qwant.description')}
      extraFilters={filters}
      results={results}
  placeholder={t('platform.qwant.placeholder')}
      loading={loading}
      error={error}
  emptyState={t('platform.qwant.emptyState')}
      controls={locationControls}
      onGlobalSearch={onGlobalSearch}
      globalLoading={globalLoading}
      translate={t}
    />
  )
}

export default QwantTool
