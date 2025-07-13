// src/components/tools/glossary-search/components/shared/EmptyState.tsx
interface EmptyStateProps {
  type: 'no-search' | 'no-results' | 'error'
  message?: string
  actionButton?: React.ReactNode
  className?: string
}

export function EmptyState({ type, message, actionButton, className = '' }: EmptyStateProps) {
  const getContent = () => {
    switch (type) {
      case 'no-search':
        return {
          icon: '🔍',
          title: 'Recherchez un terme',
          description: message || 'Tapez votre recherche pour découvrir nos définitions business'
        }
      case 'no-results':
        return {
          icon: '📭',
          title: 'Aucun résultat',
          description: message || 'Essayez avec des mots-clés différents ou vérifiez l\'orthographe'
        }
      case 'error':
        return {
          icon: '⚠️',
          title: 'Erreur',
          description: message || 'Une erreur s\'est produite lors de la recherche'
        }
    }
  }
  
  const content = getContent()
  
  return (
    <div className={`text-center py-12 px-6 ${className}`}>
      <div className="text-6xl mb-4">{content.icon}</div>
      <h3 className="text-xl font-semibold text-neutral-800 mb-2">
        {content.title}
      </h3>
      <p className="text-neutral-600 mb-6 max-w-md mx-auto">
        {content.description}
      </p>
      {actionButton && (
        <div className="mt-6">
          {actionButton}
        </div>
      )}
    </div>
  )
}