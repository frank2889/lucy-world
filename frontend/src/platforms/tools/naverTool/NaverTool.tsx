import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const NaverTool: React.FC<PlatformToolProps> = (props) => {
  const {
    keyword,
    setKeyword,
    searchLanguage,
    country,
    ui,
    locationControls,
    onGlobalSearch,
    globalLoading
  } = props
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
          q: query
        })
        if (searchLanguage) {
          params.set('lang', searchLanguage.toLowerCase())
        }
        if (country) {
          params.set('country', country.toLowerCase())
        }
        const response = await fetch(`/api/platforms/naver?${params.toString()}`)
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.error || t('platform.naver.errors.fetch', 'Unable to fetch Naver suggestions'))
        }
        const payload = await response.json()
        const suggestions: string[] = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestions.map((item, index) => ({
          title: item,
          subtitle: t('platform.naver.results.subtitle', 'Naver autosuggest result'),
          metric: t('platform.naver.results.rank', 'Popular #{{rank}}', { rank: index + 1 })
        }))
        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.naver.errors.noneFound', 'No Naver suggestions found for this keyword.'))
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : t('platform.naver.errors.generic', 'Unknown error')
        setError(message)
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [searchLanguage, country, t]
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
  }, [searchLanguage, country, normalizedKeyword, performSearch])

  return (
    <PlatformToolLayout
      platformName={t('platform.naver.meta.name', 'Naver')}
      keyword={normalizedKeyword}
      onKeywordChange={setKeyword}
      onSearch={performSearch}
      description={t('platform.naver.description', 'Search behaviour and content formats for Naver.')}
      results={results}
      placeholder={t('platform.naver.placeholder', 'Which Korean term are you analysing?')}
      loading={loading}
      error={error}
      emptyState={t('platform.naver.emptyState', 'Enter a keyword to see Naver opportunities.')}
      controls={locationControls}
      onGlobalSearch={onGlobalSearch}
      globalLoading={globalLoading}
      translate={t}
    />
  )
}

export default NaverTool
