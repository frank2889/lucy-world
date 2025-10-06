import React from 'react'
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import PlatformSidebar from './PlatformSidebar'
import { filterPlatformsByEntitlements } from '../../entitlements/platformVisibility'
import type { PlatformConfig } from '../types'
import type { SidebarGroupKey } from '../../entitlements/types'

type PlatformSeed = Pick<PlatformConfig, 'id' | 'name' | 'icon' | 'description' | 'group' | 'tool'>

const stubPlatform = (config: PlatformSeed): PlatformConfig => ({
  ...config,
  tool: config.tool
})

const PLATFORMS: PlatformConfig[] = [
  stubPlatform({
    id: 'google',
    name: 'Google Search',
    icon: '/icons/google.svg',
    description: 'Search engine',
    group: 'search',
  tool: (() => null) as unknown as PlatformConfig['tool']
  }),
  stubPlatform({
    id: 'amazon',
    name: 'Amazon Marketplace',
    icon: '/icons/amazon.svg',
    description: 'Marketplace',
    group: 'marketplaces',
  tool: (() => null) as unknown as PlatformConfig['tool']
  }),
  stubPlatform({
    id: 'labs',
    name: 'AI Labs',
    icon: '/icons/ai.svg',
    description: 'AI workspace',
    group: 'ai',
  tool: (() => null) as unknown as PlatformConfig['tool']
  })
]

describe('PlatformSidebar entitlement rendering', () => {
  const renderSidebar = (allowedGroups: SidebarGroupKey[]) => {
    const visible = filterPlatformsByEntitlements(PLATFORMS, allowedGroups)
    const activeId = visible[0]?.id ?? ''
    render(
      <PlatformSidebar
        title="Platforms"
        platforms={visible}
        activePlatformId={activeId}
        onSelect={() => {}}
      />
    )
  }

  it('shows only free search modules when limited to search group', () => {
    renderSidebar(['search'])

    expect(screen.getByText('Google Search')).toBeInTheDocument()
    expect(screen.queryByText('Amazon Marketplace')).not.toBeInTheDocument()
    expect(screen.queryByText('AI Labs')).not.toBeInTheDocument()
  })

  it('includes marketplace modules for pro entitlements', () => {
    renderSidebar(['search', 'marketplaces'])

    expect(screen.getByText('Google Search')).toBeInTheDocument()
    expect(screen.getByText('Amazon Marketplace')).toBeInTheDocument()
    expect(screen.queryByText('AI Labs')).not.toBeInTheDocument()
  })

  it('unlocks AI modules when ai credits are available', () => {
    renderSidebar(['search', 'marketplaces', 'ai'])

    expect(screen.getByText('AI Labs')).toBeInTheDocument()
  })
})
