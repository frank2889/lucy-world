import type { LazyExoticComponent, ComponentType } from 'react'

export type UIStrings = Record<string, string>

export interface UIState {
  lang: string
  dir: 'ltr' | 'rtl'
  strings: UIStrings
}

export type CategoryItem = {
  keyword: string
  search_volume?: number
  difficulty?: number | null
  cpc?: number | null
  competition?: string
  trend?: string
}

export type FreeSearchResponse = {
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

export interface PlatformToolProps {
  keyword: string
  setKeyword: (value: string) => void
  ui?: UIState | null
  loading?: boolean
  error?: string | null
  data?: FreeSearchResponse | null
  setData?: (value: FreeSearchResponse | null) => void
  onSubmit?: (event: React.FormEvent<HTMLFormElement>) => void
  searchLanguage?: string
  setSearchLanguage?: (value: string) => void
  languagesList?: Array<{ code: string; label: string }>
  country?: string
  setCountry?: (value: string) => void
  countriesList?: string[]
  filteredCountries?: string[]
  showCountryDropdown?: boolean
  setShowCountryDropdown?: (value: boolean) => void
  countrySearchTerm?: string
  setCountrySearchTerm?: (value: string) => void
  getCountryName?: (code: string) => string
  flagEmoji?: (countryCode: string) => string
  categoryOrder?: string[]
  formatNumber?: (value?: number) => string
}

export interface PlatformConfig {
  id: string
  name: string
  icon: string
  description?: string
  tool: LazyExoticComponent<ComponentType<PlatformToolProps>>
}
