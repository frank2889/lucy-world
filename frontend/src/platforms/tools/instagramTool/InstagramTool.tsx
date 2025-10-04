import React, { useMemo } from 'react'
import type { PlatformToolProps } from '../../types'
import { createTranslator } from '../../../i18n/translate'

const InstagramTool: React.FC<PlatformToolProps> = ({ ui }) => {
  const t = useMemo(() => createTranslator(ui), [ui])
  return (
    <section className="platform-tool">
      <header className="platform-tool__header">
        <h3>{t('platform.instagram.heading', 'Instagram keyword tool')}</h3>
        <p className="platform-tool__description">
          {t('platform.instagram.description', 'This tool is currently unavailable because Instagram does not provide a public autocomplete API.')}
        </p>
      </header>
      <div className="platform-tool__results">
        <div className="platform-tool__placeholder">{t('platform.instagram.placeholder', 'Not available')}</div>
      </div>
    </section>
  )
}

export default InstagramTool
