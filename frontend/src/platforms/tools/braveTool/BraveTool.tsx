import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const BraveTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, searchLanguage, country, ui, uiFallback } = props
  const normalizedKeyword = keyword ?? ''
  const [source, setSource] = useState<string>('web')
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui, uiFallback), [ui, uiFallback])
  const sourceOptions = useMemo(
    () => [
      { value: 'web', label: t('platform.brave.source.web') },
      { value: 'news', label: t('platform.brave.source.news') },
      { value: 'videos', label: t('platform.brave.source.videos') }
    ],
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
          source
        })
        const response = await fetch(`/api/platforms/brave?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.brave.error.fetch'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.brave.subtitle', {
            source: payload?.metadata?.source || source
          }),
          metric: t('platform.brave.metric.rank', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.brave.error.none'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.brave.error.generic')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [source, searchLanguage, t]
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
  {t('platform.brave.filters.source')}
        <select
          id="brave-source"
          value={source}
          onChange={(event) => {
            setSource(event.target.value)
            hasFetched.current = false
          }}
        >
          {sourceOptions.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  ), [source, sourceOptions, t])

  return (
    <PlatformToolLayout
  platformName={t('platform.brave.meta.name')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
  description={t('platform.brave.description')}
      extraFilters={filters}
      results={results}
  placeholder={t('platform.brave.placeholder')}
      loading={loading}
      error={error}
  emptyState={t('platform.brave.empty')}
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
      translate={t}
    />
  )
}

export default BraveTool
