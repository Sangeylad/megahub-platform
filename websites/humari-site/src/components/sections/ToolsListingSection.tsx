// components/sections/ToolsListingSection.tsx - VERSION SSR COMPLÈTE CORRIGÉE
import Link from 'next/link'
import { toolsAPI } from '@/lib/api'
import type { ToolsListingSectionProps } from '@/lib/types/sections'
import type { ToolsByCategoryResponse } from '@/lib/types/tools'

interface Props {
  data: ToolsListingSectionProps
}

export async function ToolsListingSection({ data }: Props) {
  // 🚀 SERVER SIDE FETCH
  let toolsData: ToolsByCategoryResponse | null = null
  let error: string | null = null

  // Configuration avec defaults et conversion de types
  const config = {
    title: data.title || 'Nos Outils',
    subtitle: data.subtitle || '',
    display_mode: data.display_mode || 'grid',
    show_category_info: data.show_category_info ?? true,
    show_description: data.show_description ?? true,
    show_tools_count: data.show_tools_count ?? true,
    grid_columns: typeof data.grid_columns === 'string' ? parseInt(data.grid_columns) : (data.grid_columns || 3),
    card_style: data.card_style || 'default',
    cta_text: data.cta_text || 'Utiliser l&apos;outil',
    empty_state_message: data.empty_state_message || 'Aucun outil disponible dans cette catégorie.',
  }

  try {
    if (data.category_id) {
      const categoryId = typeof data.category_id === 'string' ? parseInt(data.category_id) : data.category_id
      toolsData = await toolsAPI.getCategoryTools(categoryId)
    } else if (data.category_path) {
      toolsData = await toolsAPI.getCategoryToolsByPath(data.category_path)
    } else {
      error = 'Configuration manquante : category_id ou category_path requis'
    }
  } catch (err) {
    console.error('Error fetching tools:', err)
    error = 'Erreur de connexion'
  }

  // 🚨 GESTION D'ERREURS
  if (error) {
    return (
      <section className="py-16 bg-gradient-to-br from-neutral-50 to-white">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg max-w-md mx-auto">
              <p className="font-medium">Erreur de chargement</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      </section>
    )
  }

  // 🚨 ÉTAT VIDE
  if (!toolsData || toolsData.tools.length === 0) {
    return (
      <section className="py-16 bg-gradient-to-br from-neutral-50 to-white">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="max-w-md mx-auto">
              <div className="text-6xl mb-4">🛠️</div>
              <h3 className="text-xl font-semibold text-neutral-800 mb-2">
                Aucun outil disponible
              </h3>
              <p className="text-neutral-600">{config.empty_state_message}</p>
            </div>
          </div>
        </div>
      </section>
    )
  }

  // 🎨 STYLES DYNAMIQUES
  const gridClasses = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
  }

  const cardStyles = {
    default: 'bg-white border border-neutral-200 shadow-sm hover:shadow-md transition-shadow duration-300',
    minimal: 'bg-neutral-50 border border-neutral-100 hover:bg-white transition-colors duration-300',
    elevated: 'bg-white border border-neutral-200 shadow-md hover:shadow-lg hover:-translate-y-1 transition-all duration-300'
  }

  // 🎉 RENDU PRINCIPAL
  return (
    <section className="py-16 bg-gradient-to-br from-neutral-50 to-white">
      <div className="container mx-auto px-4">
        
        {/* Header avec info catégorie */}
        <div className="text-center mb-12">
          <h2 className="text-3xl lg:text-4xl font-bold text-dark-900 mb-4">
            {config.title}
          </h2>
          
          {config.subtitle && (
            <p className="text-lg text-neutral-600 mb-6 max-w-2xl mx-auto">
              {config.subtitle}
            </p>
          )}

          {config.show_category_info && toolsData.category && (
            <div className="bg-white border border-neutral-200 rounded-lg p-6 max-w-3xl mx-auto mb-8">
              <h3 className="text-xl font-semibold text-dark-800 mb-2">
                {toolsData.category.title}
              </h3>
              
              {config.show_description && toolsData.category.description && (
                <p className="text-neutral-600 mb-4">
                  {toolsData.category.description}
                </p>
              )}
              
              {config.show_tools_count && (
                <div className="inline-flex items-center px-3 py-1 bg-brand-50 text-brand-600 rounded-full text-sm font-medium">
                  {toolsData.tools_count} outil{toolsData.tools_count > 1 ? 's' : ''} disponible{toolsData.tools_count > 1 ? 's' : ''}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Grille d&apos;outils */}
        <div className={`grid gap-6 ${gridClasses[config.grid_columns as keyof typeof gridClasses]}`}>
          {toolsData.tools.map((tool) => (
            <div
              key={tool.id}
              className={`rounded-lg p-6 group relative overflow-hidden ${cardStyles[config.card_style]}`}
            >
              {/* Icône et titre */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <div className="w-10 h-10 bg-gradient-brand rounded-lg flex items-center justify-center text-white text-lg font-bold mr-3">
                      🛠️
                    </div>
                    <h3 className="text-lg font-semibold text-dark-800 group-hover:text-brand-600 transition-colors duration-200">
                      {tool.title}
                    </h3>
                  </div>
                </div>
              </div>

              {/* Description */}
              {config.show_description && tool.description && (
                <p className="text-neutral-600 mb-6 line-clamp-3">
                  {tool.description}
                </p>
              )}

              {/* CTA */}
              <div className="pt-4 border-t border-neutral-100">
                <Link
                  href={tool.url_path}
                  className="inline-flex items-center justify-center w-full px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg transition-all duration-200 hover:shadow-brand group-hover:scale-105"
                >
                  {config.cta_text}
                  <svg 
                    className="w-4 h-4 ml-2 transition-transform duration-200 group-hover:translate-x-1" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M9 5l7 7-7 7" 
                    />
                  </svg>
                </Link>
              </div>

              {/* Hover effect gradient */}
              <div className="absolute inset-0 bg-gradient-to-r from-brand-500/5 to-dark-500/5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            </div>
          ))}
        </div>

        {/* Footer avec lien vers toutes les catégories */}
        <div className="text-center mt-12">
          <Link
            href="/outils"
            className="inline-flex items-center px-6 py-3 bg-dark-800 hover:bg-dark-700 text-white font-medium rounded-lg transition-all duration-200 hover:shadow-dark"
          >
            Voir toutes nos catégories d&apos;outils
            <svg 
              className="w-4 h-4 ml-2" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M14 5l7 7m0 0l-7 7m7-7H3" 
              />
            </svg>
          </Link>
        </div>
      </div>
    </section>
  )
}