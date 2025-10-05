import React, { useCallback, useMemo, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const YouTubeTool: React.FC<PlatformToolProps> = (props) => {
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
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const t = useMemo(() => createTranslator(ui, uiFallback), [ui, uiFallback])

  const resolvedLanguage = useMemo(() => {
    return (searchLanguage || ui?.lang || 'en').split('-')[0].toLowerCase()
  }, [searchLanguage, ui?.lang])

  const performSearch = useCallback(async (term: string) => {
    const trimmed = term.trim()
    if (!trimmed) {
      setResults([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ q: trimmed, lang: resolvedLanguage })
      const response = await fetch(`/api/platforms/youtube?${params.toString()}`)
      const payload = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(payload?.error || t('platform.youtube.errors.fetch'))
      }
      const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
      const mapped: PlatformResultItem[] = suggestions.map((suggestion) => ({
        title: suggestion,
        subtitle: t('platform.youtube.results.subtitle'),
        metric: payload?.metadata?.approx_volume
          ? t('platform.youtube.results.metric', {
              volume: payload.metadata.approx_volume
            })
          : undefined
      }))
      setResults(mapped)
    } catch (err: any) {
      setError(err?.message || t('platform.youtube.errors.generic'))
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [resolvedLanguage, t])

  const handleSearch = useCallback((term: string) => {
    performSearch(term)
  }, [performSearch])

  return (
    <PlatformToolLayout
  platformName={t('platform.youtube.meta.name')}
      keyword={keyword || ''}
      onKeywordChange={setKeyword}
      onSearch={handleSearch}
  description={t('platform.youtube.description')}
      results={results}
  placeholder={t('platform.youtube.placeholder')}
  emptyState={t('platform.youtube.emptyState')}
      loading={loading}
      error={error}
      controls={locationControls}
      onGlobalSearch={onGlobalSearch}
      globalLoading={globalLoading}
      translate={t}
    />
  )
}

export default YouTubeTool
