import React from 'react'
import type { PlatformToolProps } from '../../types'
import { flagEmoji as defaultFlagEmoji } from '../../../locales'

const GoogleTool: React.FC<PlatformToolProps> = (props) => {
  const {
    keyword,
    setKeyword,
    onSubmit,
    loading = false,
    error,
    searchLanguage = 'en',
    setSearchLanguage,
    languagesList = [],
    country,
    setCountry,
    filteredCountries = [],
    showCountryDropdown = false,
    setShowCountryDropdown,
    countrySearchTerm = '',
    setCountrySearchTerm,
    getCountryName,
    categoryOrder = [],
    formatNumber,
    data,
    ui
  } = props

  const flagEmoji = props.flagEmoji || defaultFlagEmoji

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    if (!onSubmit) {
      event.preventDefault()
      return
    }
    onSubmit(event)
  }

  const formatNumberSafe = formatNumber || ((value?: number) => Number(value || 0).toLocaleString('nl-NL'))
  const resolveCountryName = getCountryName || ((code: string) => code)

  return (
    <section className="search-card">
      <h3>{ui?.strings?.['search.title'] || 'Keyword research'}</h3>
      <form onSubmit={handleSubmit} className="row">
        <input
          type="text"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          placeholder={ui?.strings?.['search.placeholder'] || 'Enter a keyword'}
          required
        />
        <div style={{ position: 'relative' }}>
          <div
            className="select flag-select"
            onClick={() => setShowCountryDropdown?.(!showCountryDropdown)}
            style={{
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              minWidth: '120px'
            }}
            title={country ? `${flagEmoji(country)} ${resolveCountryName(country)}` : 'Select country'}
          >
            <span>{country ? `${flagEmoji(country)} ${resolveCountryName(country)}` : '🌍 Select country'}</span>
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
              <input
                type="text"
                placeholder="Search countries..."
                value={countrySearchTerm}
                onChange={(event) => setCountrySearchTerm?.(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Escape') {
                    setShowCountryDropdown?.(false)
                    setCountrySearchTerm?.('')
                  } else if (event.key === 'Enter' && filteredCountries.length > 0) {
                    const first = filteredCountries[0]
                    setCountry?.(first)
                    setShowCountryDropdown?.(false)
                    setCountrySearchTerm?.('')
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

              <div style={{ maxHeight: '250px', overflow: 'auto' }}>
                {filteredCountries.slice(0, 50).map((countryCode) => (
                  <div
                    key={countryCode}
                    onClick={() => {
                      setCountry?.(countryCode)
                      setShowCountryDropdown?.(false)
                      setCountrySearchTerm?.('')
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '8px 12px',
                      cursor: 'pointer',
                      background: countryCode === country ? 'var(--accent)' : 'transparent',
                      color: countryCode === country ? '#fff' : 'var(--text)',
                      borderRadius: countryCode === country ? '4px' : '0',
                      margin: countryCode === country ? '2px' : '0'
                    }}
                  >
                    <span style={{ fontSize: '16px' }}>{flagEmoji(countryCode)}</span>
                    <span style={{ flex: 1 }}>{resolveCountryName(countryCode)}</span>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{countryCode}</span>
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
          onChange={(event) => {
            const newLang = event.target.value.toLowerCase()
            setSearchLanguage?.(newLang)
            try {
              localStorage.setItem('lw_search_lang', newLang)
            } catch {
              /* ignore */
            }
          }}
        >
          {languagesList.map((languageOption) => (
            <option key={languageOption.code} value={languageOption.code}>
              {languageOption.label}
            </option>
          ))}
        </select>
        <button type="submit" disabled={loading}>
          {loading ? (ui?.strings?.['search.button'] || 'Search') + '…' : ui?.strings?.['search.button'] || 'Search'}
        </button>
      </form>
      <div className="hint">{ui?.strings?.['search.hint'] || 'Free suggestions and trends. Results appear below.'}</div>
      <div className="hint" style={{ opacity: 0.8 }}>
        Gebruik de platforms in de zijbalk om de juiste tool voor je zoekwoord te kiezen. De zoekterm blijft behouden.
      </div>
      {error && <div className="error">{error}</div>}

      {data && (
        <>
          <section className="grid">
            <div className="card" style={{ gridColumn: 'span 12' }}>
              <div className="kpi">
                <div className="item">
                  <div className="label">{ui?.strings?.['kpi.total_keywords'] || 'Total keywords'}</div>
                  <div className="kpi-value">{formatNumberSafe(data.summary.total_keywords)}</div>
                </div>
                <div className="item">
                  <div className="label">{ui?.strings?.['kpi.total_volume'] || 'Total volume'}</div>
                  <div className="kpi-value">{formatNumberSafe(data.summary.total_volume)}</div>
                </div>
                <div className="item">
                  <div className="label">{ui?.strings?.['kpi.real_data_keywords'] || 'Real data keywords'}</div>
                  <div className="kpi-value">{formatNumberSafe(data.summary.real_data_keywords)}</div>
                </div>
                <div className="item">
                  <div className="label">{ui?.strings?.['kpi.avg_interest'] || 'Avg. interest'}</div>
                  <div className="kpi-value">{data.trends.avg_interest}</div>
                </div>
              </div>
            </div>
          </section>

          <section className="grid">
            {Object.keys(data.categories)
              .sort((a, b) => {
                const order = categoryOrder.length ? categoryOrder : undefined
                if (!order) return 0
                return order.indexOf(a) - order.indexOf(b)
              })
              .map((categoryKey) => {
                const items = data.categories[categoryKey]
                if (!items || !items.length) return null
                const title = categoryKey.replace(/_/g, ' ')
                return (
                  <div key={categoryKey} className="card" style={{ gridColumn: 'span 12' }}>
                    <h4>{title}</h4>
                    <div>
                      {items.map((item, index) => (
                        <span key={index} className="pill">
                          {item.keyword} · {formatNumberSafe(item.search_volume)}
                        </span>
                      ))}
                    </div>
                  </div>
                )
              })}
          </section>
        </>
      )}
    </section>
  )
}

export default GoogleTool
