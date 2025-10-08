import React, { useCallback, useMemo, useState } from 'react'
import type { PlatformToolProps } from '../../types'
import PlatformToolLayout, { type PlatformResultItem } from '../common/PlatformToolLayout'
import { createTranslator } from '../../../i18n/translate'

const GoogleTool: React.FC<PlatformToolProps> = (props) => {
  const { keyword, setKeyword, searchLanguage, country, ui } = props
  const [results, setResults] = useState<PlatformResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const t = useMemo(() => createTranslator(ui), [ui])

  const resolvedLanguage = useMemo(() => {
    return (searchLanguage || ui?.lang || 'en').split('-')[0].toLowerCase()
  }, [searchLanguage, ui?.lang])

  const resolvedCountry = useMemo(() => {
    return (country || '').trim().toUpperCase()
  }, [country])

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
          lang: resolvedLanguage || 'en'
        })
        if (resolvedCountry) {
          params.set('country', resolvedCountry)
        }

        const response = await fetch(`/api/platforms/google?${params.toString()}`)
        const payload = await response.json().catch(() => ({}))

        if (!response.ok) {
          throw new Error(payload?.error || t('platform.google.error.fetch'))
        }

        const suggestionsRaw = Array.isArray(payload?.suggestions) ? payload.suggestions : []
        const mapped: PlatformResultItem[] = suggestionsRaw
          .map((item: any, index: number) => {
            let text: string | null = null
            if (typeof item === 'string') {
              text = item
            } else if (item && typeof item === 'object') {
              text = item.phrase || item.keyword || item.text || null
            }
            if (!text) return null
            const subtitleParts: string[] = []
            if (payload?.metadata?.hl) {
              subtitleParts.push(t('platform.google.subtitle.language', {
                language: (payload.metadata.hl as string).toUpperCase()
              }))
            }
            if (payload?.metadata?.gl) {
              subtitleParts.push(t('platform.google.subtitle.country', {
                country: payload.metadata.gl
              }))
            }
            return {
              title: text,
              subtitle: subtitleParts.length
                ? subtitleParts.join(' • ')
                : t('platform.google.result.subtitle'),
              metric: t('platform.google.result.rank', { rank: index + 1 })
            }
          })
          .filter(Boolean) as PlatformResultItem[]

        setResults(mapped)
        if (mapped.length === 0) {
          setError(t('platform.google.error.none'))
        }
      } catch (err: any) {
        setError(err?.message || t('platform.google.error.generic'))
        setResults([])
      } finally {
        setLoading(false)
      }
    },
    [resolvedLanguage, resolvedCountry, t]
  )

  const handleSearch = useCallback(
    (term: string) => {
      performSearch(term)
    },
    [performSearch]
  )

  return (
    <PlatformToolLayout
      platformName={t('platform.google.meta.name')}
      keyword={keyword || ''}
      onKeywordChange={setKeyword}
      onSearch={handleSearch}
      description={t('platform.google.description')}
      results={results}
      placeholder={t('platform.google.placeholder')}
      loading={loading}
      error={error}
      emptyState={t('platform.google.empty')}
      controls={props.locationControls}
      onGlobalSearch={props.onGlobalSearch}
      globalLoading={props.globalLoading}
      translate={t}
    />
  )
}

export default GoogleTool
