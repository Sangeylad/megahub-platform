/** @type {import('next').NextConfig} */
const nextConfig = {
  compress: true,
  generateEtags: false,
  
  // 🎯 Force rebuild complet des assets à chaque deploy
  generateBuildId: async () => {
    return `build-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
  },
  
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // 🎯 Headers intelligents : sécurité SANS casser les assets
  headers: async () => [
    {
      // Pages HTML seulement (pas d'assets)
      source: '/((?!_next|api|favicon.ico|robots.txt|sitemap.xml|.*\\.).*)',
      headers: [
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-XSS-Protection', value: '1; mode=block' },
        { key: 'Cache-Control', value: 'no-store, no-cache, must-revalidate' },
        { key: 'Pragma', value: 'no-cache' },
        { key: 'Expires', value: '0' },
      ],
    },
    {
      // Assets statiques : cache court pour éviter les problèmes
      source: '/_next/static/(.*)',
      headers: [
        { key: 'Cache-Control', value: 'public, max-age=300' }, // 5min seulement
      ],
    },
    {
      // Images optimisées Next.js
      source: '/_next/image(.*)',
      headers: [
        { key: 'Cache-Control', value: 'public, max-age=3600' }, // 1h pour images
      ],
    },
  ],
}

module.exports = nextConfig