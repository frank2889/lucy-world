import React, { useMemo } from 'react'
import type { PlatformToolProps } from '../../types'
import { createTranslator } from '../../../i18n/translate'

const EtsyTool: React.FC<PlatformToolProps> = ({ ui }) => {
  const t = useMemo(() => createTranslator(ui), [ui])
  const heading = t('platform.etsy.heading')
  const description = t('platform.etsy.description')
  const placeholder = t('platform.etsy.placeholder')
  return (
    <section className="platform-tool">
      <header className="platform-tool__header">
        <h3>{heading}</h3>
        <p className="platform-tool__description">{description}</p>
      </header>
      <div className="platform-tool__results">
        <div className="platform-tool__placeholder">{placeholder}</div>
      </div>
    </section>
  )
}

export default EtsyTool
