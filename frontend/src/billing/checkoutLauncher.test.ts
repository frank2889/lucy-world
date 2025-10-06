import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { launchUpgradeCheckout } from './checkoutLauncher'

type Setter<T> = (value: T | ((prev: T) => T)) => void

describe('launchUpgradeCheckout', () => {
  const labels = {
    upgradeUnavailable: 'Upgrade unavailable',
    upgradeRequiresSignin: 'Sign in required',
    checkoutFailed: 'Checkout failed'
  }

  let setBillingLoading: Setter<boolean>
  let setError: Setter<string | null>
  let setShowSignin: Setter<boolean>
  let billingLoadingSpy: ReturnType<typeof vi.fn>
  let errorSpy: ReturnType<typeof vi.fn>
  let showSigninSpy: ReturnType<typeof vi.fn>

  beforeEach(() => {
    billingLoadingSpy = vi.fn()
    errorSpy = vi.fn()
    showSigninSpy = vi.fn()
    setBillingLoading = billingLoadingSpy
    setError = errorSpy
    setShowSignin = showSigninSpy
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('opens external URLs in a new tab without hitting the checkout endpoint', async () => {
    const windowMock = { open: vi.fn(), location: { href: '' } }
  const fetchMock = vi.fn<typeof fetch>()

    await launchUpgradeCheckout({
      upgradeUrl: 'https://stripe.com/upgrade',
      token: 'token',
      billingLoading: false,
      setBillingLoading,
      setError,
      setShowSignin,
      labels,
      fetchImpl: fetchMock,
      windowImpl: windowMock
    })

    expect(windowMock.open).toHaveBeenCalledWith('https://stripe.com/upgrade', '_blank', 'noopener,noreferrer')
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('navigates internally when upgrade URL is not the checkout endpoint', async () => {
    const windowMock = { open: vi.fn(), location: { href: '' } }

    await launchUpgradeCheckout({
      upgradeUrl: '/billing/manage',
      token: 'token',
      billingLoading: false,
      setBillingLoading,
      setError,
      setShowSignin,
      labels,
      windowImpl: windowMock
    })

    expect(windowMock.location.href).toBe('/billing/manage')
  })

  it('requests sign-in when checkout fallback is used without a token', async () => {
    await launchUpgradeCheckout({
      upgradeUrl: '/billing/upgrade',
      token: null,
      billingLoading: false,
      setBillingLoading,
      setError,
      setShowSignin,
      labels
    })

    expect(showSigninSpy).toHaveBeenCalledWith(true)
    expect(errorSpy).toHaveBeenCalledWith('Sign in required')
  })

  it('short-circuits when already loading', async () => {
  const fetchMock = vi.fn<typeof fetch>()

    await launchUpgradeCheckout({
      upgradeUrl: '/billing/upgrade',
      token: 'token',
      billingLoading: true,
      setBillingLoading,
      setError,
      setShowSignin,
      labels,
      fetchImpl: fetchMock
    })

    expect(fetchMock).not.toHaveBeenCalled()
    expect(billingLoadingSpy).not.toHaveBeenCalled()
  })

  it('calls checkout endpoint and redirects to the returned URL', async () => {
    const windowMock = { open: vi.fn(), location: { href: '' } }
    const fetchMock = vi.fn<typeof fetch>(async () =>
      new Response(JSON.stringify({ url: 'https://checkout.stripe.com/session' }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json'
        }
      })
    )

    await launchUpgradeCheckout({
      upgradeUrl: '/billing/upgrade',
      token: 'token',
      billingLoading: false,
      setBillingLoading,
      setError,
      setShowSignin,
      labels,
      fetchImpl: fetchMock,
      windowImpl: windowMock
    })

    expect(fetchMock).toHaveBeenCalledWith('/api/billing/checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer token'
      }
    })
    expect(billingLoadingSpy).toHaveBeenNthCalledWith(1, true)
    expect(billingLoadingSpy).toHaveBeenLastCalledWith(false)
    expect(errorSpy).toHaveBeenNthCalledWith(1, null)
    expect(windowMock.location.href).toBe('https://checkout.stripe.com/session')
  })

  it('prompts for sign in when checkout endpoint returns 401', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const fetchMock = vi.fn<typeof fetch>(async () =>
      new Response(JSON.stringify({ message: 'Unauthorized' }), {
        status: 401,
        headers: {
          'Content-Type': 'application/json'
        }
      })
    )

    await launchUpgradeCheckout({
      upgradeUrl: '/billing/upgrade',
      token: 'token',
      billingLoading: false,
      setBillingLoading,
      setError,
      setShowSignin,
      labels,
      fetchImpl: fetchMock
    })

    expect(showSigninSpy).toHaveBeenCalledWith(true)
    expect(errorSpy).toHaveBeenCalledWith('Sign in required')
    expect(consoleSpy).not.toHaveBeenCalled()
    expect(billingLoadingSpy).toHaveBeenNthCalledWith(1, true)
    expect(billingLoadingSpy).toHaveBeenLastCalledWith(false)
  })

  it('sets error when checkout endpoint responds without a URL', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const fetchMock = vi.fn<typeof fetch>(async () =>
      new Response(JSON.stringify({}), {
        status: 200,
        headers: {
          'Content-Type': 'application/json'
        }
      })
    )

    await launchUpgradeCheckout({
      upgradeUrl: '/billing/upgrade',
      token: 'token',
      billingLoading: false,
      setBillingLoading,
      setError,
      setShowSignin,
      labels,
      fetchImpl: fetchMock
    })

    expect(consoleSpy).toHaveBeenCalled()
    expect(errorSpy).toHaveBeenLastCalledWith('Checkout failed')
    expect(billingLoadingSpy).toHaveBeenNthCalledWith(1, true)
    expect(billingLoadingSpy).toHaveBeenLastCalledWith(false)
  })

  it('handles network failures gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const fetchMock = vi.fn<typeof fetch>(async () => {
      throw new Error('network')
    })

    await launchUpgradeCheckout({
      upgradeUrl: '/billing/upgrade',
      token: 'token',
      billingLoading: false,
      setBillingLoading,
      setError,
      setShowSignin,
      labels,
      fetchImpl: fetchMock
    })

    expect(consoleSpy).toHaveBeenCalled()
    expect(errorSpy).toHaveBeenLastCalledWith('Checkout failed')
    expect(billingLoadingSpy).toHaveBeenNthCalledWith(1, true)
    expect(billingLoadingSpy).toHaveBeenLastCalledWith(false)
  })

  it('surfaces upgrade unavailable error when URL is empty', async () => {
    await launchUpgradeCheckout({
      upgradeUrl: '    ',
      token: 'token',
      billingLoading: false,
      setBillingLoading,
      setError,
      setShowSignin,
      labels
    })

    expect(errorSpy).toHaveBeenCalledWith('Upgrade unavailable')
  })
})
