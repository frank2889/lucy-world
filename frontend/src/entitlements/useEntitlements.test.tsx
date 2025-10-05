import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi, afterEach } from 'vitest'
import { DEFAULT_ENTITLEMENTS, useEntitlements } from './useEntitlements'

describe('useEntitlements', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  it('normalizes payloads and resolves success state', async () => {
    const payload = {
      tier: 'PRO',
      ai_credits: 42.9,
      sidebar_groups: ['social', 'ai', 'search', 'ai'],
      upgrade_url: '   ',
      buy_credits_url: '/buy',
      expires_at: '2025-12-01T00:00:00Z'
    }

    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload)
    })

    vi.stubGlobal('fetch', fetchSpy)

    const { result } = renderHook(() => useEntitlements(null))

    await waitFor(() => {
      expect(result.current.status).toBe('success')
    })

    expect(fetchSpy).toHaveBeenCalledTimes(1)
    expect(result.current.entitlements).toEqual({
      tier: 'pro',
      ai_credits: 42,
      sidebar_groups: ['social', 'ai', 'search'],
      upgrade_url: '/billing/upgrade',
      buy_credits_url: '/buy',
      expires_at: '2025-12-01T00:00:00Z'
    })
  })

  it('falls back to defaults and error state when request fails', async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: false,
      status: 500
    })

    vi.stubGlobal('fetch', fetchSpy)

    const { result } = renderHook(() => useEntitlements(null))

    await waitFor(() => {
      expect(result.current.status).toBe('error')
    })

    expect(result.current.entitlements).toEqual(DEFAULT_ENTITLEMENTS)
  })

  it('sends authorization header and allows manual refresh', async () => {
    const firstResponse = {
      ok: true,
      json: () => Promise.resolve({
        tier: 'pro',
        ai_credits: 5,
        sidebar_groups: ['search', 'marketplaces']
      })
    }

    const secondResponse = {
      ok: true,
      json: () => Promise.resolve({
        tier: 'enterprise',
        ai_credits: 10,
        sidebar_groups: ['search', 'marketplaces', 'social', 'video']
      })
    }

    const fetchSpy = vi.fn()
      .mockResolvedValueOnce(firstResponse)
      .mockResolvedValueOnce(secondResponse)

    vi.stubGlobal('fetch', fetchSpy)

    const { result } = renderHook(() => useEntitlements('abc123'))

    await waitFor(() => {
      expect(result.current.status).toBe('success')
    })

    expect(fetchSpy).toHaveBeenCalled()
    expect(fetchSpy.mock.calls[0]?.[1]?.headers).toEqual({ Authorization: 'Bearer abc123' })

    await act(async () => {
      await result.current.refresh({ token: 'xyz999' })
    })

    expect(fetchSpy).toHaveBeenCalledTimes(2)
    expect(fetchSpy.mock.calls[1]?.[1]?.headers).toEqual({ Authorization: 'Bearer xyz999' })
    expect(result.current.entitlements.tier).toBe('enterprise')
  })
})
