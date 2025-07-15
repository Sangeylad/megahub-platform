// frontend/src/pages/index.tsx

// 🏠 Index Route - Simple selon TanStack Router v1.126

import { authService } from '@/services/api/authService';
import { createFileRoute } from '@tanstack/react-router';

// ==========================================
// INDEX ROUTE - Redirection automatique simple
// ==========================================

export const Route = createFileRoute('/')({

  // ⚡ BEFORELOAD - Logique de redirection simple
  beforeLoad: () => {
    console.log('🏠 [Index] Vérification statut authentification...');

    // Pour l'instant, redirection simple sans throw
    // À améliorer plus tard avec la logique de redirect
    if (authService.isAuthenticated()) {
      console.log('✅ [Index] Utilisateur connecté');
      // window.location.href = '/dashboard';
    } else {
      console.log('❌ [Index] Utilisateur non connecté');
      // window.location.href = '/auth/login';
    }

    return {};
  },

  // ⚡ COMPONENT - Page d'accueil temporaire
  component: IndexPage,
});

// ==========================================
// INDEX COMPONENT - Temporaire avec redirections manuelles
// ==========================================

function IndexPage() {
  // Redirect manual en attendant
  React.useEffect(() => {
    if (authService.isAuthenticated()) {
      window.location.href = '/dashboard';
    } else {
      window.location.href = '/auth/login';
    }
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          MegaHub
        </h1>
        <p className="text-gray-600 mb-4">
          Redirection en cours...
        </p>

        {/* Loading spinner */}
        <div className="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-blue-500 hover:bg-blue-400 transition ease-in-out duration-150 cursor-not-allowed">
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Chargement...
        </div>

        {/* Development info */}
        {import.meta.env.MODE === 'development' && (
          <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-left">
            <p className="text-sm text-yellow-800">
              🚧 <strong>Mode Développement :</strong> Redirection manuelle avec window.location.href en attendant de configurer les redirections TanStack Router.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

// Import React
import React from 'react';
