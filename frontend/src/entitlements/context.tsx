import React, { createContext, useContext, useMemo } from 'react'
import type { ReactNode } from 'react'
import type { SidebarGroupKey, SubscriptionTier } from './types'
import type { UseEntitlementsResult } from './useEntitlements'

export type EntitlementsContextValue = UseEntitlementsResult & {
  tier: SubscriptionTier
  hasAiCredits: boolean
  isGroupEnabled: (group: SidebarGroupKey) => boolean
}

const EntitlementsContext = createContext<EntitlementsContextValue | undefined>(undefined)

export function EntitlementsProvider({ value, children }: { value: UseEntitlementsResult; children: ReactNode }) {
  const memoized = useMemo<EntitlementsContextValue>(() => {
    const groups = new Set(value.entitlements.sidebar_groups)
    const isGroupEnabled = (group: SidebarGroupKey) => groups.has(group)

    return {
      ...value,
      tier: value.entitlements.tier,
      hasAiCredits: value.entitlements.ai_credits > 0,
      isGroupEnabled
    }
  }, [value.entitlements, value.status, value.error, value.refresh])

  return <EntitlementsContext.Provider value={memoized}>{children}</EntitlementsContext.Provider>
}

export function useEntitlementsContext(): EntitlementsContextValue {
  const context = useContext(EntitlementsContext)
  if (!context) {
    throw new Error('useEntitlementsContext must be used within an EntitlementsProvider')
  }
  return context
}
