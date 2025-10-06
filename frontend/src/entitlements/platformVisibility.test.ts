import { describe, expect, it } from 'vitest'
import { filterPlatformsByEntitlements } from './platformVisibility'
import type { PlatformConfig } from '../platforms/types'
import type { SidebarGroupKey } from './types'

const stubPlatform = (id: string, group: SidebarGroupKey): PlatformConfig => ({
  id,
  name: id,
  icon: `/icons/${id}.svg`,
  description: `${id} description`,
  tool: (() => null) as unknown as PlatformConfig['tool'],
  group
})

describe('filterPlatformsByEntitlements', () => {
  const platforms = [
    stubPlatform('google', 'search'),
    stubPlatform('amazon', 'marketplaces'),
    stubPlatform('tiktok', 'social'),
    stubPlatform('youtube', 'video')
  ]

  it('keeps only platforms whose groups are allowed', () => {
    const result = filterPlatformsByEntitlements(platforms, ['search', 'marketplaces'])
    expect(result.map((p) => p.id)).toEqual(['google', 'amazon'])
  })

  it('falls back to original list when no allowed groups are provided', () => {
    expect(filterPlatformsByEntitlements(platforms, [])).toEqual(platforms)
  })

  it('returns original list when filtering removes everything', () => {
    const result = filterPlatformsByEntitlements(platforms, ['ai'])
    expect(result).toEqual(platforms)
  })
})
