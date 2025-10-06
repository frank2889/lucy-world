type StateSetter<T> = (value: T | ((prev: T) => T)) => void

type CheckoutLabels = {
  upgradeUnavailable: string
  upgradeRequiresSignin: string
  checkoutFailed: string
}

type WindowLike = {
  open?: (url: string, target?: string, features?: string) => void
  location?: {
    href: string
  }
}

type LaunchUpgradeCheckoutOptions = {
  upgradeUrl: string | null | undefined
  token: string | null
  billingLoading: boolean
  setBillingLoading: StateSetter<boolean>
  setError: StateSetter<string | null>
  setShowSignin: StateSetter<boolean>
  labels: CheckoutLabels
  fetchImpl?: typeof fetch
  windowImpl?: WindowLike
}

const defaultWindow: WindowLike | undefined = typeof window !== 'undefined' ? window : undefined

export async function launchUpgradeCheckout({
  upgradeUrl,
  token,
  billingLoading,
  setBillingLoading,
  setError,
  setShowSignin,
  labels,
  fetchImpl = fetch,
  windowImpl = defaultWindow
}: LaunchUpgradeCheckoutOptions): Promise<void> {
  const target = typeof upgradeUrl === 'string' ? upgradeUrl.trim() : ''
  if (!target) {
    setError(labels.upgradeUnavailable)
    return
  }

  const lowerTarget = target.toLowerCase()
  const isExternal = /^https?:\/\//i.test(target) || lowerTarget.startsWith('mailto:')
  const normalizedPath = target.startsWith('/') ? target : `/${target}`
  const shouldUseCheckoutEndpoint = normalizedPath === '/billing/upgrade'

  if (isExternal || !shouldUseCheckoutEndpoint) {
    if (!windowImpl) {
      return
    }
    if (isExternal) {
      windowImpl.open?.(target, '_blank', 'noopener,noreferrer')
    } else if (windowImpl.location) {
      windowImpl.location.href = target
    }
    return
  }

  if (!token) {
    setShowSignin(true)
    setError(labels.upgradeRequiresSignin)
    return
  }

  if (billingLoading) {
    return
  }

  setBillingLoading(true)
  setError(null)

  try {
    const response = await fetchImpl('/api/billing/checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      }
    })

    if (response.status === 401) {
      setShowSignin(true)
      setError(labels.upgradeRequiresSignin)
      return
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const payload = await response.json()
    const checkoutUrl = typeof payload?.url === 'string' ? payload.url.trim() : ''
    if (!checkoutUrl) {
      throw new Error('missing_checkout_url')
    }

    if (!windowImpl || !windowImpl.location) {
      throw new Error('window_unavailable')
    }

    windowImpl.location.href = checkoutUrl
  } catch (error) {
    console.error('Failed to initiate checkout session', error)
    setError(labels.checkoutFailed)
  } finally {
    setBillingLoading(false)
  }
}
