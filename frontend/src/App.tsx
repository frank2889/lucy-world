import React, { Suspense, useCallback, useEffect, useMemo, useState } from 'react'
import { COUNTRY_CODES, GOOGLE_LANGUAGES, flagEmoji } from './locales'
import { AMAZON_MARKETPLACE_CODES } from './platforms/data/amazonMarketplaces'
import PlatformSidebar from './platforms/Sidebar/PlatformSidebar'
import { usePlatformHandler } from './platforms/handlers/platformHandler'
import { createTranslator } from './i18n/translate'
import { useEntitlements } from './entitlements/useEntitlements'
import { EntitlementsProvider } from './entitlements/context'
import { RequireEntitlement } from './entitlements/RequireEntitlement'
import { filterPlatformsByEntitlements } from './entitlements/platformVisibility'
import type { UIState } from './platforms/types'
import { launchUpgradeCheckout } from './billing/checkoutLauncher'

type CategoryItem = {
  keyword: string
  search_volume?: number
  difficulty?: number | null
  cpc?: number | null
  competition?: string
  trend?: string
}

type PremiumSearchResponse = {
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

type CreditPack = {
  price_id: string
  credits: number
  currency?: string
  unit_amount?: number | null
  nickname?: string | null
  mode?: string | null
  description?: string | null
}

const DEFAULT_LANGUAGE = 'nl' as const

const SEARCH_TIMEOUT_MS = 20_000

const LANGUAGE_FLAG_OVERRIDES: Record<string, string> = {
  af: 'ZA',
  sq: 'AL',
  am: 'ET',
  ar: 'SA',
  hy: 'AM',
  eu: 'ES',
  be: 'BY',
  bn: 'BD',
  bs: 'BA',
  my: 'MM',
  ca: 'ES',
  zh: 'CN',
  co: 'FR',
  en: 'US',
  eo: '🌐',
  fy: 'NL',
  gl: 'ES',
  ka: 'GE',
  gu: 'IN',
  ha: 'NG',
  he: 'IL',
  hi: 'IN',
  ig: 'NG',
  id: 'ID',
  ga: 'IE',
  jv: 'ID',
  kn: 'IN',
  kk: 'KZ',
  km: 'KH',
  rw: 'RW',
  ko: 'KR',
  ku: 'IQ',
  ky: 'KG',
  lo: 'LA',
  la: 'VA',
  mg: 'MG',
  ms: 'MY',
  ml: 'IN',
  mi: 'NZ',
  mr: 'IN',
  ne: 'NP',
  ny: 'MW',
  or: 'IN',
  ps: 'AF',
  fa: 'IR',
  pt: 'PT',
  pa: 'IN',
  sm: 'WS',
  gd: 'GB',
  st: 'ZA',
  sn: 'ZW',
  sd: 'PK',
  si: 'LK',
  su: 'ID',
  sw: 'KE',
  tl: 'PH',
  tg: 'TJ',
  ta: 'IN',
  tt: 'RU',
  te: 'IN',
  ug: 'CN',
  cy: 'GB',
  xh: 'ZA',
  yi: 'IL',
  yo: 'NG',
  zu: 'ZA'
}

const getLanguageFlag = (code: string): string => {
  const normalized = (code || '').split('-')[0].toLowerCase()
  if (!normalized) return '🌐'
  const override = LANGUAGE_FLAG_OVERRIDES[normalized]
  if (override) {
    if (/^[A-Z]{2}$/.test(override)) {
      return flagEmoji(override)
    }
    return override
  }
  const cc = normalized.toUpperCase()
  if (COUNTRY_CODES.includes(cc)) {
    return flagEmoji(cc)
  }
  return '🌐'
}

async function fetchWithTimeout(resource: RequestInfo, options: RequestInit = {}, timeout = SEARCH_TIMEOUT_MS): Promise<Response> {
  const { signal: externalSignal, ...rest } = options
  const controller = new AbortController()
  let timedOut = false

  const timeoutId = setTimeout(() => {
    timedOut = true
    controller.abort()
  }, timeout)

  if (externalSignal) {
    if (externalSignal.aborted) {
      controller.abort()
    } else {
      externalSignal.addEventListener('abort', () => controller.abort(), { once: true })
    }
  }

  try {
    return await fetch(resource, { ...rest, signal: controller.signal })
  } catch (error) {
    if (timedOut) {
      const timeoutError = new DOMException('Request timed out', 'AbortError')
      ;(timeoutError as unknown as { isTimeout?: boolean }).isTimeout = true
      throw timeoutError
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}

function nl(n?: number) {
  return Number(n || 0).toLocaleString('nl-NL')
}

export default function App() {
  // Detect UI language from URL prefix - no fallbacks, all languages are equal
  const urlLang = (typeof window !== 'undefined' ? window.location.pathname.split('/').filter(Boolean)[0] : '')
  const [ui, setUi] = useState<UIState | null>(null)
  useEffect(() => {
    // Prefer URL language when present; otherwise prefer saved UI language; else DEFAULT_LANGUAGE
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
    if (!lang) lang = DEFAULT_LANGUAGE
    fetch(`/meta/content/${lang}.json`).then(r => r.json()).then((data) => {
      setUi(data)
      const resolvedLang = (data?.lang || lang || DEFAULT_LANGUAGE).toLowerCase()
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
        const resolved = (lang || DEFAULT_LANGUAGE).toLowerCase()
        return prevLower !== resolved ? resolved : prev
      })
    })
  }, [urlLang])
  const [keyword, setKeyword] = useState('')
  // Language used for fetching search results (does NOT change UI language)
  const [searchLanguage, setSearchLanguageState] = useState(() => {
    try {
      const stored = localStorage.getItem('lw_search_lang')
      if (stored) return stored.toLowerCase()
      const fallback = localStorage.getItem('lw_lang') || urlLang || DEFAULT_LANGUAGE
      return (fallback || DEFAULT_LANGUAGE).toLowerCase()
    } catch {
      return (urlLang || DEFAULT_LANGUAGE).toLowerCase()
    }
  })
  const [languageManuallySelected, setLanguageManuallySelected] = useState(() => {
    try {
      return localStorage.getItem('lw_search_lang_manual') === '1'
    } catch {
      return false
    }
  })
  const [language, setLanguage] = useState(() => {
    try {
      return (localStorage.getItem('lw_lang') || urlLang || DEFAULT_LANGUAGE).toLowerCase()
    } catch {
      return (urlLang || DEFAULT_LANGUAGE).toLowerCase()
    }
  })
  const [country, setCountry] = useState(() => {
    try {
      return localStorage.getItem('lw_country') || ''
    } catch {
      return ''
    }
  })
  const [languagesList, setLanguagesList] = useState(GOOGLE_LANGUAGES)
  const [countriesList, setCountriesList] = useState(COUNTRY_CODES)
  const [countrySearchTerm, setCountrySearchTerm] = useState('')
  const [showCountryDropdown, setShowCountryDropdown] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<PremiumSearchResponse | null>(null)
  const [selectedKeyword, setSelectedKeyword] = useState<{ keyword: string; search_volume: number; category: string } | null>(null)
  const [token, setToken] = useState<string | null>(() => {
    try { return localStorage.getItem('lw_token') } catch { return null }
  })
  const [showSignin, setShowSignin] = useState(false)
  const [signinEmail, setSigninEmail] = useState('')
  const [signinStatus, setSigninStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle')
  const [signinFeedback, setSigninFeedback] = useState<string | null>(null)
  const [showProjects, setShowProjects] = useState(false)
  const [projects, setProjects] = useState<Array<{ id: number; name: string; description?: string | null; language?: string | null; country?: string | null; updated_at?: string }>>([])
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [langMenuAnchor, setLangMenuAnchor] = useState<'desktop' | 'mobile' | null>(null)
  const [marketLocales, setMarketLocales] = useState<Map<string, string[]>>(() => new Map())
  const [billingLoading, setBillingLoading] = useState(false)
  const [creditPacks, setCreditPacks] = useState<CreditPack[]>([])
  const [creditPacksLoading, setCreditPacksLoading] = useState(false)
  const [creditCheckoutLoading, setCreditCheckoutLoading] = useState(false)
  const [stickyCtaDismissed, setStickyCtaDismissed] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false
    try {
      return sessionStorage.getItem('lw_sticky_cta_dismissed') === '1'
    } catch {
      return false
    }
  })

  useEffect(() => {
    if (showSignin) {
      setSigninStatus('idle')
      setSigninFeedback(null)
    }
  }, [showSignin])

  const closeSigninModal = useCallback(() => {
    setShowSignin(false)
    setSigninStatus('idle')
    setSigninFeedback(null)
  }, [])

  const entitlementsResult = useEntitlements(token)

  useEffect(() => {
    let cancelled = false
    const controller = new AbortController()

    if (!token) {
      setCreditPacks([])
      setCreditPacksLoading(false)
      return () => {
        cancelled = true
        controller.abort()
      }
    }

    setCreditPacksLoading(true)

    fetch('/api/billing/credit-packs', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`
      },
      signal: controller.signal
    })
      .then(async (response) => {
        if (response.status === 401) {
          throw new Error('unauthorized')
        }
        const payload = await response.json().catch(() => ({}))
        if (!response.ok) {
          const error = (payload && (payload.error || payload.message)) || `HTTP ${response.status}`
          throw new Error(String(error))
        }
        const packs = Array.isArray(payload?.packs) ? payload.packs : []
        return packs.filter((pack: CreditPack) => pack && typeof pack.price_id === 'string' && pack.price_id.trim().length > 0)
      })
      .then((packs) => {
        if (!cancelled) {
          setCreditPacks(packs)
        }
      })
      .catch((err) => {
        if (cancelled) return
        if (err?.message === 'unauthorized') {
          setCreditPacks([])
          return
        }
        console.warn('Unable to load credit packs', err)
        setCreditPacks([])
      })
      .finally(() => {
        if (!cancelled) {
          setCreditPacksLoading(false)
        }
      })

    return () => {
      cancelled = true
      controller.abort()
    }
  }, [token])

  const updateSearchLanguage = useCallback((lang: string, manual = false) => {
    const normalized = (lang || '').split('-')[0].toLowerCase() || DEFAULT_LANGUAGE
    setSearchLanguageState((prev) => (prev === normalized ? prev : normalized))
    try {
      localStorage.setItem('lw_search_lang', normalized)
      if (manual) {
        localStorage.setItem('lw_search_lang_manual', '1')
      } else {
        localStorage.removeItem('lw_search_lang_manual')
      }
    } catch {
      /* no-op */
    }
    setLanguageManuallySelected(manual)
    return normalized
  }, [setLanguageManuallySelected, setSearchLanguageState])

  const isSignedIn = !!token
  const { platforms, activePlatform, activePlatformId, setActivePlatformId } = usePlatformHandler()
  const ActivePlatformTool = activePlatform?.tool
  const translate = useMemo(() => createTranslator(ui), [ui])
  const getTranslated = useCallback((key: string, _fallback?: string) => {
    const value = translate(key)
    // Never use English fallback - show missing translation marker instead
    return value === key ? `[MISSING: ${key}]` : value
  }, [translate])
  const localizedPlatforms = useMemo(() => {
    const googleDescription = translate('platform.google.description')
    const duckduckgoDescription = translate('platform.duckduckgo.description')
    const yahooDescription = translate('platform.yahoo.description')
    const braveDescription = translate('platform.brave.description')
    const qwantDescription = translate('platform.qwant.description')
    const youtubeDescription = translate('platform.youtube.description')
    const amazonDescription = translate('platform.amazon.description')
    const tiktokDescription = translate('platform.tiktok.description')
    const instagramDescription = translate('platform.instagram.description')
    const pinterestDescription = translate('platform.pinterest.description')
    const bingDescription = translate('platform.bing.description')
    const baiduDescription = translate('platform.baidu.description')
    const yandexDescription = translate('platform.yandex.description')
    const naverDescription = translate('platform.naver.description')
    const ebayDescription = translate('platform.ebay.description')
    const appStoreDescription = translate('platform.appstore.description')
    const googlePlayDescription = translate('platform.googlePlay.description')
    const etsyDescription = translate('platform.etsy.description')

    const descriptionMap: Record<string, { key: string; value: string }> = {
      google: { key: 'platform.google.description', value: googleDescription },
      duckduckgo: { key: 'platform.duckduckgo.description', value: duckduckgoDescription },
      yahoo: { key: 'platform.yahoo.description', value: yahooDescription },
      brave: { key: 'platform.brave.description', value: braveDescription },
      qwant: { key: 'platform.qwant.description', value: qwantDescription },
      youtube: { key: 'platform.youtube.description', value: youtubeDescription },
      amazon: { key: 'platform.amazon.description', value: amazonDescription },
      tiktok: { key: 'platform.tiktok.description', value: tiktokDescription },
      instagram: { key: 'platform.instagram.description', value: instagramDescription },
      pinterest: { key: 'platform.pinterest.description', value: pinterestDescription },
      bing: { key: 'platform.bing.description', value: bingDescription },
      baidu: { key: 'platform.baidu.description', value: baiduDescription },
      yandex: { key: 'platform.yandex.description', value: yandexDescription },
      naver: { key: 'platform.naver.description', value: naverDescription },
      ebay: { key: 'platform.ebay.description', value: ebayDescription },
      appstore: { key: 'platform.appstore.description', value: appStoreDescription },
      googleplay: { key: 'platform.googlePlay.description', value: googlePlayDescription },
      etsy: { key: 'platform.etsy.description', value: etsyDescription }
    }

    return platforms.map((platform) => {
      const fallback = platform.description || platform.name
      const translated = descriptionMap[platform.id]
      if (!translated) {
        return {
          ...platform,
          description: fallback
        }
      }
      return {
        ...platform,
        description: translated.value === translated.key ? fallback : translated.value
      }
    })
  }, [platforms, translate])
  const visiblePlatforms = useMemo(
    () => filterPlatformsByEntitlements(localizedPlatforms, entitlementsResult.entitlements.sidebar_groups),
    [localizedPlatforms, entitlementsResult.entitlements.sidebar_groups]
  )

  useEffect(() => {
    if (!visiblePlatforms.length) return
    if (!visiblePlatforms.some((platform) => platform.id === activePlatformId)) {
      setActivePlatformId(visiblePlatforms[0].id)
    }
  }, [visiblePlatforms, activePlatformId, setActivePlatformId])

  const entitlementsData = entitlementsResult.entitlements
  const entitlementsPlanLabel = useMemo(() => getTranslated('entitlements.sidebar.plan_label', 'Your plan'), [getTranslated])
  const entitlementsStatus = entitlementsResult.status
  const entitlementsTierLabel = useMemo(() => {
    const tier = entitlementsData.tier
    const fallback = tier === 'enterprise' ? 'Enterprise' : tier === 'pro' ? 'Pro' : 'Free'
    return getTranslated(`entitlements.tier.${tier}`, fallback)
  }, [entitlementsData.tier, getTranslated])
  const aiCreditsLabel = useMemo(() => getTranslated('entitlements.sidebar.ai_credits', 'AI credits'), [getTranslated])
  const upgradeCtaLabel = useMemo(() => getTranslated('entitlements.actions.upgrade', 'Upgrade plan'), [getTranslated])
  const buyCreditsCtaLabel = useMemo(() => getTranslated('entitlements.actions.buy_credits', 'Get AI credits'), [getTranslated])
  const buyCreditsRequiresSigninLabel = useMemo(() => getTranslated('billing.error.buy_credits_signin', 'Sign in to buy AI credits.'), [getTranslated])
  const buyCreditsUnavailableLabel = useMemo(() => getTranslated('billing.error.buy_credits_unavailable', 'AI credit purchase is unavailable right now. Please contact support.'), [getTranslated])
  const loadingCreditPacksLabel = useMemo(() => getTranslated('billing.status.loading_credit_packs', 'Loading credit packs…'), [getTranslated])
  const upgradeUnavailableLabel = useMemo(() => getTranslated('billing.error.upgrade_unavailable', 'Upgrade is currently unavailable. Please contact support.'), [getTranslated])
  const upgradeRequiresSigninLabel = useMemo(() => getTranslated('billing.error.signin_required', 'Please sign in to upgrade.'), [getTranslated])
  const checkoutLaunchingLabel = useMemo(() => getTranslated('billing.status.launching_checkout', 'Opening checkout…'), [getTranslated])
  const checkoutFailedLabel = useMemo(() => getTranslated('billing.error.checkout_failed', 'Unable to open checkout. Please try again.'), [getTranslated])
  const aiUnlockedLabel = useMemo(() => getTranslated('entitlements.sidebar.ai_unlocked', 'AI workspace unlocked'), [getTranslated])
  const aiLockedLabel = useMemo(() => getTranslated('entitlements.sidebar.ai_locked', 'Unlock AI workspace with credits'), [getTranslated])
  const entitlementsLoadingLabel = useMemo(() => getTranslated('entitlements.status.loading', 'Loading plan…'), [getTranslated])
  const entitlementsErrorLabel = useMemo(() => getTranslated('entitlements.status.error', 'Unable to load plan'), [getTranslated])
  const lockedModuleMessage = useMemo(() => getTranslated('entitlements.locked.module', 'Upgrade your plan to access this module.'), [getTranslated])
  const upgradeNowLabel = useMemo(() => getTranslated('entitlements.actions.upgrade_now', 'Upgrade now'), [getTranslated])
  const normalizedUpgradeUrl = useMemo(() => {
    const raw = entitlementsData.upgrade_url
    return typeof raw === 'string' ? raw.trim() : ''
  }, [entitlementsData.upgrade_url])
  const handleUpgradeClick = useCallback(async () => {
    await launchUpgradeCheckout({
      upgradeUrl: normalizedUpgradeUrl,
      token,
      billingLoading,
      setBillingLoading,
      setError,
      setShowSignin,
      labels: {
        upgradeUnavailable: upgradeUnavailableLabel,
        upgradeRequiresSignin: upgradeRequiresSigninLabel,
        checkoutFailed: checkoutFailedLabel
      }
    })
  }, [normalizedUpgradeUrl, token, billingLoading, setBillingLoading, setError, setShowSignin, upgradeUnavailableLabel, upgradeRequiresSigninLabel, checkoutFailedLabel])
    const primaryCreditPack = useMemo(() => creditPacks.find((pack) => typeof pack?.price_id === 'string' && pack.price_id.trim().length > 0) || null, [creditPacks])
    const formatCreditPackPrice = useCallback((pack: CreditPack | null) => {
      if (!pack) return null
      const amount = typeof pack.unit_amount === 'number' ? pack.unit_amount / 100 : null
      if (amount === null) return null
      const currency = (pack.currency || 'EUR').toUpperCase()
      const localeCandidates = [
        language === 'nl' ? 'nl-NL' : null,
        language === 'en' ? 'en-US' : null,
        `${DEFAULT_LANGUAGE}-${DEFAULT_LANGUAGE.toUpperCase()}`,
        language ? `${language}-${language.toUpperCase()}` : null,
        language || DEFAULT_LANGUAGE,
        undefined
      ].filter((candidate): candidate is string | undefined => Boolean(candidate) || candidate === undefined)

      for (const locale of localeCandidates) {
        try {
          return new Intl.NumberFormat(locale, { style: 'currency', currency }).format(amount)
        } catch {
          continue
        }
      }

      return `${amount.toFixed(2)} ${currency}`
    }, [language])
    const primaryCreditPackPrice = useMemo(() => formatCreditPackPrice(primaryCreditPack), [formatCreditPackPrice, primaryCreditPack])
    const buyCreditsButtonText = useMemo(() => {
      if (creditPacksLoading) {
        return loadingCreditPacksLabel
      }
      if (creditCheckoutLoading) {
        return checkoutLaunchingLabel
      }
      if (primaryCreditPackPrice) {
        return `${buyCreditsCtaLabel} · ${primaryCreditPackPrice}`
      }
      return buyCreditsCtaLabel
    }, [buyCreditsCtaLabel, checkoutLaunchingLabel, creditCheckoutLoading, creditPacksLoading, loadingCreditPacksLabel, primaryCreditPackPrice])
    const handleBuyCreditsClick = useCallback(async () => {
      if (!token) {
        setShowSignin(true)
        setError(buyCreditsRequiresSigninLabel)
        return
      }
      if (billingLoading || creditCheckoutLoading) {
        return
      }
      if (!primaryCreditPack?.price_id) {
        setError(buyCreditsUnavailableLabel)
        return
      }

      setBillingLoading(true)
      setCreditCheckoutLoading(true)
      setError(null)

      try {
        const response = await fetch('/api/billing/credit-checkout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ price_id: primaryCreditPack.price_id, quantity: 1 })
        })

        let payload: any = null
        try {
          payload = await response.json()
        } catch {
          payload = null
        }

        if (response.status === 401) {
          setShowSignin(true)
          setError(buyCreditsRequiresSigninLabel)
          return
        }

        if (!response.ok || typeof payload?.url !== 'string' || !payload.url.trim()) {
          console.error('Credit checkout failed', { status: response.status, payload })
          setError(buyCreditsUnavailableLabel)
          return
        }

        if (typeof window !== 'undefined' && window.location) {
          window.location.href = payload.url
        }
      } catch (err) {
        console.error('Unable to initiate credit checkout', err)
        setError(buyCreditsUnavailableLabel)
      } finally {
        setCreditCheckoutLoading(false)
        setBillingLoading(false)
      }
    }, [token, billingLoading, creditCheckoutLoading, primaryCreditPack, setBillingLoading, setError, setShowSignin, buyCreditsRequiresSigninLabel, buyCreditsUnavailableLabel])
  const entitlementsExpiresLabel = useMemo(() => {
    if (!entitlementsData.expires_at) return null
    const parsed = new Date(entitlementsData.expires_at)
    const formatted = Number.isNaN(parsed.getTime()) ? entitlementsData.expires_at : parsed.toLocaleDateString()
    return getTranslated('entitlements.sidebar.expires', `Renews on ${formatted}`)
  }, [entitlementsData.expires_at, getTranslated])
  const searchLoadingLabel = useMemo(() => getTranslated('search.status.loading', 'Running keyword analysis…'), [getTranslated])
  const lowCreditsTitle = useMemo(() => getTranslated('billing.cta.low_credits.title', 'Almost out of AI credits?'), [getTranslated])
  const lowCreditsSubtitle = useMemo(() => getTranslated('billing.cta.low_credits.subtitle', 'Top up to keep premium keyword data flowing.'), [getTranslated])
  const signinCtaTitle = useMemo(() => getTranslated('billing.cta.signin.title', 'Unlock full keyword intelligence'), [getTranslated])
  const signinCtaSubtitle = useMemo(() => getTranslated('billing.cta.signin.subtitle', 'Sign in to access premium searches, saved projects, and AI credits.'), [getTranslated])
  const signinCtaEyebrow = useMemo(() => getTranslated('billing.cta.signin.eyebrow', 'Lucy World account'), [getTranslated])
  const stickyCtaDismissLabel = useMemo(() => getTranslated('billing.cta.dismiss', 'Hide this message'), [getTranslated])
  const lowCreditsCounterLabel = useMemo(() => {
    const raw = translate('billing.cta.low_credits.counter', { amount: entitlementsData.ai_credits })
    if (!raw || raw === 'billing.cta.low_credits.counter') {
      return `Remaining credits: ${entitlementsData.ai_credits}`
    }
    return raw
  }, [entitlementsData.ai_credits, translate])
  const openNavigationLabel = useMemo(() => translate('aria.open_navigation'), [translate])
  const myProjectsLabel = useMemo(() => translate('projects.button.my_projects'), [translate])
  const saveProjectLabel = useMemo(() => translate('projects.button.save'), [translate])
  const closeLabel = useMemo(() => translate('modal.close'), [translate])
  const signInTitle = useMemo(() => translate('auth.signin.title'), [translate])
  const signInDescription = useMemo(() => translate('auth.signin.description'), [translate])
  const signInPlaceholder = useMemo(() => translate('auth.signin.placeholder'), [translate])
  const sendLinkLabel = useMemo(() => translate('auth.signin.submit'), [translate])
  const sendingLinkLabel = useMemo(() => translate('auth.magic_link.sending'), [translate])
  const LOW_CREDITS_THRESHOLD = 25
  const isLowCredits = isSignedIn && typeof entitlementsData.ai_credits === 'number' && entitlementsData.ai_credits >= 0 && entitlementsData.ai_credits < LOW_CREDITS_THRESHOLD
  const showStickyCta = (!isSignedIn || isLowCredits) && !stickyCtaDismissed
  const stickyCtaButtonLabel = isLowCredits ? buyCreditsButtonText : signInTitle
  const stickyCtaDisabled = isLowCredits ? (billingLoading || creditCheckoutLoading) : false
  const handleStickyCtaClick = useCallback(() => {
    if (isLowCredits) {
      void handleBuyCreditsClick()
    } else {
      setShowSignin(true)
    }
  }, [isLowCredits, handleBuyCreditsClick, setShowSignin])
  const dismissStickyCta = useCallback(() => {
    setStickyCtaDismissed(true)
    try {
      sessionStorage.setItem('lw_sticky_cta_dismissed', '1')
    } catch {
      /* ignore */
    }
  }, [])
  useEffect(() => {
    if (isLowCredits && stickyCtaDismissed) {
      setStickyCtaDismissed(false)
      try {
        sessionStorage.removeItem('lw_sticky_cta_dismissed')
      } catch {
        /* ignore */
      }
    }
  }, [isLowCredits, stickyCtaDismissed])
  const projectsTitle = useMemo(() => translate('projects.modal.title'), [translate])
  const projectsEmptyMessage = useMemo(() => translate('projects.modal.empty', { save: saveProjectLabel }), [translate, saveProjectLabel])
  const openLabel = useMemo(() => translate('projects.modal.open'), [translate])
  const renameLabel = useMemo(() => translate('projects.modal.rename'), [translate])
  const deleteLabel = useMemo(() => translate('projects.modal.delete'), [translate])

  // Priority countries (mix of major regions + active marketplace coverage - no bias)
  const priorityCountries = useMemo(() => {
    const core = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'ES', 'IT', 'NL', 'BE']
    const activeMarketplaceCountries = AMAZON_MARKETPLACE_CODES
    const blended = [...core, ...activeMarketplaceCountries, 'JP', 'BR', 'IN', 'MX', 'AR']
    const seen = new Set<string>()
    return blended.filter((code) => {
      const upper = code.toUpperCase()
      if (!COUNTRY_CODES.includes(upper)) return false
      if (seen.has(upper)) return false
      seen.add(upper)
      return true
    })
  }, [languageManuallySelected, updateSearchLanguage])
  
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
      const dn = new ctor([DEFAULT_LANGUAGE], { type: 'region' })
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
  const dn = new ctor([ui?.lang || DEFAULT_LANGUAGE], { type: 'region' })
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

  const getLanguageLabel = useCallback((code?: string) => {
    const normalized = (code || '').toLowerCase()
    if (!normalized) return (code || '').toUpperCase()

    const fallbackRaw = languagesList.find((l) => (l.code || '').toLowerCase() === normalized)?.label || normalized.toUpperCase()
    let fallbackBase = fallbackRaw
    let fallbackHint = ''
    const fallbackMatch = typeof fallbackRaw === 'string' ? fallbackRaw.match(/^(.*?)\s*\((.*?)\)\s*$/) : null
    if (fallbackMatch) {
      fallbackBase = fallbackMatch[1]
      fallbackHint = fallbackMatch[2]
    }

    try {
      const ctor: any = (Intl as any).DisplayNames
      if (ctor) {
  const dn = new ctor([ui?.lang || language || DEFAULT_LANGUAGE], { type: 'language' })
        const localized = dn?.of?.(normalized)
        if (localized && typeof localized === 'string') {
          const titleCased = localized.charAt(0).toUpperCase() + localized.slice(1)
          if (titleCased.toLowerCase() === fallbackBase.toLowerCase()) {
            return titleCased
          }
          const hint = fallbackHint || fallbackBase
          return `${titleCased} (${hint})`
        }
      }
    } catch {
      /* ignore */
    }

    return fallbackRaw
  }, [languagesList, ui?.lang, language])

  const currentLangLabel = useMemo(() => getLanguageLabel(language), [getLanguageLabel, language])

  const renderPlanSummary = (variant: 'desktop' | 'mobile') => {
    const compact = variant === 'mobile'
    const containerStyle: React.CSSProperties = {
      display: 'grid',
      gap: compact ? 4 : 6,
      padding: compact ? '8px 10px' : '10px 12px',
      borderRadius: 12,
      border: '1px solid var(--line)',
      background: 'rgba(15,18,27,0.72)',
      color: 'var(--text)',
      minWidth: compact ? 0 : 210,
      flex: compact ? '1 1 auto' : '0 0 auto'
    }
    const labelStyle: React.CSSProperties = {
      fontSize: compact ? 10 : 11,
      textTransform: 'uppercase',
      letterSpacing: '0.08em',
      color: 'var(--text-secondary)',
      fontWeight: 600
    }

    if (entitlementsStatus === 'loading' || entitlementsStatus === 'idle') {
      return (
        <div style={containerStyle}>
          <div style={labelStyle}>{entitlementsPlanLabel}</div>
          <div style={{ fontSize: compact ? 12 : 13, color: 'var(--text-secondary)' }}>{entitlementsLoadingLabel}</div>
        </div>
      )
    }

    if (entitlementsStatus === 'error') {
      return (
        <div style={containerStyle}>
          <div style={labelStyle}>{entitlementsPlanLabel}</div>
          <div style={{ fontSize: compact ? 12 : 13, color: '#ffb3b3' }}>{entitlementsErrorLabel}</div>
        </div>
      )
    }

    const credits = Number(entitlementsData.ai_credits) || 0
    const hasCredits = credits > 0

    return (
      <div style={containerStyle}>
        <div style={labelStyle}>{entitlementsPlanLabel}</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: compact ? 16 : 18, fontWeight: 700 }}>{entitlementsTierLabel}</span>
          {entitlementsExpiresLabel ? (
            <span style={{ fontSize: compact ? 11 : 12, color: 'var(--text-secondary)' }}>{entitlementsExpiresLabel}</span>
          ) : null}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: compact ? 12 : 13, color: 'var(--text-secondary)' }}>
          <span>{aiCreditsLabel}</span>
          <span style={{ fontWeight: 600, color: 'var(--text)' }}>{credits}</span>
        </div>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: compact ? 11 : 12, color: 'var(--text-secondary)' }}>
          <span aria-hidden>{hasCredits ? '✨' : '⚡'}</span>
          <span>{hasCredits ? aiUnlockedLabel : aiLockedLabel}</span>
        </div>
      </div>
    )
  }

  const renderBillingActions = (variant: 'desktop' | 'mobile') => {
    const compact = variant === 'mobile'
    const containerStyle: React.CSSProperties = {
      display: 'inline-flex',
      alignItems: 'center',
      gap: compact ? 6 : 8,
      flexWrap: 'wrap',
      justifyContent: 'flex-end'
    }
    const buttonStyle: React.CSSProperties = {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 6,
      padding: compact ? '6px 10px' : '8px 12px',
      borderRadius: 10,
      border: '1px solid var(--line)',
      background: 'transparent',
      color: 'var(--text)',
      fontSize: compact ? 12 : 13
    }

    return (
      <div style={containerStyle}>
        <button
          type="button"
          onClick={handleUpgradeClick}
          disabled={billingLoading}
          style={{ ...buttonStyle, cursor: billingLoading ? 'wait' : 'pointer' }}
        >
          ⬆️ {billingLoading ? checkoutLaunchingLabel : upgradeCtaLabel}
        </button>
        {primaryCreditPack ? (
          <button
            type="button"
            onClick={handleBuyCreditsClick}
            disabled={billingLoading || creditPacksLoading}
            style={{ ...buttonStyle, cursor: billingLoading || creditPacksLoading ? 'wait' : 'pointer' }}
          >
            💡 {buyCreditsButtonText}
          </button>
        ) : entitlementsData.buy_credits_url ? (
          <a
            href={entitlementsData.buy_credits_url}
            target="_blank"
            rel="noreferrer"
            style={{ ...buttonStyle, textDecoration: 'none' }}
          >
            💡 {buyCreditsCtaLabel}
          </a>
        ) : null}
      </div>
    )
  }

  const locationControls = (
    <>
      <div className="platform-tool__control platform-tool__control--country" style={{ position: 'relative', minWidth: 160 }}>
        <div
          className="select flag-select"
          onClick={() => setShowCountryDropdown(!showCountryDropdown)}
          style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
          title={country ? `${flagEmoji(country)} ${getCountryName(country)}` : translate('controls.country.select_title')}
        >
          <span>{country ? `${flagEmoji(country)} ${getCountryName(country)}` : `🌍 ${translate('controls.country.select_placeholder')}`}</span>
          <span style={{ marginLeft: 8, fontSize: 12 }}>▼</span>
        </div>
        {showCountryDropdown && (
          <div
            style={{
              position: 'absolute',
              top: 'calc(100% + 6px)',
              left: 0,
              right: 0,
              background: '#0e1217',
              border: '1px solid var(--line)',
              borderRadius: 8,
              maxHeight: 300,
              overflow: 'hidden',
              zIndex: 1000,
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
            }}
          >
            <input
              type="text"
              placeholder={translate('controls.country.search_placeholder')}
              value={countrySearchTerm}
              onChange={(e) => setCountrySearchTerm(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Escape') {
                  setShowCountryDropdown(false)
                  setCountrySearchTerm('')
                } else if (e.key === 'Enter' && filteredCountries.length > 0) {
                  const nextCountry = filteredCountries[0]
                  setCountry(nextCountry)
                  try { localStorage.setItem('lw_country', nextCountry) } catch {}
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
                fontSize: 14,
                outline: 'none'
              }}
              autoFocus
            />
            <div style={{ maxHeight: 250, overflow: 'auto' }}>
              {filteredCountries.slice(0, 50).map((cc) => (
                <div
                  key={cc}
                  onClick={() => {
                    setCountry(cc)
                    try { localStorage.setItem('lw_country', cc) } catch {}
                    setShowCountryDropdown(false)
                    setCountrySearchTerm('')
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    padding: '8px 12px',
                    cursor: 'pointer',
                    background: cc === country ? 'var(--accent)' : 'transparent',
                    color: cc === country ? '#fff' : 'var(--text)'
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = cc === country ? 'var(--accent)' : 'rgba(255,255,255,0.1)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = cc === country ? 'var(--accent)' : 'transparent')}
                >
                  <span style={{ fontSize: 16 }}>{flagEmoji(cc)}</span>
                  <span style={{ flex: 1 }}>{getCountryName(cc)}</span>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{cc}</span>
                </div>
              ))}
              {filteredCountries.length === 0 && (
                <div style={{ padding: 16, textAlign: 'center', color: 'var(--text-secondary)' }}>
                  {translate('controls.country.no_results')}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      <select
        className="select platform-tool__language-select"
        value={searchLanguage}
        onChange={(e) => {
          const newLang = e.target.value.toLowerCase()
          updateSearchLanguage(newLang, true)
        }}
      >
        {languagesList.map((l) => (
          <option key={l.code} value={l.code}>{getLanguageLabel(l.code)}</option>
        ))}
      </select>
    </>
  )

  const categoryOrder = useMemo(
    () => ['google_suggestions', 'trends_related', 'related_questions', 'wikipedia_terms'],
    []
  )

  const runGlobalSearch = useCallback(async (term?: string) => {
    const submittedKeyword = (term ?? keyword).trim()
    if (!submittedKeyword) return

    if (!country) {
      alert(translate('alerts.country_required'))
      return
    }

    if (typeof window !== 'undefined' && (window as any).dataLayer) {
      (window as any).dataLayer.push({
        event: 'search_button_click',
        search_keyword: submittedKeyword,
        search_language: searchLanguage,
        country,
        keyword_length: submittedKeyword.length,
        has_keyword: submittedKeyword.length > 0
      })
      console.log('🔍 GTM: Search button clicked', submittedKeyword)
    }

    setLoading(true)
    setError(null)
    const searchStartTime = Date.now()

    try {
      const res = await fetchWithTimeout('/api/premium/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: submittedKeyword, language: searchLanguage, country })
      })
      if (!res.ok) throw new Error(translate('errors.search_failed'))
      const result = await res.json()
      setData(result)

      if (typeof window !== 'undefined' && (window as any).dataLayer) {
        const totalKeywords = Object.values(result.categories || {}).reduce((sum: number, cat: any) => sum + cat.length, 0)
        ;(window as any).dataLayer.push({
          event: 'search_success',
          search_keyword: submittedKeyword,
          total_results: totalKeywords,
          categories_found: Object.keys(result.categories || {}).length,
          response_time: Date.now() - searchStartTime,
          search_language: searchLanguage
        })
        console.log('✅ GTM: Search successful', totalKeywords, 'results')
      }
    } catch (err: any) {
      // Differentiate error types for proper localized messaging
      let errorKey = 'errors.generic'
      
      if (err?.name === 'AbortError' || /timeout/i.test(err?.message || '')) {
        errorKey = 'errors.search_timeout'
      } else if (err?.message?.includes('NetworkError') || err?.message?.includes('Failed to fetch')) {
        errorKey = 'errors.network_error'
      } else if (err?.status === 404 || err?.message?.includes('no results')) {
        errorKey = 'errors.search_no_results'
      } else if (err?.status >= 400 && err?.status < 500) {
        errorKey = 'errors.search_failed'
      }

      const errorMessage = translate(errorKey)
      setError(errorMessage === errorKey ? `[MISSING: ${errorKey}]` : errorMessage)

      if (typeof window !== 'undefined' && (window as any).dataLayer) {
        ;(window as any).dataLayer.push({
          event: 'search_error',
          search_keyword: submittedKeyword,
          error_type: errorKey,
          error_message: errorMessage,
          response_time: Date.now() - searchStartTime
        })
        console.log('❌ GTM: Search error', errorKey, errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }, [keyword, country, searchLanguage, translate])

  const requestMagicLink = async (e: React.FormEvent) => {
    e.preventDefault()
    const email = signinEmail.trim().toLowerCase()
    if (!email) return
    try {
      setSigninStatus('sending')
      const pendingMessage = sendingLinkLabel === 'auth.magic_link.sending'
        ? 'Sending link…'
        : sendingLinkLabel
      setSigninFeedback(pendingMessage)
      const res = await fetch('/api/auth/request', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })
      let payload: any = null
      try {
        payload = await res.json()
      } catch {
        payload = null
      }
      if (!res.ok) {
        const message = (payload && (payload.message || payload.error)) || translate('auth.magic_link.failed')
        throw new Error(message)
      }
      const successMessage = (payload && (payload.message || payload.detail)) || translate('auth.magic_link.sent')
      const normalized = successMessage === 'auth.magic_link.sent'
        ? 'Sign-in link sent. Check your inbox.'
        : successMessage
      setSigninStatus('sent')
      setSigninFeedback(normalized)
      setSigninEmail('')
    } catch (err: any) {
      const fallback = translate('auth.magic_link.error')
      const message = err?.message || fallback
      setSigninStatus('error')
      setSigninFeedback(message === 'auth.magic_link.error' ? 'We could not send the link. Please try again later.' : message)
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
  if (!res.ok) throw new Error(translate('projects.error.load'))
      const j = await res.json()
      setProjects(Array.isArray(j) ? j : [])
      setShowProjects(true)
    } catch (err: any) {
      alert(err?.message || translate('projects.error.load_generic'))
    }
  }

  const openProject = async (pid: number) => {
    try {
    const t = token || localStorage.getItem('lw_token')
    if (!t) { setShowSignin(true); return }
    const res = await fetch(`/api/projects/${pid}`, { headers: { 'Authorization': `Bearer ${t}` } })
    if (!res.ok) throw new Error(translate('projects.error.open'))
      const j = await res.json()
    // Restore search context
    if (j.language) updateSearchLanguage(String(j.language), true)
      if (j.country) setCountry(String(j.country))
      if (j.data) setData(j.data)
      setShowProjects(false)
    } catch (err: any) {
      alert(err?.message || translate('projects.error.open_generic'))
    }
  }

  const renameProject = async (pid: number) => {
    const newName = prompt(translate('projects.rename.prompt'))
    if (!newName) return
    try {
      const t = token || localStorage.getItem('lw_token')
      if (!t) { setShowSignin(true); return }
      const res = await fetch(`/api/projects/${pid}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${t}` },
        body: JSON.stringify({ name: newName.trim() })
      })
  if (!res.ok) throw new Error(translate('projects.error.rename'))
      // update locally
      setProjects(prev => prev.map(p => p.id === pid ? { ...p, name: newName.trim() } : p))
    } catch (err: any) {
      alert(err?.message || translate('projects.error.rename_generic'))
    }
  }

  const deleteProject = async (pid: number) => {
    if (!confirm(translate('projects.delete.confirm'))) return
    try {
      const t = token || localStorage.getItem('lw_token')
      if (!t) { setShowSignin(true); return }
      const res = await fetch(`/api/projects/${pid}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${t}` }
      })
  if (!res.ok) throw new Error(translate('projects.error.delete'))
      setProjects(prev => prev.filter(p => p.id !== pid))
    } catch (err: any) {
      alert(err?.message || translate('projects.error.delete_generic'))
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
        alert(translate('projects.save.missing_search'))
        return
      }
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${t}` },
        body: JSON.stringify({
          name: `${data.keyword} (${searchLanguage}-${country})`,
          description: translate('projects.save.default_description'),
          language: searchLanguage,
          country,
          data
        })
      })
      if (!res.ok) throw new Error(translate('projects.error.save'))
      const j = await res.json()
      if (j?.id) {
        alert(translate('projects.save.success_with_id', { id: j.id }))
      } else {
        alert(translate('projects.save.success'))
      }
    } catch (err: any) {
      alert(err?.message || translate('projects.error.save_generic'))
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
        if (selectedKeyword) {
          setSelectedKeyword(null)
        } else {
          setSidebarOpen(false)
          setLangMenuAnchor(null)
          setShowCountryDropdown(false)
        }
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
          setLanguage((urlLang || data.default || DEFAULT_LANGUAGE).toLowerCase())
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

  useEffect(() => {
    fetch('/meta/markets.json')
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data) => {
        const map = new Map<string, string[]>()
        const markets = Array.isArray(data?.markets) ? data.markets : []
        markets.forEach((entry: any) => {
          const code = (entry?.code || '').toString().toUpperCase()
          if (!code || code.length !== 2) return
          const seen = new Set<string>()
          const locales: string[] = []
          const push = (value: any) => {
            if (!value) return
            const normalized = value.toString().toLowerCase()
            if (!normalized) return
            const primary = normalized.split('-')[0]
            if (!primary || seen.has(primary)) return
            seen.add(primary)
            locales.push(primary)
          }
          push(entry?.defaultLocale)
          if (Array.isArray(entry?.locales)) {
            entry.locales.forEach(push)
          }
          if (locales.length) {
            map.set(code, locales)
          }
        })
        if (map.size) {
          setMarketLocales(map)
        }
      })
      .catch(() => { /* ignore */ })
  }, [])

  useEffect(() => {
    if (!country) return
    if (languageManuallySelected) return
    const locales = marketLocales.get(country.toUpperCase())
    if (!locales || locales.length === 0) return

    const availableCodes = new Set<string>()
    languagesList.forEach((lang) => {
      const code = (lang?.code || '').toLowerCase()
      if (!code) return
      availableCodes.add(code)
      const primary = code.split('-')[0]
      if (primary) availableCodes.add(primary)
    })

    const preferred = locales.find((locale) => availableCodes.has(locale.toLowerCase()))
    if (preferred && preferred !== searchLanguage) {
      updateSearchLanguage(preferred, false)
    }
  }, [country, languageManuallySelected, marketLocales, languagesList, searchLanguage, updateSearchLanguage])

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
          if (!hasSavedLang && !pathHasLangPrefix && detLang) {
            setLanguage(detLang)
            try { localStorage.setItem('lw_lang', detLang) } catch {}
          }
          if ((!hasSavedSearchLang || !languageManuallySelected) && detLang) {
            updateSearchLanguage(detLang, false)
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
    <EntitlementsProvider value={entitlementsResult}>
      <div className="layout">
        <aside id="sidebar" className={`sidebar ${sidebarOpen ? 'open' : ''}`} aria-hidden={!sidebarOpen}>
          <div className="sidebar-brand">Lucy <span>World</span></div>
          <PlatformSidebar
          title={translate('platforms.sidebar.title')}
          platforms={visiblePlatforms}
          activePlatformId={activePlatformId}
          onSelect={(platformId) => {
            setActivePlatformId(platformId)
            setSidebarOpen(false)
          }}
        />
        {/* CTA Ribbon for free tier users */}
        {entitlementsData.tier === 'free' && (
          <div className="sidebar-cta">
            <div className="sidebar-cta-content">
              <div className="sidebar-cta-icon">⚡</div>
              <div className="sidebar-cta-text">
                <div className="sidebar-cta-title">{translate('cta.upgrade_title')}</div>
                <div className="sidebar-cta-description">{translate('cta.upgrade_description')}</div>
              </div>
            </div>
            <button
              type="button"
              className="sidebar-cta-button"
              onClick={() => {
                handleUpgradeClick()
                const dl = (window as any).dataLayer
                if (Array.isArray(dl)) {
                  dl.push({
                    event: 'cta_clicked',
                    cta_location: 'sidebar',
                    cta_type: 'upgrade',
                    user_tier: entitlementsData.tier
                  })
                }
              }}
            >
              {translate('cta.upgrade_button')}
            </button>
          </div>
        )}
        <div className="sidebar-footer">
          <span className="sidebar-footer-copy">© {new Date().getFullYear()} Lucy World</span>
        </div>
      </aside>
      <div className={`overlay ${sidebarOpen ? 'show' : ''}`} onClick={() => setSidebarOpen(false)} />

      <div className="content">
        {/* Desktop header bar */}
  <div className="desktopbar" style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', padding: '12px 14px', borderBottom: '1px solid var(--line)', position: 'sticky', top: 0, zIndex: 9, background: 'rgba(11,13,16,0.6)', backdropFilter: 'saturate(180%) blur(10px)' }}>
          <div className="brand">Lucy <span>World</span></div>
          <div
            style={{
              marginLeft: 'auto',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 10,
              flexWrap: 'wrap',
              justifyContent: 'flex-end',
              width: '100%'
            }}
          >
            {renderPlanSummary('desktop')}
            {renderBillingActions('desktop')}
            {!isSignedIn ? (
              <button
                type="button"
                onClick={() => setShowSignin(true)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
              >
                � {signInTitle}
              </button>
            ) : (
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={loadProjects}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
                >
                  � {myProjectsLabel}
                </button>
                <button
                  type="button"
                  onClick={saveProject}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
                >
                  � {saveProjectLabel}
                </button>
              </div>
            )}
            <div style={{ position: 'relative' }}>
              <button
                type="button"
                className="lang-btn"
                aria-haspopup="listbox"
                aria-expanded={langMenuAnchor === 'desktop'}
                onClick={() => toggleLangMenu('desktop')}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: 'var(--text)', border: '1px solid var(--line)', padding: '8px 10px', borderRadius: 10 }}
                title={language.toUpperCase()}
              >
                <span aria-hidden>{getLanguageFlag(language)}</span>
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
                      <span style={{ width: 22, textAlign: 'center' }} aria-hidden>{getLanguageFlag(l.code)}</span>
                      <span style={{ flex: 1 }}>{l.label || l.code.toUpperCase()}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        {/* Mobile top bar */}
        <div className="topbar">
          <button
            className="hamburger"
            aria-label={openNavigationLabel}
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
          <div
            className="topbar-actions"
            style={{
              marginLeft: 'auto',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              flexWrap: 'wrap',
              justifyContent: 'flex-end'
            }}
          >
            {renderPlanSummary('mobile')}
            {renderBillingActions('mobile')}
            {!isSignedIn ? (
              <button
                type="button"
                onClick={() => setShowSignin(true)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  background: 'transparent',
                  color: 'var(--text)',
                  border: '1px solid var(--line)',
                  padding: '8px 10px',
                  borderRadius: 10
                }}
              >
                🔐 {signInTitle}
              </button>
            ) : (
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={loadProjects}
                  aria-label={myProjectsLabel}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    background: 'transparent',
                    color: 'var(--text)',
                    border: '1px solid var(--line)',
                    padding: '8px 10px',
                    borderRadius: 10
                  }}
                >
                  📁
                </button>
                <button
                  type="button"
                  onClick={saveProject}
                  aria-label={saveProjectLabel}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    background: 'transparent',
                    color: 'var(--text)',
                    border: '1px solid var(--line)',
                    padding: '8px 10px',
                    borderRadius: 10
                  }}
                >
                  💾
                </button>
              </div>
            )}
            <div className="lang-switch" style={{ position: 'relative', zIndex: 30 }}>
              <button
                type="button"
                className="lang-btn"
                aria-haspopup="listbox"
                aria-expanded={langMenuAnchor === 'mobile'}
                onClick={() => toggleLangMenu('mobile')}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  background: 'transparent',
                  color: 'var(--text)',
                  border: '1px solid var(--line)',
                  padding: '8px 10px',
                  borderRadius: 10
                }}
                title={language.toUpperCase()}
              >
                <span aria-hidden>{getLanguageFlag(language)}</span>
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
                        display: 'flex',
                        width: '100%',
                        textAlign: 'left',
                        gap: 10,
                        padding: '10px 12px',
                        background: 'transparent',
                        color: 'var(--text)',
                        border: 0,
                        cursor: 'pointer'
                      }}
                    >
                      <span style={{ width: 22, textAlign: 'center' }} aria-hidden>{getLanguageFlag(l.code)}</span>
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
          <div
            style={{ position: 'fixed', inset: 0 as any, background: 'rgba(0,0,0,0.5)', display: 'grid', placeItems: 'center', zIndex: 50, padding: '16px' }}
            onClick={closeSigninModal}
          >
            <div
              role="dialog"
              aria-modal="true"
              aria-labelledby="signin-modal-title"
              style={{ background: '#0e1217', border: '1px solid var(--line)', borderRadius: 16, padding: 20, width: 'min(440px, 100%)', display: 'grid', gap: 16, boxShadow: '0 12px 32px rgba(0,0,0,0.35)' }}
              onClick={e => e.stopPropagation()}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
                <h3 id="signin-modal-title" style={{ margin: 0 }}>{signInTitle}</h3>
                <button
                  type="button"
                  onClick={closeSigninModal}
                  aria-label={closeLabel}
                  style={{ background: 'transparent', border: 0, color: 'var(--text)', fontSize: 20, cursor: 'pointer', lineHeight: 1 }}
                >
                  ✕
                </button>
              </div>
              <p style={{ margin: 0, opacity: 0.85 }}>{signInDescription}</p>
              <form onSubmit={requestMagicLink} style={{ display: 'grid', gap: 12 }}>
                <label style={{ display: 'grid', gap: 6 }}>
                  <span style={{ fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--muted)' }}>{signInPlaceholder}</span>
                  <input
                    type="email"
                    placeholder={signInPlaceholder}
                    value={signinEmail}
                    onChange={e => setSigninEmail(e.target.value)}
                    required
                    style={{ width: '100%' }}
                    autoFocus
                  />
                </label>
                <button
                  type="submit"
                  disabled={signinStatus === 'sending'}
                  style={{ justifyContent: 'center', display: 'inline-flex', alignItems: 'center', gap: 8 }}
                >
                  {signinStatus === 'sending'
                    ? (sendingLinkLabel === 'auth.magic_link.sending' ? 'Sending…' : sendingLinkLabel)
                    : sendLinkLabel}
                </button>
              </form>
              {signinFeedback && (
                <div
                  role="status"
                  aria-live="assertive"
                  style={{
                    marginTop: 4,
                    padding: '10px 12px',
                    borderRadius: 12,
                    border: signinStatus === 'error' ? '1px solid rgba(248,113,113,0.35)' : '1px solid rgba(74,222,128,0.35)',
                    background: signinStatus === 'error' ? 'rgba(248,113,113,0.12)' : 'rgba(74,222,128,0.12)',
                    color: signinStatus === 'error' ? '#fca5a5' : '#bbf7d0',
                    fontSize: 14,
                    display: 'flex',
                    gap: 8,
                    alignItems: 'flex-start'
                  }}
                >
                  <span aria-hidden="true">{signinStatus === 'error' ? '⚠️' : '✅'}</span>
                  <span>{signinFeedback}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {loading && (
          <div className="search-status" role="status" aria-live="polite">
            <span className="search-status__spinner" aria-hidden="true" />
            <span>{searchLoadingLabel}</span>
          </div>
        )}

        {showStickyCta && (
          <aside
            className={`sticky-cta ${isLowCredits ? 'sticky-cta--warning' : 'sticky-cta--signin'}`}
            role="complementary"
            aria-live="polite"
          >
            <button
              type="button"
              className="sticky-cta__close"
              onClick={dismissStickyCta}
              aria-label={stickyCtaDismissLabel}
            >
              ✕
            </button>
            <div className="sticky-cta__content">
              <span className="sticky-cta__eyebrow">{isLowCredits ? aiCreditsLabel : signinCtaEyebrow}</span>
              <h2 className="sticky-cta__title">{isLowCredits ? lowCreditsTitle : signinCtaTitle}</h2>
              <p className="sticky-cta__subtitle">{isLowCredits ? lowCreditsSubtitle : signinCtaSubtitle}</p>
              {isLowCredits && (
                <div className="sticky-cta__counter">{lowCreditsCounterLabel}</div>
              )}
            </div>
            <div className="sticky-cta__actions">
              <button
                type="button"
                onClick={handleStickyCtaClick}
                disabled={stickyCtaDisabled}
                className="sticky-cta__button"
              >
                {stickyCtaButtonLabel}
              </button>
            </div>
          </aside>
        )}

        {showProjects && (
          <div style={{ position: 'fixed', inset: 0 as any, background: 'rgba(0,0,0,0.5)', display: 'grid', placeItems: 'center', zIndex: 50 }} onClick={() => setShowProjects(false)}>
            <div style={{ background: '#0e1217', border: '1px solid var(--line)', borderRadius: 12, padding: 16, width: 'min(720px, 92vw)' }} onClick={e => e.stopPropagation()}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <h3 style={{ margin: 0, flex: 1 }}>{projectsTitle}</h3>
                <button onClick={() => setShowProjects(false)} aria-label={closeLabel} title={closeLabel} style={{ background: 'transparent', border: 0, color: 'var(--text)', fontSize: 20 }}>✕</button>
              </div>
              {projects.length === 0 ? (
                <p style={{ marginTop: 12 }}>{projectsEmptyMessage}</p>
              ) : (
                <div style={{ marginTop: 12, display: 'grid', gap: 8 }}>
                  {projects.map((p) => (
                    <div key={p.id} style={{ display: 'flex', alignItems: 'center', gap: 10, border: '1px solid var(--line)', borderRadius: 10, padding: '10px 12px' }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.name}</div>
                        <div style={{ opacity: 0.7, fontSize: 12 }}>{[(p.language || '').toUpperCase(), p.country]?.filter(Boolean).join(' • ')}{p.updated_at ? ` • ${new Date(p.updated_at).toLocaleString()}` : ''}</div>
                      </div>
                      <div style={{ display: 'inline-flex', gap: 8 }}>
                        <button onClick={() => openProject(p.id)} title={openLabel} style={{ background: 'transparent', border: '1px solid var(--line)', borderRadius: 8, color: 'var(--text)', padding: '6px 10px' }}>{openLabel}</button>
                        <button onClick={() => renameProject(p.id)} title={renameLabel} style={{ background: 'transparent', border: '1px solid var(--line)', borderRadius: 8, color: 'var(--text)', padding: '6px 10px' }}>{renameLabel}</button>
                        <button onClick={() => deleteProject(p.id)} title={deleteLabel} style={{ background: 'transparent', border: '1px solid var(--line)', borderRadius: 8, color: 'var(--text)', padding: '6px 10px' }}>{deleteLabel}</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
        {error && (
          <div className="error">{error}</div>
        )}

        {!isSignedIn && (
          <div
            className="card"
            style={{
              marginTop: 24,
              padding: 24,
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              gap: 16,
              justifyContent: 'space-between'
            }}
          >
            <div style={{ flex: '1 1 220px', minWidth: 220 }}>
              <h3 style={{ marginTop: 0, marginBottom: 8 }}>{signInTitle}</h3>
              <p style={{ margin: 0, opacity: 0.85 }}>{signInDescription}</p>
            </div>
            <button
              type="button"
              onClick={() => setShowSignin(true)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                background: 'var(--accent)',
                color: '#050607',
                border: 0,
                borderRadius: 10,
                padding: '10px 18px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              🔐 {signInTitle}
            </button>
          </div>
        )}

        {ActivePlatformTool && activePlatform && (
          <RequireEntitlement
            group={activePlatform.group}
            fallback={(
              <div className="card" style={{ marginTop: 24, padding: 24, textAlign: 'center' }}>
                <p style={{ marginBottom: 16 }}>{lockedModuleMessage}</p>
                <button
                  type="button"
                  onClick={handleUpgradeClick}
                  disabled={billingLoading}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 8,
                    padding: '10px 16px',
                    borderRadius: 10,
                    border: '1px solid var(--line)',
                    color: 'var(--text)',
                    background: 'transparent',
                    fontWeight: 600,
                    cursor: billingLoading ? 'wait' : 'pointer'
                  }}
                >
                  🚀 {billingLoading ? checkoutLaunchingLabel : upgradeNowLabel}
                </button>
              </div>
            )}
          >
            <>
              <Suspense
                fallback={
                  <div className="card" style={{ marginTop: 24, padding: 24 }}>
                    {translate('platforms.common.placeholder.loading')}
                  </div>
                }
              >
                <ActivePlatformTool
                  keyword={keyword}
                  setKeyword={setKeyword}
                  ui={ui}
                  loading={loading}
                  error={error}
                  data={data}
                  setData={setData}
                  searchLanguage={searchLanguage}
                  setSearchLanguage={updateSearchLanguage}
                  languagesList={languagesList}
                  country={country}
                  setCountry={setCountry}
                  countriesList={countriesList}
                  filteredCountries={filteredCountries}
                  showCountryDropdown={showCountryDropdown}
                  setShowCountryDropdown={setShowCountryDropdown}
                  countrySearchTerm={countrySearchTerm}
                  setCountrySearchTerm={setCountrySearchTerm}
                  getCountryName={getCountryName}
                  flagEmoji={flagEmoji}
                  categoryOrder={categoryOrder}
                  formatNumber={nl}
                  onGlobalSearch={runGlobalSearch}
                  globalLoading={loading}
                  locationControls={locationControls}
                />
              </Suspense>
              <div className="hint" style={{ marginTop: 12 }}>{ui?.strings['search.hint'] || 'Premium suggestions and trends. Results appear below.'}</div>
              <div className="hint" style={{ opacity: 0.8 }}>
                {ui?.strings['hint.site_vs_search'] || 'Use the selectors to choose the search country and language. Change the site interface language from the top menu.'}
              </div>
            </>
          </RequireEntitlement>
        )}

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
                          <button
                            key={idx}
                            className="pill pill-clickable"
                            onClick={() => {
                              setSelectedKeyword({ keyword: it.keyword, search_volume: it.search_volume || 0, category: cat })
                              if (typeof window !== 'undefined' && (window as any).dataLayer) {
                                ;(window as any).dataLayer.push({
                                  event: 'keyword_detail_opened',
                                  keyword: it.keyword,
                                  category: cat
                                })
                              }
                            }}
                          >
                            {it.keyword} · {nl(it.search_volume)}
                          </button>
                        ))}
                      </div>
                    </div>
                  )
                })}
            </section>

            {/* Keyword Detail Drawer */}
            {selectedKeyword && (
              <div className="keyword-drawer-backdrop" onClick={() => setSelectedKeyword(null)}>
                <div className="keyword-drawer" onClick={(e) => e.stopPropagation()}>
                  <div className="drawer-header">
                    <h3>{selectedKeyword.keyword}</h3>
                    <button className="btn-close" onClick={() => setSelectedKeyword(null)} aria-label={translate('actions.close') || 'Close'}>
                      ×
                    </button>
                  </div>
                  <div className="drawer-content">
                    <div className="metric-grid">
                      <div className="metric-card">
                        <label>{translate('metrics.search_volume') || 'Search Volume'}</label>
                        <div className="metric-value">{nl(selectedKeyword.search_volume)}</div>
                      </div>
                      <div className="metric-card">
                        <label>{translate('metrics.category') || 'Category'}</label>
                        <div className="metric-value">{selectedKeyword.category.replace(/_/g, ' ')}</div>
                      </div>
                    </div>
                    <div className="drawer-actions">
                      <button 
                        className="btn-secondary"
                        onClick={() => {
                          navigator.clipboard.writeText(selectedKeyword.keyword)
                          alert(translate('actions.copied') || 'Copied to clipboard!')
                        }}
                      >
                        {translate('actions.copy') || 'Copy Keyword'}
                      </button>
                      <button 
                        className="btn-primary"
                        onClick={() => {
                          const csv = `keyword,search_volume,category\n"${selectedKeyword.keyword}",${selectedKeyword.search_volume},"${selectedKeyword.category}"`
                          const blob = new Blob([csv], { type: 'text/csv' })
                          const url = URL.createObjectURL(blob)
                          const a = document.createElement('a')
                          a.href = url
                          a.download = `${selectedKeyword.keyword}.csv`
                          a.click()
                          URL.revokeObjectURL(url)
                        }}
                      >
                        {translate('actions.export') || 'Export CSV'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        <footer className="footer">
          © {new Date().getFullYear()} Lucy World
        </footer>
      </div>
    </div>
      </div>
    </EntitlementsProvider>
  )
}
