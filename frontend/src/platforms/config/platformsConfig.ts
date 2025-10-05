import { lazy } from 'react'
import type { PlatformConfig } from '../types'

const icon = (name: string) => new URL(`../icons/${name}.svg`, import.meta.url).href

export const platformsConfig: PlatformConfig[] = [
  {
    id: 'google',
    name: 'Google',
    icon: icon('google'),
    description: 'Algemene web zoekwoorden',
    descriptionKey: 'platform.google.description',
    tool: lazy(() => import('../tools/googleTool/GoogleTool'))
  },
  {
    id: 'duckduckgo',
    name: 'DuckDuckGo',
    icon: icon('duckduckgo'),
    description: 'Privacyvriendelijke zoekmachine',
    descriptionKey: 'platform.duckduckgo.description',
    tool: lazy(() => import('../tools/duckduckgoTool/DuckDuckGoTool'))
  },
  {
    id: 'yahoo',
    name: 'Yahoo',
    icon: icon('yahoo'),
    description: 'Yahoo zoekmachine',
    descriptionKey: 'platform.yahoo.description',
    tool: lazy(() => import('../tools/yahooTool/YahooTool'))
  },
  {
    id: 'brave',
    name: 'Brave',
    icon: icon('brave'),
    description: 'Brave zoekmachine',
    descriptionKey: 'platform.brave.description',
    tool: lazy(() => import('../tools/braveTool/BraveTool'))
  },
  {
    id: 'qwant',
    name: 'Qwant',
    icon: icon('qwant'),
    description: 'Europese zoekmachine',
    descriptionKey: 'platform.qwant.description',
    tool: lazy(() => import('../tools/qwantTool/QwantTool'))
  },
  {
    id: 'youtube',
    name: 'YouTube',
    icon: icon('youtube'),
    description: 'Video zoekwoorden',
    descriptionKey: 'platform.youtube.description',
    tool: lazy(() => import('../tools/youtubeTool/YouTubeTool'))
  },
  {
    id: 'amazon',
    name: 'Amazon',
    icon: icon('amazon'),
    description: 'Product zoekwoorden',
    descriptionKey: 'platform.amazon.description',
    tool: lazy(() => import('../tools/amazonTool/AmazonTool'))
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: icon('tiktok'),
    description: 'Short-form video zoekwoorden',
    descriptionKey: 'platform.tiktok.description',
    tool: lazy(() => import('../tools/tiktokTool/TikTokTool'))
  },
  {
    id: 'instagram',
    name: 'Instagram',
    icon: icon('instagram'),
    description: 'Hashtags en visuele zoekwoorden',
    descriptionKey: 'platform.instagram.description',
    tool: lazy(() => import('../tools/instagramTool/InstagramTool'))
  },
  {
    id: 'pinterest',
    name: 'Pinterest',
    icon: icon('pinterest'),
    description: 'Inspiratie en beeld zoekwoorden',
    descriptionKey: 'platform.pinterest.description',
    tool: lazy(() => import('../tools/pinterestTool/PinterestTool'))
  },
  {
    id: 'bing',
    name: 'Bing',
    icon: icon('bing'),
    description: 'Microsoft zoekmachine',
    descriptionKey: 'platform.bing.description',
    tool: lazy(() => import('../tools/bingTool/BingTool'))
  },
  {
    id: 'baidu',
    name: 'Baidu',
    icon: icon('baidu'),
    description: 'Chinese zoekmachine',
    descriptionKey: 'platform.baidu.description',
    tool: lazy(() => import('../tools/baiduTool/BaiduTool'))
  },
  {
    id: 'yandex',
    name: 'Yandex',
    icon: icon('yandex'),
    description: 'Russische zoekmachine',
    descriptionKey: 'platform.yandex.description',
    tool: lazy(() => import('../tools/yandexTool/YandexTool'))
  },
  {
    id: 'naver',
    name: 'Naver',
    icon: icon('naver'),
    description: 'Koreaanse zoekmachine',
    descriptionKey: 'platform.naver.description',
    tool: lazy(() => import('../tools/naverTool/NaverTool'))
  },
  {
    id: 'ebay',
    name: 'eBay',
    icon: icon('ebay'),
    description: 'E-commerce zoekwoorden',
    descriptionKey: 'platform.ebay.description',
    tool: lazy(() => import('../tools/ebayTool/EbayTool'))
  },
  {
    id: 'appstore',
    name: 'App Store',
    icon: icon('appstore'),
    description: 'iOS app zoekwoorden',
    descriptionKey: 'platform.appstore.description',
    tool: lazy(() => import('../tools/appstoreTool/AppStoreTool'))
  },
  {
    id: 'googleplay',
    name: 'Google Play',
    icon: icon('googleplay'),
    description: 'Android app zoekwoorden',
    descriptionKey: 'platform.googlePlay.description',
    tool: lazy(() => import('../tools/googleplayTool/GooglePlayTool'))
  },
  {
    id: 'etsy',
    name: 'Etsy',
    icon: icon('etsy'),
    description: 'Marktplaats zoekwoorden',
    descriptionKey: 'platform.etsy.description',
    tool: lazy(() => import('../tools/etsyTool/EtsyTool'))
  }
]

export const DEFAULT_PLATFORM_ID = platformsConfig[0]?.id || 'google'
