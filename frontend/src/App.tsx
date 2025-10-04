import React, { useEffect, useMemo, useState } from 'react'
import { COUNTRY_CODES, GOOGLE_LANGUAGES, flagEmoji } from './locales'

const FEATURED_LANGUAGE_CODES = ['en', 'nl', 'de', 'fr', 'es', 'it', 'pt', 'pl', 'tr', 'ja', 'ko', 'zh', 'ru'] as const

const LANGUAGE_FLAG_MAP: Record<string, string> = {
  en: 'us',
  nl: 'nl',
  de: 'de',
  fr: 'fr',
  es: 'es',
  it: 'it',
  pt: 'pt',
  pl: 'pl',
  tr: 'tr',
  ja: 'jp',
  ko: 'kr',
  zh: 'cn',
  ru: 'ru'
}

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
  const [language, setLanguage] = useState(() => {
    const urlCandidate = (urlLang || '').split('-')[0].toLowerCase()
    if (urlCandidate && /^[a-z]{2}$/i.test(urlCandidate)) {
      return urlCandidate
    }
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('lw_lang') || ''
        if (saved && /^[a-z]{2}$/i.test(saved)) {
          return saved.toLowerCase()
        }
      } catch {
        /* ignore */
      }
    }
    return 'en'
  })
  const [ui, setUi] = useState<{ lang: string; dir: 'ltr' | 'rtl'; strings: Record<string,string> } | null>(null)
  useEffect(() => {
    let lang = (urlLang || '').split('-')[0].toLowerCase()
    if (!lang || !/^[a-z]{2}$/i.test(lang)) {
      try {
        const saved = typeof window !== 'undefined' ? (localStorage.getItem('lw_lang') || '') : ''
        if (saved && /^[a-z]{2}$/i.test(saved)) {
          lang = saved.toLowerCase()
        }
      } catch {
        /* ignore */
      }
    }
    if (!lang) lang = 'en'
    const normalized = lang.toLowerCase()
    setLanguage(prev => {
      const prevLower = (prev || '').toLowerCase()
      return prevLower !== normalized ? normalized : prev
    })
    if (typeof window !== 'undefined') {
      try { localStorage.setItem('lw_lang', normalized) } catch { /* ignore */ }
    }
  }, [urlLang])
  useEffect(() => {
    const normalized = (language || '').split('-')[0].toLowerCase()
    if (!normalized) return
    let cancelled = false
    fetch(`/meta/content/${normalized}.json`)
      .then(r => (r.ok ? r.json() : Promise.reject()))
      .then((data) => {
        if (cancelled) return
        setUi(data)
        const resolvedLang = (data?.lang || normalized).toLowerCase()
        if (resolvedLang !== normalized) {
          setLanguage(prev => (prev === resolvedLang ? prev : resolvedLang))
          if (typeof window !== 'undefined') {
            try { localStorage.setItem('lw_lang', resolvedLang) } catch { /* ignore */ }
          }
          if (typeof document !== 'undefined') {
            document.documentElement.lang = resolvedLang
            document.documentElement.dir = data?.dir || 'ltr'
          }
          return
        }
        if (typeof window !== 'undefined') {
          try { localStorage.setItem('lw_lang', normalized) } catch { /* ignore */ }
        }
        if (typeof document !== 'undefined') {
          document.documentElement.lang = data?.lang || normalized
          document.documentElement.dir = data?.dir || 'ltr'
        }
      })
      .catch(() => {
        if (cancelled) return
        setUi({ lang: normalized, dir: 'ltr', strings: {} })
        if (typeof document !== 'undefined') {
          document.documentElement.lang = normalized
          document.documentElement.dir = 'ltr'
        }
      })
    return () => {
      cancelled = true
    }
  }, [language])
  const [keyword, setKeyword] = useState('')
  // Language used for fetching search results (does NOT change UI language)
  const [searchLanguage, setSearchLanguage] = useState(() => {
    if (typeof window !== 'undefined') {
      try {
        const savedSearch = localStorage.getItem('lw_search_lang')
        if (savedSearch && /^[a-z]{2}$/i.test(savedSearch)) {
          return savedSearch.toLowerCase()
        }
        const savedUi = localStorage.getItem('lw_lang')
        if (savedUi && /^[a-z]{2}$/i.test(savedUi)) {
          return savedUi.toLowerCase()
        }
      } catch {
        /* ignore */
      }
    }
    return (urlLang || language || 'en').toLowerCase()
  })
  const [country, setCountry] = useState(() => localStorage.getItem('lw_country') || '')
  // Detected country (geo/IP/headers) for display; separate from user-selected country used in searches
  const [detectedCountry, setDetectedCountry] = useState<string>('')
  const [languagesList, setLanguagesList] = useState(GOOGLE_LANGUAGES)
  const [countriesList, setCountriesList] = useState(COUNTRY_CODES)
  const [countrySearchTerm, setCountrySearchTerm] = useState('')
  const [showCountryDropdown, setShowCountryDropdown] = useState(false)
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
  const [langMenuAnchor, setLangMenuAnchor] = useState<'desktop' | 'mobile' | null>(null)
  const normalizedLanguage = (language || '').toLowerCase()
  type LanguageSelectOptions = { closeMenu?: boolean }

  const isSignedIn = !!token

  // Priority countries (mix of major regions worldwide - no bias)
  const priorityCountries = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'ES', 'IT', 'NL', 'BE', 'JP', 'BR', 'IN', 'MX', 'AR']
  
  // Filter and sort countries based on search
  const filteredCountries = useMemo(() => {
    if (!countrySearchTerm) {
      // No search - show priority countries first, then rest alphabetically
      const priority = priorityCountries.filter(cc => COUNTRY_CODES.includes(cc))
      const others = COUNTRY_CODES.filter(cc => !priorityCountries.includes(cc)).sort()
      return [...priority, ...others]
    }
    
    // Search mode - filter by country name
    const term = countrySearchTerm.toLowerCase()
    return COUNTRY_CODES.filter(cc => {
      try {
        const ctor: any = (Intl as any).DisplayNames
        if (ctor) {
          const dn = new ctor(['en'], { type: 'region' })
          const name = dn?.of?.(cc)?.toLowerCase() || cc.toLowerCase()
          return name.includes(term) || cc.toLowerCase().includes(term)
        }
        return cc.toLowerCase().includes(term)
      } catch {
        return cc.toLowerCase().includes(term)
      }
    })
  }, [countrySearchTerm])

  // Get country display name
  const getCountryName = (code: string) => {
    try {
      const ctor: any = (Intl as any).DisplayNames
      if (ctor) {
        const dn = new ctor([ui?.lang || 'en'], { type: 'region' })
        return dn?.of?.(code) || code
      }
      return code
    } catch {
      return code
    }
  }

  const toggleLangMenu = (anchor: 'desktop' | 'mobile') => {
    setLangMenuAnchor(prev => (prev === anchor ? null : anchor))
  }

  const closeLangMenu = () => setLangMenuAnchor(null)

  const handleLanguageSelect = (newLang: string, options: LanguageSelectOptions = {}) => {
    const normalized = (newLang || '').split('-')[0].toLowerCase()
    if (!normalized) return
    if (options.closeMenu !== false) {
      closeLangMenu()
    }
    if (normalized === normalizedLanguage) return
    if (typeof window !== 'undefined') {
      try { localStorage.setItem('lw_lang', normalized) } catch { /* ignore */ }
    }
    setLanguage(normalized)
    setSearchLanguage(prev => {
      if (!prev || prev === normalizedLanguage) {
        if (typeof window !== 'undefined') {
          try { localStorage.setItem('lw_search_lang', normalized) } catch { /* ignore */ }
        }
        return normalized
      }
      return prev
    })
  }

  const currentLangLabel = useMemo(() => {
    const match = languagesList.find(l => (l.code || '').toLowerCase() === normalizedLanguage)
    return match?.label || (normalizedLanguage || 'en').toUpperCase()
  }, [languagesList, normalizedLanguage])

  const quickLanguages = useMemo(() => {
    const ordered = new Map<string, { code: string; label: string }>()
    FEATURED_LANGUAGE_CODES.forEach(code => {
      const match = languagesList.find(l => (l.code || '').toLowerCase() === code)
      if (match) {
        ordered.set(match.code.toLowerCase(), match)
      }
    })
    const current = languagesList.find(l => (l.code || '').toLowerCase() === normalizedLanguage)
    if (current) {
      ordered.set(current.code.toLowerCase(), current)
    }
    return Array.from(ordered.values())
  }, [languagesList, normalizedLanguage])

  const languageSwitcherLabel = ui?.strings?.['sidebar.languages'] || ui?.strings?.['nav.language'] || 'Interface language'

  const getLanguageIcon = (code: string) => {
    const mapped = LANGUAGE_FLAG_MAP[code] || code
    return /^[a-z]{2}$/i.test(mapped) ? flagEmoji(mapped) : code.toUpperCase()
  }

  const formatLanguageLabel = (label?: string) => (label || '').replace(/\s*\(.*?\)/, '').trim()

  // Localized country display name for the topbar pill
  const displayCountryName = useMemo(() => {
    if (!detectedCountry) {
      // Return "Unknown location" in current UI language
      return ui?.strings?.unknown_location || 'Unknown location'
    }
    try {
      const cc = detectedCountry.toUpperCase()
      const langCode = (ui?.lang || language || 'en').toLowerCase()
      const ctor: any = (Intl as any).DisplayNames
      if (ctor) {
        const dn = new ctor([langCode], { type: 'region' })
        const name = dn?.of?.(cc)
        return name || cc
      }
      return cc
    } catch {
      return detectedCountry.toUpperCase()
    }
  }, [detectedCountry, ui?.lang, ui?.strings, language])

  const categoryOrder = useMemo(
    () => ['google_suggestions', 'trends_related', 'related_questions', 'wikipedia_terms'],
    []
  )

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!keyword.trim()) return
    
    // Require country selection
    if (!country) {
      alert('Please select a country first')
      return
    }
    
    // GTM tracking - Search button click
    if (typeof window !== 'undefined' && (window as any).dataLayer) {
      (window as any).dataLayer.push({
        event: 'search_button_click',
        search_keyword: keyword.trim(),
        search_language: searchLanguage,
        country: country,
        keyword_length: keyword.trim().length,
        has_keyword: keyword.trim().length > 0
      });
      console.log('🔍 GTM: Search button clicked', keyword.trim());
    }
    
    setLoading(true)
    setError(null)
    const searchStartTime = Date.now()
    
    try {
      const res = await fetch('/api/free/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: keyword.trim(), language: searchLanguage, country })
      })
      if (!res.ok) throw new Error('Search failed')
      const result = await res.json()
      setData(result)
      
      // GTM tracking - Search success
      if (typeof window !== 'undefined' && (window as any).dataLayer) {
        const totalKeywords = Object.values(result.categories || {}).reduce((sum: number, cat: any) => sum + cat.length, 0);
        (window as any).dataLayer.push({
          event: 'search_success',
          search_keyword: keyword.trim(),
          total_results: totalKeywords,
          categories_found: Object.keys(result.categories || {}).length,
          response_time: Date.now() - searchStartTime,
          search_language: searchLanguage
        });
        console.log('✅ GTM: Search successful', totalKeywords, 'results');
      }
      
    } catch (err: any) {
      setError(err?.message || 'Er is een fout opgetreden')
      
      // GTM tracking - Search error
      if (typeof window !== 'undefined' && (window as any).dataLayer) {
        (window as any).dataLayer.push({
          event: 'search_error',
          search_keyword: keyword.trim(),
          error_message: err?.message || 'Search failed',
          response_time: Date.now() - searchStartTime
        });
        console.log('❌ GTM: Search failed', err?.message);
      }
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
    // Check for auth token changes (e.g., after magic link verification)
    const checkToken = () => {
      const t = localStorage.getItem('lw_token')
      if (t && t !== token) {
        setToken(t)
      }
    }
    
    // Check immediately
    checkToken()
    
    // Also listen for storage events from other tabs/windows
    window.addEventListener('storage', checkToken)
    
    // Check periodically in case of timing issues
    const interval = setInterval(checkToken, 1000)
    
    return () => {
      window.removeEventListener('storage', checkToken)
      clearInterval(interval)
    }
  }, [token])

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
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSidebarOpen(false)
        setLangMenuAnchor(null)
        setShowCountryDropdown(false)
      }
    }
    document.addEventListener('keydown', handleEsc)
    return () => document.removeEventListener('keydown', handleEsc)
  }, [])

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (showCountryDropdown) {
        const target = e.target as Element
        if (!target.closest('.flag-select')) {
          setShowCountryDropdown(false)
          setCountrySearchTerm('')
        }
      }
    }
    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [showCountryDropdown])

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
          <div className="sidebar-lang-switch">
            <span className="sidebar-lang-heading">{languageSwitcherLabel}</span>
            <div
            className="sidebar-lang-carousel"
            role="listbox"
            aria-label={languageSwitcherLabel}
            >
            {quickLanguages.map((l) => {
              const code = (l.code || '').toLowerCase()
              const isActive = code === normalizedLanguage
              return (
              <button
                key={l.code}
                type="button"
                role="option"
                aria-selected={isActive}
                className={`sidebar-lang-pill${isActive ? ' active' : ''}`}
                onClick={() => handleLanguageSelect(l.code, { closeMenu: false })}
                title={formatLanguageLabel(l.label || l.code.toUpperCase())}
              >
                <span className="sidebar-lang-icon" aria-hidden>
                {getLanguageIcon(code)}
                </span>
                <span className="sidebar-lang-label-text">{formatLanguageLabel(l.label || l.code.toUpperCase())}</span>
              </button>
              )
            })}
            </div>
          </div>
          </div>
        </div>
      </aside>
      <div className={`overlay ${sidebarOpen ? 'show' : ''}`} onClick={() => setSidebarOpen(false)} />

      <div className="content">
        {/* Desktop header bar */}
        <div className="desktopbar" style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', borderBottom: '1px solid var(--line)', position: 'sticky', top: 0, zIndex: 9, background: 'rgba(11,13,16,0.6)', backdropFilter: 'saturate(180%) blur(10px)' }}>
          <div className="brand">Lucy <span>World</span></div>
          <div style={{ marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: 8, position: 'relative' }}>
            {/* Country indicator (shows detected location or unknown) */}
            {detectedCountry ? (
              <div
                className="country-pill"
                title={detectedCountry.toUpperCase()}
                aria-label={`Country ${detectedCountry.toUpperCase()}`}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
              >
                <span aria-hidden style={{ fontSize: 14 }}>{flagEmoji(detectedCountry.toUpperCase())}</span>
                <span style={{ fontWeight: 600 }}>{displayCountryName}</span>
              </div>
            ) : (
              <div
                className="country-pill"
                title="Location unknown"
                aria-label="Location unknown"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
              >
                <span aria-hidden style={{ fontSize: 14 }}>🌍</span>
                <span style={{ fontWeight: 600 }}>{displayCountryName}</span>
              </div>
            )}
            {/* Project features only for signed-in users */}
            {isSignedIn && (
              <>
                <button
                  type="button"
                  onClick={loadProjects}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
                >
                  📁 My projects
                </button>
                <button
                  type="button"
                  onClick={saveProject}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
                >
                  💾 Save project
                </button>
              </>
            )}
            {/* Language switch button (always visible) */}
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
                    onClick={() => handleLanguageSelect(l.code)}
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
              {/* Country indicator (shows detected location or unknown) */}
              {detectedCountry ? (
                <div
                  className="country-pill"
                  title={detectedCountry.toUpperCase()}
                  aria-label={`Country ${detectedCountry.toUpperCase()}`}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10, marginRight: 8 }}
                >
                  <span aria-hidden style={{ fontSize: 14 }}>{flagEmoji(detectedCountry.toUpperCase())}</span>
                  <span style={{ fontWeight: 600 }}>{displayCountryName}</span>
                </div>
              ) : (
                <div
                  className="country-pill"
                  title="Location unknown"
                  aria-label="Location unknown"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10, marginRight: 8 }}
                >
                  <span aria-hidden style={{ fontSize: 14 }}>🌍</span>
                  <span style={{ fontWeight: 600 }}>{displayCountryName}</span>
                </div>
              )}
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
                      onClick={() => handleLanguageSelect(l.code)}
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
            {/* Enhanced country selector with search */}
            <div style={{ position: 'relative' }}>
              <div
                className="select flag-select"
                onClick={() => setShowCountryDropdown(!showCountryDropdown)}
                style={{ 
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  minWidth: '120px'
                }}
                title={country ? `${flagEmoji(country)} ${getCountryName(country)}` : 'Select country'}
              >
                <span>{country ? `${flagEmoji(country)} ${getCountryName(country)}` : '🌍 Select country'}</span>
                <span style={{ marginLeft: '8px', fontSize: '12px' }}>▼</span>
              </div>
              
              {showCountryDropdown && (
                <div
                  style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    background: '#0e1217',
                    border: '1px solid var(--line)',
                    borderRadius: '8px',
                    maxHeight: '300px',
                    overflow: 'hidden',
                    zIndex: 1000,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
                  }}
                >
                  {/* Search input */}
                  <input
                    type="text"
                    placeholder="Search countries..."
                    value={countrySearchTerm}
                    onChange={(e) => setCountrySearchTerm(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Escape') {
                        setShowCountryDropdown(false)
                        setCountrySearchTerm('')
                      } else if (e.key === 'Enter' && filteredCountries.length > 0) {
                        setCountry(filteredCountries[0])
                        setShowCountryDropdown(false)
                        setCountrySearchTerm('')
                      }
                    }}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      background: 'transparent',
                      border: 'none',
                      borderBottom: '1px solid var(--line)',
                      color: 'var(--text)',
                      fontSize: '14px',
                      outline: 'none'
                    }}
                    autoFocus
                  />
                  
                  {/* Country list */}
                  <div style={{ maxHeight: '250px', overflow: 'auto' }}>
                    {filteredCountries.slice(0, 50).map((cc) => (
                      <div
                        key={cc}
                        onClick={() => {
                          setCountry(cc)
                          setShowCountryDropdown(false)
                          setCountrySearchTerm('')
                        }}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '8px 12px',
                          cursor: 'pointer',
                          background: cc === country ? 'var(--accent)' : 'transparent',
                          color: cc === country ? '#fff' : 'var(--text)',
                          borderRadius: cc === country ? '4px' : '0',
                          margin: cc === country ? '2px' : '0'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = cc === country ? 'var(--accent)' : 'rgba(255,255,255,0.1)'}
                        onMouseLeave={(e) => e.currentTarget.style.background = cc === country ? 'var(--accent)' : 'transparent'}
                      >
                        <span style={{ fontSize: '16px' }}>{flagEmoji(cc)}</span>
                        <span style={{ flex: 1 }}>{getCountryName(cc)}</span>
                        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{cc}</span>
                      </div>
                    ))}
                    {filteredCountries.length === 0 && (
                      <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                        No countries found
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
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
