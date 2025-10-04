import React from 'react'
import type { PlatformConfig } from '../types'
import '../styles/sidebar.css'

type PlatformSidebarProps = {
  title?: string
  platforms: PlatformConfig[]
  activePlatformId: string
  onSelect: (platformId: string) => void
}

const PlatformSidebar: React.FC<PlatformSidebarProps> = ({ title = 'Platforms', platforms, activePlatformId, onSelect }) => {
  if (!platforms.length) {
    return null
  }

  return (
    <div className="platform-sidebar">
      <h4 className="platform-sidebar__title">{title}</h4>
      <ul className="platform-sidebar__list">
        {platforms.map((platform) => {
          const isActive = platform.id === activePlatformId
          return (
            <li key={platform.id}>
              <button
                type="button"
                className={`platform-sidebar__item${isActive ? ' platform-sidebar__item--active' : ''}`}
                onClick={() => onSelect(platform.id)}
                aria-pressed={isActive}
                title={platform.description}
              >
                <span className="platform-sidebar__icon" aria-hidden>
                  <img src={platform.icon} alt="" loading="lazy" />
                </span>
                <span className="platform-sidebar__label">{platform.name}</span>
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

export default PlatformSidebar
