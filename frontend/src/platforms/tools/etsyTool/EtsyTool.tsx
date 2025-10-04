import React, { useMemo } from 'react'
import type { PlatformToolProps } from '../../types'
import { createTranslator } from '../../../i18n/translate'

const EtsyTool: React.FC<PlatformToolProps> = ({ ui }) => {
  const t = useMemo(() => createTranslator(ui), [ui])
  return (
    <section className="platform-tool">
      <header className="platform-tool__header">
        <h3>{t('platform.etsy.heading', 'Etsy keyword tool')}</h3>
        <p className="platform-tool__description">
          {t(
            'platform.etsy.description',
            'This tool is currently unavailable because Etsy does not offer a public suggestions API without authentication.'
          )}
        </p>
      </header>
      <div className="platform-tool__results">
        <div className="platform-tool__placeholder">{t('platform.etsy.placeholder', 'Not available')}</div>
      </div>
    </section>
  )
}

export default EtsyTool
