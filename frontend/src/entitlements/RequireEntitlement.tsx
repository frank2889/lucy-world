import React from 'react'
import type { ReactNode } from 'react'
import type { SidebarGroupKey } from './types'
import { useEntitlementsContext } from './context'

export type RequireEntitlementProps = {
  group?: SidebarGroupKey
  minimumAiCredits?: number
  fallback?: ReactNode
  children: ReactNode
}

export const RequireEntitlement: React.FC<RequireEntitlementProps> = ({
  group,
  minimumAiCredits = 0,
  fallback = null,
  children
}) => {
  const { entitlements, status, isGroupEnabled } = useEntitlementsContext()

  const satisfiesGroup = group ? isGroupEnabled(group) : true
  const satisfiesCredits = entitlements.ai_credits >= minimumAiCredits
  const canRender = satisfiesGroup && satisfiesCredits

  if (status === 'loading' && !canRender) {
    return null
  }

  return <>{canRender ? children : fallback}</>
}
