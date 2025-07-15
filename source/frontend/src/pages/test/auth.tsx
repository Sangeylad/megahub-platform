// frontend/src/pages/test/auth.tsx
import { createFileRoute } from '@tanstack/react-router'
import AuthTest from '@/components/AuthTest'

export const Route = createFileRoute('/test/auth')({
  component: AuthTestPage,
})

function AuthTestPage() {
  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        background: 'white',
        borderRadius: '12px',
        padding: '20px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
      }}>
        <div style={{ marginBottom: '20px', textAlign: 'center' }}>
          <h1 style={{ 
            color: '#333', 
            fontSize: '2.5rem',
            marginBottom: '10px'
          }}>
            🧪 MegaHub - Test d'Authentification
          </h1>
          <p style={{ 
            color: '#666',
            fontSize: '1.1rem'
          }}>
            Interface de test pour valider le système d'authentification
          </p>
          <div style={{
            background: '#f8f9fa',
            border: '1px solid #e9ecef',
            borderRadius: '8px',
            padding: '15px',
            margin: '20px 0',
            textAlign: 'left'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#495057' }}>📝 Status du développement :</h3>
            <ul style={{ margin: 0, paddingLeft: '20px', color: '#6c757d' }}>
              <li>✅ <strong>Configuration tests</strong> - 13/13 tests passent</li>
              <li>✅ <strong>React 19 + TanStack v5</strong> - Architecture prête</li>
              <li>⏳ <strong>Hooks d'authentification</strong> - En cours de création</li>
              <li>⏳ <strong>Store Zustand</strong> - En cours de création</li>
              <li>⏳ <strong>Types TypeScript</strong> - En cours de création</li>
            </ul>
          </div>
        </div>
        
        <AuthTest />
      </div>
    </div>
  )
}