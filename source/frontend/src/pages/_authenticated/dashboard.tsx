// frontend/src/pages/_authenticated/dashboard.tsx

// 📊 Dashboard Route - Automatiquement protégée par layout _authenticated

import { useAuth } from '@/hooks/useAuth';
import { createFileRoute } from '@tanstack/react-router';

// ==========================================
// DASHBOARD ROUTE - Route protégée
// ==========================================

export const Route = createFileRoute('/_authenticated/dashboard')({
  component: DashboardPage,
});

// ==========================================
// DASHBOARD COMPONENT
// ==========================================

function DashboardPage() {
  const { user, isAuthenticated, sessionInfo } = useAuth();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Tableau de bord
        </h1>
        <p className="mt-2 text-gray-600">
          Bienvenue sur votre espace MegaHub
        </p>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {/* User Info Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Informations utilisateur
          </h3>

          {user ? (
            <div className="space-y-2">
              <p className="text-sm">
                <span className="font-medium">Nom :</span> {user.first_name} {user.last_name}
              </p>
              <p className="text-sm">
                <span className="font-medium">Email :</span> {user.email}
              </p>
              <p className="text-sm">
                <span className="font-medium">Type :</span> {user.user_type}
              </p>
              <p className="text-sm">
                <span className="font-medium">Status :</span>
                <span className="ml-1 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                  Connecté
                </span>
              </p>
            </div>
          ) : (
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          )}
        </div>

        {/* Session Info Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Session
          </h3>

          <div className="space-y-2">
            <p className="text-sm">
              <span className="font-medium">Authentifié :</span>
              <span className={`ml-1 px-2 py-1 rounded-full text-xs ${isAuthenticated
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
                }`}>
                {isAuthenticated ? 'Oui' : 'Non'}
              </span>
            </p>

            {sessionInfo && (
              <>
                <p className="text-sm">
                  <span className="font-medium">Type utilisateur :</span> {user?.user_type || 'N/A'}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Session valide :</span>
                  <span className={`ml-1 px-2 py-1 rounded-full text-xs ${sessionInfo?.hasValidSession
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                    }`}>
                    {sessionInfo?.hasValidSession ? 'Oui' : 'Expirée'}
                  </span>
                </p>
              </>
            )}
          </div>
        </div>

        {/* Quick Actions Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Actions rapides
          </h3>

          <div className="space-y-3">
            <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
              Créer une page
            </button>
            <button className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm">
              Voir les analytics
            </button>
            <button className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm">
              Gérer les utilisateurs
            </button>
          </div>
        </div>
      </div>

      {/* Development Debug Info */}
      {import.meta.env.MODE === 'development' && (
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="text-sm font-medium text-blue-900 mb-2">
            🔧 Debug Info (Development)
          </h4>
          <pre className="text-xs text-blue-800 whitespace-pre-wrap">
            {JSON.stringify({
              isAuthenticated,
              userType: user?.user_type,
              sessionInfo: sessionInfo
            }, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}