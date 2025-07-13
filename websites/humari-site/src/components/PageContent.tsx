import { Page } from '@/lib/types/api'
import { getPageHierarchyLevel, getPrimaryKeyword } from '@/lib/utils/page'
import { MarkdownRenderer } from './MarkdownRenderer'
import { ErrorBoundary } from './common/ErrorBoundary'
import { cn, formatDate } from '@/lib/utils'

interface PageContentProps {
  page: Page
  className?: string
}

export function PageContent({ page, className }: PageContentProps) {
  const hierarchyLevel = getPageHierarchyLevel(page)
  const primaryKeyword = getPrimaryKeyword(page)

  return (
    <ErrorBoundary>
      <article className={cn("max-w-4xl mx-auto px-4 py-8", className)}>
        {/* Breadcrumb si besoin */}
        {hierarchyLevel > 1 && (
          <nav className="mb-6 text-sm text-secondary-500">
            <span>Vous êtes ici : {page.url_path}</span>
          </nav>
        )}

        {/* Header de la page */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold font-heading text-gray-900 mb-4">
            {page.title}
          </h1>
          
          {page.content?.meta_description && (
            <p className="text-xl text-secondary-600 leading-relaxed">
              {page.content.meta_description}
            </p>
          )}

          {/* Métadonnées pour debug en dev */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg text-sm border border-gray-200">
              <h3 className="font-bold mb-2 text-gray-800">Debug Info:</h3>
              <div className="space-y-1 text-gray-600">
                <p><strong>Type:</strong> {page.page_type}</p>
                <p><strong>Intent:</strong> {page.search_intent}</p>
                <p><strong>Niveau:</strong> {hierarchyLevel}</p>
                {primaryKeyword && (
                  <p><strong>Mot-clé principal:</strong> {primaryKeyword}</p>
                )}
                {page.keywords && (
                  <p><strong>Mots-clés:</strong> {page.keywords.length}</p>
                )}
              </div>
            </div>
          )}
        </header>

        {/* Contenu principal */}
        {page.content?.content_markdown ? (
          <div className="markdown-content">
            <MarkdownRenderer content={page.content.content_markdown} />
          </div>
        ) : (
          <div className="text-center py-12 card-base">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Contenu en préparation
            </h2>
            <p className="text-secondary-600">
              Cette page est en cours de rédaction. Revenez bientôt !
            </p>
          </div>
        )}

        {/* Footer de l'article */}
        {page.content && (
          <footer className="mt-12 pt-8 border-t border-gray-200">
            <div className="flex flex-wrap items-center justify-between text-sm text-secondary-500">
              <div>
                Publié le {formatDate(page.content.created_at)}
                {page.content.updated_at !== page.content.created_at && (
                  <span> • Mis à jour le {formatDate(page.content.updated_at)}</span>
                )}
              </div>
              
              {page.content.reading_time_minutes > 0 && (
                <div>
                  Temps de lecture : {page.content.reading_time_minutes} min
                  {page.content.word_count > 0 && (
                    <span> • {page.content.word_count} mots</span>
                  )}
                </div>
              )}
            </div>
          </footer>
        )}
      </article>
    </ErrorBoundary>
  )
}
