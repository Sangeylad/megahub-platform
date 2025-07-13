import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center max-w-md mx-auto px-4">
        <h1 className="text-6xl font-bold text-gray-300 mb-4">404</h1>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Page non trouvée
        </h2>
        <p className="text-gray-600 mb-6">
          Désolé, la page que vous cherchez n&apos;existe pas.
        </p>
        <Link 
          href="/"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-block"
        >
          Retour à l&apos;accueil
        </Link>
      </div>
    </div>
  )
}