import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: [
        '/api/',
        '/_next/',
        '/admin/',
        '/backoffice/',
        '*.json$',
        '/*?*'
      ],
      crawlDelay: 1
    },
    sitemap: `https://${process.env.NEXT_PUBLIC_DOMAIN}/sitemap.xml`,
  }
}