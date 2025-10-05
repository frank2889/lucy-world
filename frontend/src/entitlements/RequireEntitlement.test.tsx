import React from 'react'
import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EntitlementsProvider } from './context'
import { RequireEntitlement } from './RequireEntitlement'
import { DEFAULT_ENTITLEMENTS } from './useEntitlements'

const renderWithEntitlements = (value: React.ComponentProps<typeof EntitlementsProvider>['value'], ui: React.ReactNode) => {
  return render(<EntitlementsProvider value={value}>{ui}</EntitlementsProvider>)
}

describe('RequireEntitlement', () => {
  it('renders children when entitlements satisfy requirements', () => {
    const refresh = vi.fn(async () => DEFAULT_ENTITLEMENTS)

    renderWithEntitlements(
      {
        entitlements: { ...DEFAULT_ENTITLEMENTS, sidebar_groups: ['search', 'ai'], ai_credits: 3 },
        status: 'success',
        error: null,
        refresh
      },
      <RequireEntitlement group="ai" minimumAiCredits={1}>
        <div>ai-content</div>
      </RequireEntitlement>
    )

    expect(screen.getByText('ai-content')).toBeInTheDocument()
  })

  it('renders fallback when requirements are not met', () => {
    const refresh = vi.fn(async () => DEFAULT_ENTITLEMENTS)

    renderWithEntitlements(
      {
        entitlements: { ...DEFAULT_ENTITLEMENTS, sidebar_groups: ['search'], ai_credits: 0 },
        status: 'success',
        error: null,
        refresh
      },
      <RequireEntitlement group="ai" minimumAiCredits={1} fallback={<div>no-access</div>}>
        <div>ai-content</div>
      </RequireEntitlement>
    )

    expect(screen.queryByText('ai-content')).not.toBeInTheDocument()
    expect(screen.getByText('no-access')).toBeInTheDocument()
  })

  it('does not render fallback while entitlements are loading', () => {
    const refresh = vi.fn(async () => DEFAULT_ENTITLEMENTS)

    renderWithEntitlements(
      {
        entitlements: { ...DEFAULT_ENTITLEMENTS },
        status: 'loading',
        error: null,
        refresh
      },
      <RequireEntitlement group="ai" minimumAiCredits={1} fallback={<div>no-access</div>}>
        <div>ai-content</div>
      </RequireEntitlement>
    )

    expect(screen.queryByText('ai-content')).not.toBeInTheDocument()
    expect(screen.queryByText('no-access')).not.toBeInTheDocument()
  })
})
