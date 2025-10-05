import { useCallback, useEffect, useRef, useState } from 'react'
import type { EntitlementsPayload, EntitlementsStatus, SidebarGroupKey, SubscriptionTier } from './types'

const VALID_SIDEBAR_GROUPS: readonly SidebarGroupKey[] = ['search', 'marketplaces', 'social', 'video', 'ai', 'enterprise'] as const
const VALID_TIERS: readonly SubscriptionTier[] = ['free', 'pro', 'enterprise'] as const

const DEFAULT_GROUP: SidebarGroupKey = 'search'
const DEFAULT_UPGRADE_URL = '/billing/upgrade'
const DEFAULT_CREDITS_URL = '/billing/credits'

export const DEFAULT_ENTITLEMENTS: EntitlementsPayload = {
  tier: 'free',
  ai_credits: 0,
  sidebar_groups: [DEFAULT_GROUP],
  upgrade_url: DEFAULT_UPGRADE_URL,
  buy_credits_url: DEFAULT_CREDITS_URL,
}

export type RefreshOptions = {
  token?: string | null
  signal?: AbortSignal
}

export type UseEntitlementsResult = {
  entitlements: EntitlementsPayload
  status: EntitlementsStatus
  error: string | null
  refresh: (options?: RefreshOptions) => Promise<EntitlementsPayload | null>
}

const sidebarGroupSet = new Set(VALID_SIDEBAR_GROUPS)
const tierSet = new Set(VALID_TIERS)

function isSidebarGroup(value: string): value is SidebarGroupKey {
  return sidebarGroupSet.has(value as SidebarGroupKey)
}

function normalizeSidebarGroups(input: unknown): SidebarGroupKey[] {
  const raw = Array.isArray(input) ? input : []
  const normalized: SidebarGroupKey[] = []

  for (const entry of raw) {
    if (typeof entry !== 'string') continue
    const candidate = entry.trim().toLowerCase()
    if (!isSidebarGroup(candidate)) continue
    if (!normalized.includes(candidate)) {
      normalized.push(candidate)
    }
  }

  if (!normalized.includes(DEFAULT_GROUP)) {
    normalized.unshift(DEFAULT_GROUP)
  }

  return normalized
}

function normalizeTier(value: unknown): SubscriptionTier {
  if (typeof value === 'string') {
    const candidate = value.trim().toLowerCase()
    if (tierSet.has(candidate as SubscriptionTier)) {
      return candidate as SubscriptionTier
    }
  }
  return 'free'
}

function normalizeAiCredits(value: unknown): number {
  const credits = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(credits) || Number.isNaN(credits)) {
    return 0
  }
  return Math.max(0, Math.floor(credits))
}

function normalizeUrl(value: unknown, fallback: string): string {
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (trimmed.length > 0) {
      return trimmed
    }
  }
  return fallback
}

function normalizeExpiresAt(value: unknown): string | undefined {
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (trimmed.length > 0) {
      return trimmed
    }
  }
  return undefined
}

export function normalizeEntitlements(payload: Partial<EntitlementsPayload> | null | undefined): EntitlementsPayload {
  if (!payload || typeof payload !== 'object') {
    return { ...DEFAULT_ENTITLEMENTS }
  }

  const tier = normalizeTier((payload as EntitlementsPayload).tier)
  const aiCredits = normalizeAiCredits((payload as EntitlementsPayload).ai_credits)
  const sidebarGroups = normalizeSidebarGroups((payload as EntitlementsPayload).sidebar_groups)
  const upgradeUrl = normalizeUrl((payload as EntitlementsPayload).upgrade_url, DEFAULT_UPGRADE_URL)
  const buyCreditsUrl = normalizeUrl((payload as EntitlementsPayload).buy_credits_url, DEFAULT_CREDITS_URL)
  const expiresAt = normalizeExpiresAt((payload as EntitlementsPayload).expires_at)

  return {
    tier,
    ai_credits: aiCredits,
    sidebar_groups: sidebarGroups,
    upgrade_url: upgradeUrl,
    buy_credits_url: buyCreditsUrl,
    ...(expiresAt ? { expires_at: expiresAt } : {}),
  }
}

export function useEntitlements(token: string | null): UseEntitlementsResult {
  const [entitlements, setEntitlements] = useState<EntitlementsPayload>(DEFAULT_ENTITLEMENTS)
  const [status, setStatus] = useState<EntitlementsStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const tokenRef = useRef<string | null>(token)

  useEffect(() => {
    tokenRef.current = token
  }, [token])

  const refresh = useCallback(async (options: RefreshOptions = {}) => {
    const currentToken = (options.token ?? tokenRef.current ?? '').trim()
    const signal = options.signal

    setStatus('loading')
    setError(null)

    try {
      const response = await fetch('/api/entitlements', {
        method: 'GET',
        headers: currentToken ? { Authorization: `Bearer ${currentToken}` } : undefined,
        signal,
      })

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }

      const json = await response.json()
      if (signal?.aborted) {
        return null
      }

      const normalized = normalizeEntitlements(json)
      setEntitlements(normalized)
      setStatus('success')
      return normalized
    } catch (err: unknown) {
      if (signal?.aborted) {
        return null
      }
      const message = err instanceof Error ? err.message : 'Unable to load entitlements'
      setEntitlements(DEFAULT_ENTITLEMENTS)
      setStatus('error')
      setError(message)
      return null
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    refresh({ token, signal: controller.signal })
    return () => controller.abort()
  }, [token, refresh])

  return {
    entitlements,
    status,
    error,
    refresh,
  }
}
