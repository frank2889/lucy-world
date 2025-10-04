export type AmazonMarketplace = {
  code: string
  label: string
}

export const AMAZON_MARKETPLACES: AmazonMarketplace[] = [
  { code: 'AE', label: 'Amazon.ae (AE)' },
  { code: 'AU', label: 'Amazon.com.au (AU)' },
  { code: 'BE', label: 'Amazon.com.be (BE)' },
  { code: 'BR', label: 'Amazon.com.br (BR)' },
  { code: 'CA', label: 'Amazon.ca (CA)' },
  { code: 'DE', label: 'Amazon.de (DE)' },
  { code: 'EG', label: 'Amazon.eg (EG)' },
  { code: 'ES', label: 'Amazon.es (ES)' },
  { code: 'FR', label: 'Amazon.fr (FR)' },
  { code: 'GB', label: 'Amazon.co.uk (UK)' },
  { code: 'IN', label: 'Amazon.in (IN)' },
  { code: 'IT', label: 'Amazon.it (IT)' },
  { code: 'JP', label: 'Amazon.co.jp (JP)' },
  { code: 'MX', label: 'Amazon.com.mx (MX)' },
  { code: 'NL', label: 'Amazon.nl (NL)' },
  { code: 'PL', label: 'Amazon.pl (PL)' },
  { code: 'SA', label: 'Amazon.sa (SA)' },
  { code: 'SE', label: 'Amazon.se (SE)' },
  { code: 'SG', label: 'Amazon.sg (SG)' },
  { code: 'TR', label: 'Amazon.com.tr (TR)' },
  { code: 'US', label: 'Amazon.com (US)' }
]

export const AMAZON_MARKETPLACE_CODES = AMAZON_MARKETPLACES.map((market) => market.code)
