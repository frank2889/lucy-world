import React, { useMemo } from 'react'
import type { PlatformToolProps } from '../../types'
import { createTranslator } from '../../../i18n/translate'

const TikTokTool: React.FC<PlatformToolProps> = ({ ui }) => {
  const t = useMemo(() => createTranslator(ui), [ui])
  return (
    <section className="platform-tool">
      <header className="platform-tool__header">
        <h3>{t('platform.tiktok.heading', 'TikTok keyword tool')}</h3>
        <p className="platform-tool__description">
          {t('platform.tiktok.description', 'This tool is currently unavailable because there is no public TikTok autocomplete API.')}
        </p>
      </header>
      <div className="platform-tool__results">
        <div className="platform-tool__placeholder">{t('platform.tiktok.placeholder', 'Not available')}</div>
      </div>
    </section>
  )
}

export default TikTokTool
