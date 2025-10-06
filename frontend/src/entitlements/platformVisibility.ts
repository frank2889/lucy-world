import type { PlatformConfig } from '../platforms/types'
import type { SidebarGroupKey } from './types'

const ensureArray = <T>(input: readonly T[] | T[]): T[] => {
  if (Array.isArray(input)) {
    return [...input]
  }
  return []
}

export function filterPlatformsByEntitlements(
  platforms: PlatformConfig[],
  allowedGroups: readonly SidebarGroupKey[]
): PlatformConfig[] {
  if (!platforms.length) {
    return platforms
  }

  const allowedSet = new Set(ensureArray(allowedGroups))
  if (allowedSet.size === 0) {
    return platforms
  }

  const filtered = platforms.filter((platform) => allowedSet.has(platform.group as SidebarGroupKey))
  if (filtered.length === 0) {
    return platforms
  }

  return filtered
}
