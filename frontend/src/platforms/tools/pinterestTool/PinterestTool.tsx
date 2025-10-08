import React, { useMemo } from 'react'
import type { PlatformToolProps } from '../../types'
import { createTranslator } from '../../../i18n/translate'

const PinterestTool: React.FC<PlatformToolProps> = ({ ui }) => {
  const t = useMemo(() => createTranslator(ui), [ui])
  const heading = t('platform.pinterest.heading')
  const description = t('platform.pinterest.description')
  const placeholder = t('platform.pinterest.placeholder')
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

export default PinterestTool
