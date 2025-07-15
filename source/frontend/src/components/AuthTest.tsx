// frontend/src/components/AuthTest.tsx

// 🧪 Composant Test Auth - Vérification système d'authentification

import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useAuthStore } from '@/stores/authStore';
import type { LoginFormData } from '@/types/auth';

export default function AuthTest() {
  const [credentials, setCredentials] = useState<LoginFormData>({
    username: '',
    password: '',
    remember_me: false,
  });

  // Test du hook useAuth
  const {
    user,
    isAuthenticated,
    isLoading,
    isPending,
    isLoggingIn,
    login,
    logout,
    hasPermission,
    isCompanyAdmin,
    isBrandAdmin,
    canAccessAnalytics,
    sessionInfo,
  } = useAuth();

  // Test direct du store
  const {
    user: storeUser,
    isAuthenticated: storeIsAuth,
    error: storeError,
  } = useAuthStore();

  // Test des actions du store
  const {
    setUser,
    clearAuth,
    updateUserProfile,
  } = useAuthStore();

  // ==========================================
  // HANDLERS PROPRES - React 19 + TypeScript strict
  // ==========================================
  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setCredentials({
      ...credentials,
      username: newValue,
    });
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setCredentials({
      ...credentials,
      password: newValue,
    });
  };

  const handleRememberMeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const isChecked = e.target.checked;
    setCredentials({
      ...credentials,
      remember_me: isChecked,
    });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      console.log('🔐 Tentative de connexion...', credentials);
      await login(credentials);
      console.log('✅ Connexion réussie!');
    } catch (error) {
      console.error('❌ Erreur de connexion:', error);
    }
  };

  const handleLogout = async () => {
    try {
      console.log('🚪 Déconnexion...');
      await logout();
      console.log('✅ Déconnexion réussie!');
    } catch (error) {
      console.error('❌ Erreur de déconnexion:', error);
    }
  };

  const testStoreActions = () => {
    console.log('🧪 Test des actions du store...');

    // Test setUser avec données factices
    const mockUser = {
      id: 999,
      username: 'test_user',
      email: 'test@megahub.fr',
      first_name: 'Test',
      last_name: 'User',
      user_type: 'brand_admin' as const,
      can_access_analytics: true,
      can_access_reports: false,
      phone: '0123456789',
      position: 'Testeur',
      is_active: true,
      is_staff: false,
      is_superuser: false,
      date_joined: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setUser(mockUser);
    console.log('✅ setUser() testé avec succès');

    // Test updateUserProfile
    setTimeout(() => {
      updateUserProfile({ first_name: 'Test Updated' });
      console.log('✅ updateUserProfile() testé avec succès');
    }, 1000);

    // Test clearAuth
    setTimeout(() => {
      clearAuth();
      console.log('✅ clearAuth() testé avec succès');
    }, 3000);
  };

  return (
    <div style={{
      padding: '20px',
      maxWidth: '800px',
      margin: '0 auto',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1>🧪 Test Système d'Authentification MegaHub</h1>

      {/* STATUS GÉNÉRAL */}
      <div style={{
        background: isAuthenticated ? '#d4edda' : '#f8d7da',
        padding: '15px',
        borderRadius: '8px',
        marginBottom: '20px',
        border: `2px solid ${isAuthenticated ? '#28a745' : '#dc3545'}`
      }}>
        <h2>📊 État d'Authentification</h2>
        <p><strong>Connecté:</strong> {isAuthenticated ? '✅ OUI' : '❌ NON'}</p>
        <p><strong>Chargement:</strong> {isLoading ? '⏳ OUI' : '✅ NON'}</p>
        <p><strong>En cours:</strong> {isPending ? '⏳ OUI' : '✅ NON'}</p>
        <p><strong>Connexion en cours:</strong> {isLoggingIn ? '⏳ OUI' : '✅ NON'}</p>
      </div>

      {/* DONNÉES UTILISATEUR */}
      <div style={{
        background: '#e7f3ff',
        padding: '15px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2>👤 Données Utilisateur (Hook)</h2>
        {user ? (
          <div>
            <p><strong>ID:</strong> {user.id}</p>
            <p><strong>Nom:</strong> {user.first_name} {user.last_name}</p>
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Type:</strong> {user.user_type}</p>
            <p><strong>Analytics:</strong> {user.can_access_analytics ? '✅' : '❌'}</p>
            <p><strong>Reports:</strong> {user.can_access_reports ? '✅' : '❌'}</p>
          </div>
        ) : (
          <p>❌ Aucun utilisateur connecté</p>
        )}
      </div>

      {/* DONNÉES STORE */}
      <div style={{
        background: '#fff3cd',
        padding: '15px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2>🏪 Données Store (Direct)</h2>
        <p><strong>Store Auth:</strong> {storeIsAuth ? '✅ OUI' : '❌ NON'}</p>
        <p><strong>Store User:</strong> {storeUser ? `✅ ${storeUser.username}` : '❌ NULL'}</p>
        <p><strong>Store Error:</strong> {storeError || '✅ Aucune'}</p>
      </div>

      {/* PERMISSIONS */}
      <div style={{
        background: '#f8f9fa',
        padding: '15px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2>🔐 Permissions & Rôles</h2>
        <p><strong>Company Admin:</strong> {isCompanyAdmin() ? '✅ OUI' : '❌ NON'}</p>
        <p><strong>Brand Admin:</strong> {isBrandAdmin() ? '✅ OUI' : '❌ NON'}</p>
        <p><strong>Accès Analytics:</strong> {canAccessAnalytics() ? '✅ OUI' : '❌ NON'}</p>
        <p><strong>Permission 'pages.write':</strong> {hasPermission('pages.write') ? '✅ OUI' : '❌ NON'}</p>
        <p><strong>Permission 'analytics.read':</strong> {hasPermission('analytics.read') ? '✅ OUI' : '❌ NON'}</p>
      </div>

      {/* SESSION INFO */}
      <div style={{
        background: '#e2e3e5',
        padding: '15px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2>📡 Informations Session</h2>
        <pre style={{ fontSize: '12px', overflow: 'auto' }}>
          {JSON.stringify(sessionInfo, null, 2)}
        </pre>
      </div>

      {/* FORMULAIRE DE TEST */}
      {!isAuthenticated && (
        <div style={{
          background: '#ffffff',
          padding: '20px',
          borderRadius: '8px',
          border: '2px solid #007bff',
          marginBottom: '20px'
        }}>
          <h2>🔑 Test de Connexion</h2>
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '10px' }}>
              <label>
                <strong>Username:</strong>
                <input
                  type="text"
                  value={credentials.username}
                  onChange={handleUsernameChange}
                  style={{
                    marginLeft: '10px',
                    padding: '8px',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    width: '200px'
                  }}
                  placeholder="test_user"
                />
              </label>
            </div>
            <div style={{ marginBottom: '10px' }}>
              <label>
                <strong>Password:</strong>
                <input
                  type="password"
                  value={credentials.password}
                  onChange={handlePasswordChange}
                  style={{
                    marginLeft: '10px',
                    padding: '8px',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    width: '200px'
                  }}
                  placeholder="********"
                />
              </label>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label>
                <input
                  type="checkbox"
                  checked={credentials.remember_me}
                  onChange={handleRememberMeChange}
                  style={{ marginRight: '8px' }}
                />
                <strong>Se souvenir de moi</strong>
              </label>
            </div>
            <button
              type="submit"
              disabled={isLoggingIn}
              style={{
                padding: '10px 20px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isLoggingIn ? 'not-allowed' : 'pointer',
                opacity: isLoggingIn ? 0.6 : 1
              }}
            >
              {isLoggingIn ? '⏳ Connexion...' : '🔑 Se connecter'}
            </button>
          </form>
          <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
            💡 Ce formulaire tentera de se connecter à votre API Django.
            Assurez-vous que l'API est démarrée !
          </p>
        </div>
      )}

      {/* ACTIONS */}
      <div style={{
        background: '#ffffff',
        padding: '20px',
        borderRadius: '8px',
        border: '2px solid #28a745'
      }}>
        <h2>⚡ Actions de Test</h2>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {isAuthenticated && (
            <button
              onClick={handleLogout}
              style={{
                padding: '10px 15px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              🚪 Se déconnecter
            </button>
          )}

          <button
            onClick={testStoreActions}
            style={{
              padding: '10px 15px',
              backgroundColor: '#ffc107',
              color: 'black',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            🧪 Tester Store Actions
          </button>

          <button
            onClick={() => {
              console.log('🔍 État complet du hook useAuth:', {
                user,
                isAuthenticated,
                isLoading,
                isPending,
                sessionInfo
              });
            }}
            style={{
              padding: '10px 15px',
              backgroundColor: '#17a2b8',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            🔍 Log État Hook
          </button>

          <button
            onClick={() => {
              console.log('🏪 État complet du store:', useAuthStore.getState());
            }}
            style={{
              padding: '10px 15px',
              backgroundColor: '#6f42c1',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            🏪 Log État Store
          </button>
        </div>
      </div>

      {/* CONSOLE LOG INFO */}
      <div style={{
        marginTop: '20px',
        padding: '10px',
        background: '#f8f9fa',
        borderRadius: '4px',
        fontSize: '14px'
      }}>
        <p><strong>💡 Conseils de Test:</strong></p>
        <ul>
          <li>Ouvre la console (F12) pour voir les logs détaillés</li>
          <li>Teste d'abord les actions du store avec le bouton "🧪 Tester Store Actions"</li>
          <li>Vérifie que ton API Django est démarrée pour tester la vraie connexion</li>
          <li>Utilise les boutons de log pour inspecter l'état en détail</li>
        </ul>
      </div>
    </div>
  );
}