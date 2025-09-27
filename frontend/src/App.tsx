import React, { useEffect, useMemo, useState } from 'react'
import { COUNTRY_CODES, GOOGLE_LANGUAGES, flagEmoji } from './locales'

type CategoryItem = {
  keyword: string
  search_volume?: number
  difficulty?: number | null
  cpc?: number | null
  competition?: string
  trend?: string
}

type FreeSearchResponse = {
  keyword: string
  language: string
  categories: Record<string, CategoryItem[]>
  trends: {
    interest_over_time: number[]
    trending_searches: string[]
    related_topics: string[]
    avg_interest: number
    trend_direction: string
    data_points: number
  }
  summary: {
    total_volume: number
    total_keywords: number
    real_data_keywords: number
  }
}

async function freeSearch(keyword: string, language: string): Promise<FreeSearchResponse> {
  const res = await fetch('/api/free/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ keyword, language })
  })
  if (!res.ok) throw new Error('Search failed')
  return res.json()
}

function nl(n?: number) {
  return Number(n || 0).toLocaleString('nl-NL')
}

export default function App() {
  // Detect UI language from URL prefix: /<lang>/ ... fallback to 'nl'
  const urlLang = (typeof window !== 'undefined' ? window.location.pathname.split('/').filter(Boolean)[0] : '') || 'en'
  const [ui, setUi] = useState<{ lang: string; dir: 'ltr' | 'rtl'; strings: Record<string,string> } | null>(null)
  useEffect(() => {
    const lang = (urlLang || 'en').split('-')[0]
    fetch(`/meta/content/${lang}.json`).then(r => r.json()).then((data) => {
      setUi(data)
      if (typeof document !== 'undefined') {
        document.documentElement.lang = data.lang || lang
        document.documentElement.dir = data.dir || 'ltr'
      }
    }).catch(() => {
      setUi({ lang: lang, dir: 'ltr', strings: {} })
    })
  }, [urlLang])
  const [keyword, setKeyword] = useState('')
  const [language, setLanguage] = useState(() => localStorage.getItem('lw_lang') || urlLang || 'en')
  const [country, setCountry] = useState(() => localStorage.getItem('lw_country') || 'NL')
  const [languagesList, setLanguagesList] = useState(GOOGLE_LANGUAGES)
  const [countriesList, setCountriesList] = useState(COUNTRY_CODES)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<FreeSearchResponse | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const categoryOrder = useMemo(
    () => ['google_suggestions', 'trends_related', 'related_questions', 'wikipedia_terms'],
    []
  )

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!keyword.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/free/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: keyword.trim(), language, country })
      })
      if (!res.ok) throw new Error('Search failed')
      const result = await res.json()
      setData(result)
    } catch (err: any) {
      setError(err?.message || 'Er is een fout opgetreden')
    } finally {
      setLoading(false)
    }
  }

  // persist language/country
  useEffect(() => { localStorage.setItem('lw_lang', language) }, [language])
  useEffect(() => { localStorage.setItem('lw_country', country) }, [country])

  // Close sidebar on ESC key (mobile)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSidebarOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  // Load languages from backend master list (fallback to constant). If Shopify-style locales present, prefer those.
  useEffect(() => {
    fetch('/meta/locales.json')
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(data => {
        const arr = data?.locales
        if (Array.isArray(arr)) {
          let mapped: { code: string; label: string }[] = []
          const byCode = new Map(GOOGLE_LANGUAGES.map(l => [l.code, l.label]))
          mapped = (arr as string[]).map(c => ({ code: c.toLowerCase(), label: byCode.get(c.toLowerCase()) || c.toUpperCase() }))
          mapped = mapped.filter(x => x.code && x.label)
          if (mapped.length) setLanguagesList(mapped)
        }
        if (typeof data?.default === 'string' && !localStorage.getItem('lw_lang')) {
          setLanguage((urlLang || data.default || 'en').toLowerCase())
        }
      })
      .catch(() => {
        // fallback to master list of languages (codes)
        fetch('/meta/languages.json')
          .then(r => r.ok ? r.json() : Promise.reject())
          .then(data2 => {
            const arr2 = data2?.languages
            if (Array.isArray(arr2)) {
              const byCode = new Map(GOOGLE_LANGUAGES.map(l => [l.code, l.label]))
              const mapped2 = (arr2 as string[]).map(c => ({ code: c.toLowerCase(), label: byCode.get(c.toLowerCase()) || c.toUpperCase() }))
              if (mapped2.length) setLanguagesList(mapped2)
            }
          })
          .catch(() => { /* keep fallback */ })
      })
  }, [])

  // Load countries from backend (fallback to constant)
  useEffect(() => {
    fetch('/meta/countries.json')
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(data => {
        if (Array.isArray(data?.countries)) {
          const arr = data.countries.filter((c: any) => typeof c === 'string' && c.length === 2)
          if (arr.length) setCountriesList(arr)
        }
      })
      .catch(() => { /* keep fallback */ })
  }, [])

  // Initialize language/country from server-side detection if user has no saved preferences
  useEffect(() => {
    try {
      const hasSavedLang = !!localStorage.getItem('lw_lang')
      const hasSavedCountry = !!localStorage.getItem('lw_country')
      // If path already starts with /xx/, we consider it authoritative for language
      const pathHasLangPrefix = typeof window !== 'undefined' && /^\/[a-z]{2}(?:\/$|\/|$)/i.test(window.location.pathname)
      if (hasSavedLang && hasSavedCountry) return
      fetch('/meta/detect.json')
        .then(r => (r.ok ? r.json() : Promise.reject()))
        .then((det) => {
          if (!hasSavedLang && !pathHasLangPrefix && det?.language && typeof det.language === 'string') {
            setLanguage(String(det.language).toLowerCase())
          }
          if (!hasSavedCountry && det?.country && typeof det.country === 'string' && det.country.length === 2) {
            setCountry(String(det.country).toUpperCase())
          }
        })
        .catch(() => { /* ignore */ })
    } catch {
      // ignore
    }
  }, [])

  return (
    <div className="layout">
  <aside id="sidebar" className={`sidebar ${sidebarOpen ? 'open' : ''}`} aria-hidden={!sidebarOpen}>
        <div className="sidebar-brand">Lucy <span>World</span></div>
        <nav className="sidebar-nav">
          <a className="nav-item active" onClick={() => setSidebarOpen(false)}>{ui?.strings['nav.search'] || 'Search'}</a>
          <a className="nav-item muted" onClick={() => setSidebarOpen(false)}>{ui?.strings['nav.advanced'] || 'Advanced (soon)'}</a>
          <a className="nav-item muted" onClick={() => setSidebarOpen(false)}>{ui?.strings['nav.trends'] || 'Trends (soon)'}</a>
        </nav>
        <div className="sidebar-footer">© {new Date().getFullYear()} Lucy World</div>
      </aside>
      <div className={`overlay ${sidebarOpen ? 'show' : ''}`} onClick={() => setSidebarOpen(false)} />

      <div className="content">
        {/* Mobile top bar */}
        <div className="topbar">
          <button
            className="hamburger"
            aria-label="Open navigatie"
            aria-expanded={sidebarOpen}
            aria-controls="sidebar"
            type="button"
            onClick={() => setSidebarOpen((v) => !v)}
          >
            <span />
            <span />
            <span />
          </button>
          <div className="brand">Lucy <span>World</span></div>
        </div>
        <div className="content-inner">
        <section className="search-card">
          <h3>{ui?.strings['search.title'] || 'Keyword research'}</h3>
          <form onSubmit={onSubmit} className="row">
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder={ui?.strings['search.placeholder'] || 'Enter a keyword'}
              required
            />
            <select
              className="select flag-select"
              value={country}
              onChange={(e) => setCountry(e.target.value.toUpperCase())}
              title={country}
            >
              {countriesList.map((cc) => (
                <option key={cc} value={cc}>{flagEmoji(cc)}</option>
              ))}
            </select>
            <select className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
              {languagesList.map((l) => (
                <option key={l.code} value={l.code}>{l.label}</option>
              ))}
            </select>
            <button type="submit" disabled={loading}>
              {loading ? (ui?.strings['search.button'] || 'Search') + '…' : (ui?.strings['search.button'] || 'Search')}
            </button>
          </form>
          <div className="hint">{ui?.strings['search.hint'] || 'Free suggestions and trends. Results appear below.'}</div>
          {error && <div className="error">{error}</div>}
        </section>

        {data && (
          <>
            <section className="grid">
              <div className="card" style={{ gridColumn: 'span 12' }}>
                <div className="kpi">
                  <div className="item">
                    <div className="label">{ui?.strings['kpi.total_keywords'] || 'Total keywords'}</div>
                    <div className="kpi-value">{nl(data.summary.total_keywords)}</div>
                  </div>
                  <div className="item">
                    <div className="label">{ui?.strings['kpi.total_volume'] || 'Total volume'}</div>
                    <div className="kpi-value">{nl(data.summary.total_volume)}</div>
                  </div>
                  <div className="item">
                    <div className="label">{ui?.strings['kpi.real_data_keywords'] || 'Real data keywords'}</div>
                    <div className="kpi-value">{nl(data.summary.real_data_keywords)}</div>
                  </div>
                  <div className="item">
                    <div className="label">{ui?.strings['kpi.avg_interest'] || 'Avg. interest'}</div>
                    <div className="kpi-value">{data.trends.avg_interest}</div>
                  </div>
                </div>
              </div>
            </section>

            <section className="grid">
              {Object.keys(data.categories)
                .sort((a, b) => categoryOrder.indexOf(a) - categoryOrder.indexOf(b))
                .map((cat) => {
                  const items = data.categories[cat]
                  if (!items || !items.length) return null
                  const title = cat.replace(/_/g, ' ')
                  return (
                    <div key={cat} className="card" style={{ gridColumn: 'span 12' }}>
                      <h4>{title}</h4>
                      <div>
                        {items.map((it, idx) => (
                          <span key={idx} className="pill">
                            {it.keyword} · {nl(it.search_volume)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )
                })}
            </section>
          </>
        )}
        </div>
        
      </div>
    </div>
  )
}
