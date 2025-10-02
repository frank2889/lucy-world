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
  // Detect UI language from URL prefix: /<lang>/ ... fallback to saved preference, then 'en'
  const urlLang = (typeof window !== 'undefined' ? window.location.pathname.split('/').filter(Boolean)[0] : '')
  const [ui, setUi] = useState<{ lang: string; dir: 'ltr' | 'rtl'; strings: Record<string,string> } | null>(null)
  useEffect(() => {
    // Prefer URL language when present; otherwise prefer saved UI language; else 'en'
    let lang = (urlLang || '').split('-')[0].toLowerCase()
    if (!lang || !/^[a-z]{2}$/i.test(lang)) {
      try {
        const saved = localStorage.getItem('lw_lang') || ''
        if (saved && /^[a-z]{2}$/i.test(saved)) {
          lang = saved.toLowerCase()
        }
      } catch {
        /* ignore */
      }
    }
    if (!lang) lang = 'en'
    fetch(`/meta/content/${lang}.json`).then(r => r.json()).then((data) => {
      setUi(data)
      const resolvedLang = (data?.lang || lang || 'en').toLowerCase()
      setLanguage(prev => {
        const prevLower = (prev || '').toLowerCase()
        return prevLower !== resolvedLang ? resolvedLang : prev
      })
      if (typeof document !== 'undefined') {
        document.documentElement.lang = data.lang || lang
        document.documentElement.dir = data.dir || 'ltr'
      }
    }).catch(() => {
      setUi({ lang, dir: 'ltr', strings: {} })
      setLanguage(prev => {
        const prevLower = (prev || '').toLowerCase()
        const resolved = (lang || 'en').toLowerCase()
        return prevLower !== resolved ? resolved : prev
      })
    })
  }, [urlLang])
  const [keyword, setKeyword] = useState('')
  // Language used for fetching search results (does NOT change UI language)
  const [searchLanguage, setSearchLanguage] = useState(() => localStorage.getItem('lw_search_lang') || (localStorage.getItem('lw_lang') || urlLang || 'en'))
  const [language, setLanguage] = useState(() => localStorage.getItem('lw_lang') || urlLang || 'en')
  const [country, setCountry] = useState(() => localStorage.getItem('lw_country') || 'NL')
  // Detected country (geo/IP/headers) for display; separate from user-selected country used in searches
  const [detectedCountry, setDetectedCountry] = useState<string>('')
  const [languagesList, setLanguagesList] = useState(GOOGLE_LANGUAGES)
  const [countriesList, setCountriesList] = useState(COUNTRY_CODES)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<FreeSearchResponse | null>(null)
  const [token, setToken] = useState<string | null>(() => {
    try { return localStorage.getItem('lw_token') } catch { return null }
  })
  const [showSignin, setShowSignin] = useState(false)
  const [signinEmail, setSigninEmail] = useState('')
  const [showProjects, setShowProjects] = useState(false)
  const [projects, setProjects] = useState<Array<{ id: number; name: string; description?: string | null; language?: string | null; country?: string | null; updated_at?: string }>>([])
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [langMenuAnchor, setLangMenuAnchor] = useState<'desktop' | 'mobile' | 'sidebar' | null>(null)

  const isSignedIn = !!token

  const toggleLangMenu = (anchor: 'desktop' | 'mobile' | 'sidebar') => {
    setLangMenuAnchor(prev => (prev === anchor ? null : anchor))
  }

  const closeLangMenu = () => setLangMenuAnchor(null)

  const currentLangLabel = useMemo(() => {
    const match = languagesList.find(l => (l.code || '').toLowerCase() === (language || '').toLowerCase())
    return match?.label || (language || 'en').toUpperCase()
  }, [languagesList, language])

  // Localized country display name for the topbar pill
  const displayCountryName = useMemo(() => {
    try {
      const cc = (detectedCountry || 'US').toUpperCase()
      const langCode = (ui?.lang || language || 'en').toLowerCase()
      const ctor: any = (Intl as any).DisplayNames
      if (ctor) {
        const dn = new ctor([langCode], { type: 'region' })
        const name = dn?.of?.(cc)
        return name || cc
      }
      return cc
    } catch {
      return (detectedCountry || 'US').toUpperCase()
    }
  }, [detectedCountry, ui?.lang, language])

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
        body: JSON.stringify({ keyword: keyword.trim(), language: searchLanguage, country })
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

  const requestMagicLink = async (e: React.FormEvent) => {
    e.preventDefault()
    const email = signinEmail.trim().toLowerCase()
    if (!email) return
    try {
      const res = await fetch('/api/auth/request', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })
      if (!res.ok) throw new Error('Failed to send sign-in link')
      alert('Check your email for a sign-in link. After clicking it, you will be redirected back here and signed in automatically.')
      setShowSignin(false)
    } catch (err: any) {
      alert(err?.message || 'Unable to send sign-in link')
    }
  }

  useEffect(() => {
    // capture token from localStorage changes on return from magic link verify
    const t = localStorage.getItem('lw_token')
    if (t && t !== token) setToken(t)
  }, [])

  const loadProjects = async () => {
    try {
      const t = token || localStorage.getItem('lw_token')
      if (!t) {
        setShowSignin(true)
        return
      }
      const res = await fetch('/api/projects', { headers: { 'Authorization': `Bearer ${t}` } })
      if (!res.ok) throw new Error('Failed to load projects')
      const j = await res.json()
      setProjects(Array.isArray(j) ? j : [])
      setShowProjects(true)
    } catch (err: any) {
      alert(err?.message || 'Could not load projects')
    }
  }

  const openProject = async (pid: number) => {
    try {
      const t = token || localStorage.getItem('lw_token')
      if (!t) { setShowSignin(true); return }
      const res = await fetch(`/api/projects/${pid}`, { headers: { 'Authorization': `Bearer ${t}` } })
      if (!res.ok) throw new Error('Failed to open project')
      const j = await res.json()
      // Restore search context
      if (j.language) setSearchLanguage(String(j.language))
      if (j.country) setCountry(String(j.country))
      if (j.data) setData(j.data)
      setShowProjects(false)
    } catch (err: any) {
      alert(err?.message || 'Open failed')
    }
  }

  const renameProject = async (pid: number) => {
    const newName = prompt('New project name:')
    if (!newName) return
    try {
      const t = token || localStorage.getItem('lw_token')
      if (!t) { setShowSignin(true); return }
      const res = await fetch(`/api/projects/${pid}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${t}` },
        body: JSON.stringify({ name: newName.trim() })
      })
      if (!res.ok) throw new Error('Rename failed')
      // update locally
      setProjects(prev => prev.map(p => p.id === pid ? { ...p, name: newName.trim() } : p))
    } catch (err: any) {
      alert(err?.message || 'Rename failed')
    }
  }

  const deleteProject = async (pid: number) => {
    if (!confirm('Delete this project?')) return
    try {
      const t = token || localStorage.getItem('lw_token')
      if (!t) { setShowSignin(true); return }
      const res = await fetch(`/api/projects/${pid}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${t}` }
      })
      if (!res.ok) throw new Error('Delete failed')
      setProjects(prev => prev.filter(p => p.id !== pid))
    } catch (err: any) {
      alert(err?.message || 'Delete failed')
    }
  }

  const saveProject = async () => {
    try {
      const t = token || localStorage.getItem('lw_token')
      if (!t) {
        setShowSignin(true)
        return
      }
      if (!data) {
        alert('Run a search first before saving a project')
        return
      }
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${t}` },
        body: JSON.stringify({
          name: `${data.keyword} (${searchLanguage}-${country})`,
          description: 'Saved from Lucy World',
          language: searchLanguage,
          country,
          data
        })
      })
      if (!res.ok) throw new Error('Failed to save project')
      const j = await res.json()
      alert(`Project saved (id ${j.id})`)
    } catch (err: any) {
      alert(err?.message || 'Save failed')
    }
  }

  // persist search language / UI language / country
  useEffect(() => { try { localStorage.setItem('lw_search_lang', searchLanguage) } catch {} }, [searchLanguage])
  useEffect(() => { localStorage.setItem('lw_lang', language) }, [language])
  useEffect(() => { localStorage.setItem('lw_country', country) }, [country])

  // Close sidebar on ESC key (mobile)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSidebarOpen(false)
        closeLangMenu()
      }
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
  const hasSavedSearchLang = !!localStorage.getItem('lw_search_lang')
      const hasSavedCountry = !!localStorage.getItem('lw_country')
      // If path already starts with /xx/, we consider it authoritative for language
      const pathHasLangPrefix = typeof window !== 'undefined' && /^\/[a-z]{2}(?:\/$|\/|$)/i.test(window.location.pathname)
      fetch('/meta/detect.json')
        .then(r => (r.ok ? r.json() : Promise.reject()))
        .then((det) => {
          const detLang = (det?.language || '').toString().toLowerCase()
          const detCountry = (det?.country || '').toString().toUpperCase()
          // Always capture detected country for topbar indicator
          if (detCountry && detCountry.length === 2) {
            setDetectedCountry(detCountry)
          }
          if (!hasSavedLang && !pathHasLangPrefix && detLang) {
            setLanguage(detLang)
            try { localStorage.setItem('lw_lang', detLang) } catch {}
          }
          if (!hasSavedSearchLang && detLang) {
            setSearchLanguage(detLang)
            try { localStorage.setItem('lw_search_lang', detLang) } catch {}
          }
          if (!hasSavedCountry && detCountry && detCountry.length === 2) {
            setCountry(detCountry)
            try { localStorage.setItem('lw_country', detCountry) } catch {}
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
        <div className="sidebar-footer">
          <span className="sidebar-footer-copy">© {new Date().getFullYear()} Lucy World</span>
          <div className="sidebar-footer-actions">
            <button
              type="button"
              className="sidebar-signin"
              disabled={isSignedIn}
              onClick={() => {
                if (!isSignedIn) {
                  setShowSignin(true)
                }
              }}
            >
              {isSignedIn ? (ui?.strings['footer.premium'] || 'Premium account') : (ui?.strings['footer.signin'] || 'Sign in for Premium')}
            </button>
            <div className="sidebar-lang-switch" style={{ position: 'relative' }}>
              <button
                type="button"
                className="sidebar-lang-btn"
                aria-haspopup="listbox"
                aria-expanded={langMenuAnchor === 'sidebar'}
                onClick={() => toggleLangMenu('sidebar')}
              >
                <span aria-hidden>🌐</span>
                <span style={{ fontWeight: 600 }}>{currentLangLabel}</span>
              </button>
              {langMenuAnchor === 'sidebar' && (
                <div
                  className="lang-menu sidebar-lang-menu"
                  role="listbox"
                  style={{
                    position: 'absolute', 
                    right: 0, 
                    bottom: 'calc(100% + 6px)',
                    background: '#0e1217', 
                    border: '1px solid var(--line)', 
                    borderRadius: 10,
                    minWidth: 280, 
                    maxWidth: 350,
                    maxHeight: 'min(60vh, 400px)', 
                    overflow: 'auto', 
                    zIndex: 1000,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
                  }}
                >
                  {languagesList.map((l) => (
                    <button
                      key={l.code}
                      role="option"
                      aria-selected={l.code === language}
                      onClick={() => {
                        closeLangMenu()
                        const newLang = l.code.toLowerCase()
                        localStorage.setItem('lw_lang', newLang)
                        if (typeof window !== 'undefined') {
                          window.location.href = `/${newLang}/`
                        } else {
                          setLanguage(newLang)
                        }
                      }}
                      className={`lang-item ${l.code === language ? 'active' : ''}`}
                      style={{
                        display: 'flex', width: '100%', textAlign: 'left',
                        gap: 10, padding: '10px 12px', background: 'transparent', color: 'var(--text)',
                        border: 0, cursor: 'pointer'
                      }}
                    >
                      <span style={{ width: 22, textAlign: 'center' }}>{/* No pure language flags; show code */}</span>
                      <span style={{ flex: 1 }}>{l.label || l.code.toUpperCase()}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </aside>
      <div className={`overlay ${sidebarOpen ? 'show' : ''}`} onClick={() => setSidebarOpen(false)} />

      <div className="content">
        {/* Desktop header bar (only for signed-in users who have project features) */}
        {isSignedIn && (
        <div className="desktopbar" style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', borderBottom: '1px solid var(--line)', position: 'sticky', top: 0, zIndex: 9, background: 'rgba(11,13,16,0.6)', backdropFilter: 'saturate(180%) blur(10px)' }}>
          <div className="brand">Lucy <span>World</span></div>
          <div style={{ marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: 8, position: 'relative' }}>
            {/* Country indicator (always shows current detected location; independent from search settings) */}
            <div
              className="country-pill"
              title={(detectedCountry || 'US').toUpperCase()}
              aria-label={`Country ${(detectedCountry || 'US').toUpperCase()}`}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
            >
              <span aria-hidden style={{ fontSize: 14 }}>{flagEmoji((detectedCountry || 'US').toUpperCase())}</span>
              <span style={{ fontWeight: 600 }}>{displayCountryName}</span>
            </div>
            <button
              type="button"
              onClick={loadProjects}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
            >
              📁 My projects
            </button>
            {/* Save project / Sign-in */}
            <button
              type="button"
              onClick={saveProject}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
            >
              💾 Save project
            </button>
            {/* Reuse the lang switch button */}
            <button
              type="button"
              className="lang-btn"
              aria-haspopup="listbox"
              aria-expanded={langMenuAnchor === 'desktop'}
              onClick={() => toggleLangMenu('desktop')}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
              title={language.toUpperCase()}
            >
              <span aria-hidden>🌐</span>
              <span style={{ fontWeight: 600 }}>{currentLangLabel}</span>
            </button>
            {langMenuAnchor === 'desktop' && (
              <div
                className="lang-menu"
                role="listbox"
                style={{
                  position: 'absolute', right: 0, top: 'calc(100% + 6px)',
                  background: '#0e1217', border: '1px solid var(--line)', borderRadius: 10,
                  minWidth: 220, maxHeight: '50vh', overflow: 'auto', zIndex: 25,
                }}
              >
                {languagesList.map((l) => (
                  <button
                    key={l.code}
                    role="option"
                    aria-selected={l.code === language}
                    onClick={() => {
                      closeLangMenu()
                      const newLang = l.code.toLowerCase()
                      localStorage.setItem('lw_lang', newLang)
                      if (typeof window !== 'undefined') {
                        window.location.href = `/${newLang}/`
                      } else {
                        setLanguage(newLang)
                      }
                    }}
                    className={`lang-item ${l.code === language ? 'active' : ''}`}
                    style={{
                      display: 'flex', width: '100%', textAlign: 'left',
                      gap: 10, padding: '10px 12px', background: 'transparent', color: 'var(--text)',
                      border: 0, cursor: 'pointer'
                    }}
                  >
                    <span style={{ width: 22, textAlign: 'center' }}>{/* No pure language flags; show code */}</span>
                    <span style={{ flex: 1 }}>{l.label || l.code.toUpperCase()}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        )}
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
          <div className="topbar-actions" style={{ marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
            <div className="lang-switch" style={{ position: 'relative', zIndex: 30 }}>
              {/* Country indicator (always shows current detected location; independent from search settings) */}
              <div
                className="country-pill"
                title={(detectedCountry || 'US').toUpperCase()}
                aria-label={`Country ${(detectedCountry || 'US').toUpperCase()}`}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10, marginRight: 8 }}
              >
                <span aria-hidden style={{ fontSize: 14 }}>{flagEmoji((detectedCountry || 'US').toUpperCase())}</span>
                <span style={{ fontWeight: 600 }}>{displayCountryName}</span>
              </div>
              <button
                type="button"
                className="lang-btn"
                aria-haspopup="listbox"
                aria-expanded={langMenuAnchor === 'mobile'}
                onClick={() => toggleLangMenu('mobile')}
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: 8,
                  background: 'transparent', color: 'var(--text)',
                  border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10,
                }}
                title={language.toUpperCase()}
              >
                <span aria-hidden>🌐</span>
                <span style={{ fontWeight: 600 }}>{currentLangLabel}</span>
              </button>
              {langMenuAnchor === 'mobile' && (
                <div
                  className="lang-menu"
                  role="listbox"
                  style={{
                    position: 'absolute', 
                    right: 0, 
                    top: 'calc(100% + 6px)',
                    background: '#0e1217', 
                    border: '1px solid var(--line)', 
                    borderRadius: 10,
                    minWidth: 280, 
                    maxHeight: 'min(60vh, 400px)', 
                    overflow: 'auto', 
                    zIndex: 1000,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
                  }}
                >
                  {languagesList.map((l) => (
                    <button
                      key={l.code}
                      role="option"
                      aria-selected={l.code === language}
                      onClick={() => {
                        closeLangMenu()
                        // Persist and navigate to language route for proper i18n + SEO
                        const newLang = l.code.toLowerCase()
                        localStorage.setItem('lw_lang', newLang)
                        if (typeof window !== 'undefined') {
                          window.location.href = `/${newLang}/`
                        } else {
                          setLanguage(newLang)
                        }
                      }}
                      className={`lang-item ${l.code === language ? 'active' : ''}`}
                      style={{
                        display: 'flex', width: '100%', textAlign: 'left',
                        gap: 10, padding: '10px 12px', background: 'transparent', color: 'var(--text)',
                        border: 0, cursor: 'pointer'
                      }}
                    >
                      <span style={{ width: 22, textAlign: 'center' }}>{/* No pure language flags; show code */}</span>
                      <span style={{ flex: 1 }}>{l.label || l.code.toUpperCase()}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="content-inner">
        {showSignin && (
          <div style={{ position: 'fixed', inset: 0 as any, background: 'rgba(0,0,0,0.5)', display: 'grid', placeItems: 'center', zIndex: 50 }} onClick={() => setShowSignin(false)}>
            <div style={{ background: '#0e1217', border: '1px solid var(--line)', borderRadius: 12, padding: 16, width: 'min(420px, 92vw)' }} onClick={e => e.stopPropagation()}>
              <h3 style={{ marginTop: 0 }}>Sign in</h3>
              <p>Enter your email to get a one-time sign-in link. No password needed.</p>
              <form onSubmit={requestMagicLink} style={{ display: 'flex', gap: 8 }}>
                <input type="email" placeholder="you@example.com" value={signinEmail} onChange={e => setSigninEmail(e.target.value)} required />
                <button type="submit">Send link</button>
              </form>
            </div>
          </div>
        )}

        {showProjects && (
          <div style={{ position: 'fixed', inset: 0 as any, background: 'rgba(0,0,0,0.5)', display: 'grid', placeItems: 'center', zIndex: 50 }} onClick={() => setShowProjects(false)}>
            <div style={{ background: '#0e1217', border: '1px solid var(--line)', borderRadius: 12, padding: 16, width: 'min(720px, 92vw)' }} onClick={e => e.stopPropagation()}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <h3 style={{ margin: 0, flex: 1 }}>My projects</h3>
                <button onClick={() => setShowProjects(false)} aria-label="Close" style={{ background: 'transparent', border: 0, color: 'var(--text)', fontSize: 20 }}>✕</button>
              </div>
              {projects.length === 0 ? (
                <p style={{ marginTop: 12 }}>No projects yet. Run a search and click "Save project" to create one.</p>
              ) : (
                <div style={{ marginTop: 12, display: 'grid', gap: 8 }}>
                  {projects.map((p) => (
                    <div key={p.id} style={{ display: 'flex', alignItems: 'center', gap: 10, border: '1px solid var(--line)', borderRadius: 10, padding: '10px 12px' }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.name}</div>
                        <div style={{ opacity: 0.7, fontSize: 12 }}>{[(p.language || '').toUpperCase(), p.country]?.filter(Boolean).join(' • ')}{p.updated_at ? ` • ${new Date(p.updated_at).toLocaleString()}` : ''}</div>
                      </div>
                      <div style={{ display: 'inline-flex', gap: 8 }}>
                        <button onClick={() => openProject(p.id)} title="Open" style={{ background: 'transparent', border: '1px solid var(--line)', borderRadius: 8, color: 'var(--text)', padding: '6px 10px' }}>Open</button>
                        <button onClick={() => renameProject(p.id)} title="Rename" style={{ background: 'transparent', border: '1px solid var(--line)', borderRadius: 8, color: 'var(--text)', padding: '6px 10px' }}>Rename</button>
                        <button onClick={() => deleteProject(p.id)} title="Delete" style={{ background: 'transparent', border: '1px solid var(--line)', borderRadius: 8, color: 'var(--text)', padding: '6px 10px' }}>Delete</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
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
            <select
              className="select"
              value={searchLanguage}
              onChange={(e) => {
                const newLang = e.target.value.toLowerCase()
                setSearchLanguage(newLang)
                try { localStorage.setItem('lw_search_lang', newLang) } catch {}
              }}
            >
              {languagesList.map((l) => (
                <option key={l.code} value={l.code}>{l.label}</option>
              ))}
            </select>
            <button type="submit" disabled={loading}>
              {loading ? (ui?.strings['search.button'] || 'Search') + '…' : (ui?.strings['search.button'] || 'Search')}
            </button>
          </form>
          <div className="hint">{ui?.strings['search.hint'] || 'Free suggestions and trends. Results appear below.'}</div>
          <div className="hint" style={{opacity:0.8}}>
            {/* Clarify UX distinction between site locale and search settings */}
            {(ui?.strings['hint.site_vs_search'] || 'Use the selectors above to choose the search country and language. Change the site interface language from the sidebar menu.')}
          </div>
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

        <footer className="footer">
          © {new Date().getFullYear()} Lucy World
        </footer>
        </div>
        
      </div>
    </div>
  )
}
