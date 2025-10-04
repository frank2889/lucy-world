import { useMemo, useState } from 'react'
import { platformsConfig, DEFAULT_PLATFORM_ID } from '../config/platformsConfig'

export const usePlatformHandler = (initialId: string = DEFAULT_PLATFORM_ID) => {
  const [activePlatformId, setActivePlatformId] = useState(initialId)

  const activePlatform = useMemo(
    () => platformsConfig.find((platform) => platform.id === activePlatformId) ?? platformsConfig[0],
    [activePlatformId]
  )

  return {
    platforms: platformsConfig,
    activePlatform,
    activePlatformId: activePlatform?.id ?? DEFAULT_PLATFORM_ID,
    setActivePlatformId
  }
}
