import React from 'react'
import type { PlatformToolProps } from '../../types'

const PinterestTool: React.FC<PlatformToolProps> = () => {
  return (
    <section className="platform-tool">
      <header className="platform-tool__header">
        <h3>Pinterest keywordtool</h3>
        <p className="platform-tool__description">
          Deze tool is momenteel niet beschikbaar omdat Pinterest geen vrij toegankelijke suggestie-API heeft.
        </p>
      </header>
      <div className="platform-tool__results">
        <div className="platform-tool__placeholder">Not available</div>
      </div>
    </section>
  )
}

export default PinterestTool
