import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const BaiduTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, searchLanguage, ui } = props
  const normalizedKeyword = keyword ?? ''
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const hasFetched = useRef(false)
  const t = useMemo(() => createTranslator(ui), [ui])

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
          lang: (searchLanguage || '').toLowerCase()
        })
        const response = await fetch(`/api/platforms/baidu?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.baidu.error.fetch', 'Unable to fetch Baidu suggestions'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.baidu.subtitle', 'Baidu search suggestion'),
          metric: t('platform.baidu.metric.rank', 'Hotness #{{rank}}', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.baidu.error.none', 'No Baidu suggestions found for this keyword.'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.baidu.error.generic', 'Unknown error')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [searchLanguage, t]
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
  }, [searchLanguage, normalizedKeyword, performSearch])

  return (
    <PlatformToolLayout
      platformName={t('platform.baidu.meta.name', 'Baidu')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description={t('platform.baidu.description', 'Insights for the Chinese search engine Baidu.')}
      results={results}
      placeholder={t('platform.baidu.placeholder', 'Chinese keyword or brand')}
      loading={loading}
      error={error}
      emptyState={t('platform.baidu.empty', 'Enter a keyword to discover Baidu ideas.')}
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
      translate={t}
    />
  )
}

export default BaiduTool
