// /var/www/megahub/websites/humari-site/src/app/layout.tsx
import type { Metadata } from 'next'
import '../styles/globals.css'  // ✅ Nouveau chemin

export const metadata: Metadata = {
  title: 'Humari',
  description: 'Agence digitale',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body>
        {children}
      </body>
    </html>
  )
}
