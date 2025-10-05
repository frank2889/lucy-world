export type SidebarGroupKey = 'search' | 'marketplaces' | 'social' | 'video' | 'ai' | 'enterprise'

export type SubscriptionTier = 'free' | 'pro' | 'enterprise'

export interface EntitlementsPayload {
  tier: SubscriptionTier
  ai_credits: number
  sidebar_groups: SidebarGroupKey[]
  upgrade_url: string
  buy_credits_url: string
  expires_at?: string
}

export type EntitlementsStatus = 'idle' | 'loading' | 'success' | 'error'
