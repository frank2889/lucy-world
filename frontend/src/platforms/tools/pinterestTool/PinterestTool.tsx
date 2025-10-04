import React, { useMemo } from 'react'
import type { PlatformToolProps } from '../../types'
import { createTranslator } from '../../../i18n/translate'

const PinterestTool: React.FC<PlatformToolProps> = ({ ui }) => {
  const t = useMemo(() => createTranslator(ui), [ui])
  return (
    <section className="platform-tool">
      <header className="platform-tool__header">
        <h3>{t('platform.pinterest.heading', 'Pinterest keyword tool')}</h3>
        <p className="platform-tool__description">
          {t(
            'platform.pinterest.description',
            'This tool is currently unavailable because Pinterest does not offer a freely accessible suggestions API.'
          )}
        </p>
      </header>
      <div className="platform-tool__results">
        <div className="platform-tool__placeholder">{t('platform.pinterest.placeholder', 'Not available')}</div>
      </div>
    </section>
  )
}

export default PinterestTool
