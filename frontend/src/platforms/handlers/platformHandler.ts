import { useEffect, useMemo, useState } from 'react'
import { platformsConfig, DEFAULT_PLATFORM_ID } from '../config/platformsConfig'
import type { PlatformConfig } from '../types'

export const usePlatformHandler = (
  initialId: string = DEFAULT_PLATFORM_ID,
  availablePlatforms?: PlatformConfig[]
) => {
  const config = (availablePlatforms && availablePlatforms.length > 0) ? availablePlatforms : platformsConfig
  const [activePlatformId, setActivePlatformId] = useState(initialId)

  useEffect(() => {
    if (!config.some((platform) => platform.id === activePlatformId)) {
      setActivePlatformId(config[0]?.id ?? DEFAULT_PLATFORM_ID)
    }
  }, [config, activePlatformId])

  const activePlatform = useMemo(
    () => config.find((platform) => platform.id === activePlatformId) ?? config[0],
    [config, activePlatformId]
  )

  return {
    platforms: config,
    activePlatform,
    activePlatformId: activePlatform?.id ?? (config[0]?.id ?? DEFAULT_PLATFORM_ID),
    setActivePlatformId
  }
}
