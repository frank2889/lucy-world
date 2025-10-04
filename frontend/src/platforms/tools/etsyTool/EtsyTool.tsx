import React from 'react'
import type { PlatformToolProps } from '../../types'

const EtsyTool: React.FC<PlatformToolProps> = () => {
  return (
    <section className="platform-tool">
      <header className="platform-tool__header">
        <h3>Etsy keywordtool</h3>
        <p className="platform-tool__description">
          Deze tool is momenteel niet beschikbaar omdat Etsy geen open suggestie-API aanbiedt die zonder authenticatie werkt.
        </p>
      </header>
      <div className="platform-tool__results">
        <div className="platform-tool__placeholder">Not available</div>
      </div>
    </section>
  )
}

export default EtsyTool
