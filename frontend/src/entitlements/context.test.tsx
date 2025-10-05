import React from 'react'
import { describe, expect, it, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { DEFAULT_ENTITLEMENTS } from './useEntitlements'
import { EntitlementsProvider, useEntitlementsContext } from './context'

describe('EntitlementsContext', () => {
  it('exposes derived helpers from provider', () => {
    const refresh = vi.fn(async () => DEFAULT_ENTITLEMENTS)
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <EntitlementsProvider
        value={{
          entitlements: { ...DEFAULT_ENTITLEMENTS, tier: 'pro', ai_credits: 5, sidebar_groups: ['search', 'ai'] },
          status: 'success',
          error: null,
          refresh
        }}
      >
        {children}
      </EntitlementsProvider>
    )

    const { result } = renderHook(() => useEntitlementsContext(), { wrapper })

    expect(result.current.tier).toBe('pro')
    expect(result.current.hasAiCredits).toBe(true)
    expect(result.current.isGroupEnabled('ai')).toBe(true)
    expect(result.current.isGroupEnabled('video')).toBe(false)
  })

  it('throws when used outside provider', () => {
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => renderHook(() => useEntitlementsContext())).toThrowError(
      'useEntitlementsContext must be used within an EntitlementsProvider'
    )
    errorSpy.mockRestore()
  })
})
