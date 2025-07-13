// src/lib/services/header-config.ts - VERSION AVEC BLOG DYNAMIQUE

import { navigationAPI } from '@/lib/api/navigation'
import type { HeaderConfig, MenuItem } from '@/components/layout/headers/types'
import type { NavigationItem } from '@/lib/types/api'

export class HeaderConfigService {
  
  static async generateDynamicHeaderConfig(websiteId: number): Promise<HeaderConfig> {
    console.log('🏗️ DEBUG: Starting dynamic header config generation for website:', websiteId)
    
    // Configuration par défaut
    const defaultConfig: HeaderConfig = {
      variant: 'default',
      logo_url: '/logo.svg',
      logo_alt: 'Humari',
      navigation: [
        { label: 'Accueil', href: '/' },
        { label: 'Contact', href: '/contact' }
      ],
      cta_text: 'Audit Gratuit',
      cta_url: '/contact',
      show_contact_info: false
    }

    try {
      console.log('🌐 DEBUG: Calling navigationAPI.getNavigation...')
      const navigationResponse = await navigationAPI.getNavigation(websiteId)
      
      console.log('🔍 DEBUG: Navigation response received:', {
        exists: !!navigationResponse,
        itemsCount: navigationResponse?.navigation?.length || 0,
        totalItems: navigationResponse?.total_items || 0,
        hasDynamicBlog: navigationResponse?.has_dynamic_blog || false  // ✅ NOUVEAU LOG
      })

      if (!navigationResponse || !navigationResponse.navigation || navigationResponse.navigation.length === 0) {
        console.warn('⚠️ DEBUG: No navigation data, using default config')
        return defaultConfig
      }

      console.log('🔄 DEBUG: Transforming navigation items...')
      const dynamicNavigation = this.transformNavigationItems(navigationResponse.navigation)
      
      console.log('🔍 DEBUG: Transformed navigation:', JSON.stringify(dynamicNavigation, null, 2))

      // ✅ CONFIG ENRICHIE AVEC DÉTECTION BLOG
      const dynamicConfig: HeaderConfig = {
        ...defaultConfig,
        navigation: dynamicNavigation,
        // ✅ POTENTIEL : Ajouter config blog au header si besoin
        ...(navigationResponse.has_dynamic_blog && {
          blog_enabled: true,
          blog_config: this.extractBlogConfig(navigationResponse.navigation)
        })
      }

      console.log(`✅ DEBUG: Dynamic header config generated with ${dynamicNavigation.length} nav items`)
      
      return dynamicConfig

    } catch (error) {
      console.error('❌ DEBUG: Error in generateDynamicHeaderConfig:', error)
      
      if (error instanceof Error) {
        console.error('❌ DEBUG: Error stack:', error.stack)
      } else {
        console.error('❌ DEBUG: Unknown error type:', String(error))
      }
      
      return defaultConfig
    }
  }

  private static transformNavigationItems(items: NavigationItem[]): MenuItem[] {
    console.log('🔄 DEBUG: Transforming items:', items.length)
    
    return items.map((item, index) => {
      console.log(`🔄 DEBUG: Item ${index}:`, {
        id: item.id,
        title: item.title,
        url_path: item.url_path,
        children_count: item.children?.length || 0,
        is_dynamic_blog: item.is_dynamic_blog || false  // ✅ NOUVEAU LOG
      })

      const menuItem: MenuItem = {
        label: item.title,
        href: item.url_path,
        ...(item.children && item.children.length > 0 && {
          children: this.transformNavigationItems(item.children)
        }),
        // ✅ NOUVEAU : Préserver les métadonnées blog
        ...(item.is_dynamic_blog && {
          isDynamicBlog: true,
          blogConfig: item.blog_config
        })
      }

      console.log(`✅ DEBUG: Transformed item ${index}:`, JSON.stringify(menuItem, null, 2))
      return menuItem
    })
  }

  // ✅ NOUVELLE MÉTHODE : Extraire config blog pour header
  private static extractBlogConfig(navigation: NavigationItem[]) {
    const blogItem = navigation.find(item => item.is_dynamic_blog)
    return blogItem?.blog_config || null
  }

  static validateNavigation(navigation: MenuItem[]): boolean {
    const isValid = navigation.every(item =>
      typeof item.label === 'string' &&
      typeof item.href === 'string' &&
      item.href.startsWith('/')
    )
    
    console.log('🔍 DEBUG: Navigation validation result:', isValid)
    return isValid
  }
}