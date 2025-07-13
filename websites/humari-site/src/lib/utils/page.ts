import { Page } from '@/lib/types/api'  // ✅ Import direct au lieu de '@/lib/types'

/**
 * Calcule le niveau hiérarchique d'une page
 * 1 = page mère (top level)
 * 2 = page fille (mid level)  
 * 3+ = page petite-fille ou plus profond
 */
export function getPageHierarchyLevel(page: Page): number {
  if (!page.parent) {
    return 1 // Page mère
  }
  
  // Pour calculer précisément, il faudrait remonter toute la chaîne
  // Mais on peut approximer en comptant les "/" dans l'URL
  const pathSegments = page.url_path.split('/').filter(Boolean)
  return Math.min(pathSegments.length, 3) // Max 3 comme dans le modèle Django
}

/**
 * Récupère le mot-clé primaire d'une page
 */
export function getPrimaryKeyword(page: Page): string | null {
  if (!page.keywords) return null
  
  // Si on a les relations PageKeyword détaillées
  const primaryKeyword = page.keywords.find(k => 
    'keyword_type' in k && k.keyword_type === 'primary'
  )
  
  return primaryKeyword?.keyword || page.keywords[0]?.keyword || null
}

/**
 * Formate le breadcrumb d'une page
 */
export function getPageBreadcrumb(page: Page): Array<{title: string, url: string}> {
  const breadcrumb = []
  
  // Ajouter l'accueil
  breadcrumb.push({ title: 'Accueil', url: '/' })
  
  // Analyser l'URL pour construire le breadcrumb
  const segments = page.url_path.split('/').filter(Boolean)
  let currentPath = ''
  
  segments.forEach((segment, index) => {
    currentPath += `/${segment}`
    
    // Pour le dernier segment, utiliser le titre de la page
    if (index === segments.length - 1) {
      breadcrumb.push({ title: page.title, url: currentPath })
    } else {
      // Pour les segments intermédiaires, capitaliser
      const title = segment.charAt(0).toUpperCase() + segment.slice(1)
      breadcrumb.push({ title, url: currentPath })
    }
  })
  
  return breadcrumb
}