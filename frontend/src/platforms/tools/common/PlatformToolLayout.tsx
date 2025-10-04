import React, { useMemo } from 'react'
import type { Translator } from '../../../i18n/translate'
import '../../styles/tools.css'

export type PlatformResultItem = {
  title: string
  subtitle?: string
  metric?: string
}

type PlatformToolLayoutProps = {
  platformName: string
  keyword: string
  onKeywordChange: (value: string) => void
  onSearch?: (keyword: string) => void
  description?: string
  extraFilters?: React.ReactNode
  results?: PlatformResultItem[]
  placeholder?: string
  loading?: boolean
  emptyState?: string
  error?: string | null
  controls?: React.ReactNode
  onGlobalSearch?: (keyword: string) => Promise<void> | void
  globalLoading?: boolean
  translate?: Translator
}

const PlatformToolLayout: React.FC<PlatformToolLayoutProps> = ({
  platformName,
  keyword,
  onKeywordChange,
  onSearch,
  description,
  extraFilters,
  results = [],
  placeholder,
  loading = false,
  emptyState,
  error = null,
  controls,
  onGlobalSearch,
  globalLoading = false,
  translate
}) => {
  const t = useMemo(() => translate ?? ((_: string, fallback: string) => fallback), [translate])
  const canSearch = keyword.trim().length > 0

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!canSearch) return
    const term = keyword.trim()
    if (!term) return
    const tasks: Array<Promise<unknown> | unknown> = []
    if (onGlobalSearch) {
      tasks.push(onGlobalSearch(term))
    }
    if (onSearch) {
      tasks.push(onSearch(term))
    }
    if (tasks.length) {
      await Promise.all(tasks.map((task) => Promise.resolve(task)))
    }
  }

  const heading = useMemo(
    () => t('platforms.common.heading', '{{platform}} keyword tool', { platform: platformName }),
    [platformName, t]
  )

  return (
    <section className="platform-tool">
      <header className="platform-tool__header">
        <h3>{heading}</h3>
        {description && <p className="platform-tool__description">{description}</p>}
      </header>
      <form className="platform-tool__form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={keyword}
          onChange={(event) => onKeywordChange(event.target.value)}
          placeholder={placeholder ?? t('platforms.common.placeholder', 'Keyword for {{platform}}', { platform: platformName })}
        />
        {controls}
        <div className="platform-tool__actions">
          <button type="submit" disabled={!canSearch || loading || globalLoading}>
            {loading ? t('platforms.common.button.loading', 'Loading…') : t('platforms.common.button.submit', 'Search')}
          </button>
        </div>
      </form>
      {extraFilters}
      <div className="platform-tool__results">
        {error && (
          <div className="platform-tool__placeholder" style={{ borderColor: '#ff6b6b', color: '#ff8888' }}>
            {error}
          </div>
        )}
        {loading && <div className="platform-tool__placeholder">{t('platforms.common.placeholder.loading', 'Loading results…')}</div>}
        {!loading && !error && results.length === 0 && (
          <div className="platform-tool__placeholder">{emptyState ?? t('platforms.common.placeholder.empty', 'Enter a keyword to see results.')}</div>
        )}
        {!loading && !error && results.length > 0 && (
          <ul>
            {results.map((item, index) => (
              <li key={`${item.title}-${index}`}>
                <span className="platform-tool__result-title">{item.title}</span>
                {item.subtitle && <span className="platform-tool__result-subtitle">{item.subtitle}</span>}
                {item.metric && <span className="platform-tool__result-metric">{item.metric}</span>}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}

export default PlatformToolLayout
