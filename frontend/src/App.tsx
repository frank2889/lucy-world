import React, { useMemo, useState } from 'react'

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
  const [keyword, setKeyword] = useState('')
  const [language, setLanguage] = useState('nl')
  const [country, setCountry] = useState('NL')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<FreeSearchResponse | null>(null)

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

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">Lucy <span>World</span></div>
        <nav className="sidebar-nav">
          <a className="nav-item active">Zoeken</a>
          <a className="nav-item muted">Advanced (binnenkort)</a>
          <a className="nav-item muted">Trends (binnenkort)</a>
        </nav>
        <div className="sidebar-footer">© {new Date().getFullYear()} Lucy World</div>
      </aside>

      <div className="content">
        <div className="content-inner">
        <section className="search-card">
          <h3>Keyword onderzoek</h3>
          <form onSubmit={onSubmit} className="row">
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Voer een zoekwoord in (bijv. pizza bestellen)"
              required
            />
            <select className="select" value={country} onChange={(e) => setCountry(e.target.value)}>
              <option value="NL">Nederland</option>
              <option value="BE">België</option>
              <option value="DE">Duitsland</option>
              <option value="FR">Frankrijk</option>
              <option value="ES">Spanje</option>
              <option value="US">United States</option>
              <option value="GB">United Kingdom</option>
            </select>
            <select className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="nl">Nederlands</option>
              <option value="en">English</option>
              <option value="de">Deutsch</option>
              <option value="fr">Français</option>
              <option value="es">Español</option>
            </select>
            <button type="submit" disabled={loading}>
              {loading ? 'Zoeken…' : 'Zoeken'}
            </button>
          </form>
          <div className="hint">Gratis suggesties en trends. Resultaten verschijnen hieronder.</div>
          {error && <div className="error">{error}</div>}
        </section>

        {data && (
          <>
            <section className="grid">
              <div className="card" style={{ gridColumn: 'span 12' }}>
                <div className="kpi">
                  <div className="item">
                    <div className="label">Totaal keywords</div>
                    <div className="kpi-value">{nl(data.summary.total_keywords)}</div>
                  </div>
                  <div className="item">
                    <div className="label">Totaal volume</div>
                    <div className="kpi-value">{nl(data.summary.total_volume)}</div>
                  </div>
                  <div className="item">
                    <div className="label">Echte data keywords</div>
                    <div className="kpi-value">{nl(data.summary.real_data_keywords)}</div>
                  </div>
                  <div className="item">
                    <div className="label">Gem. interesse</div>
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
