// lib/api/index.ts - COMPLET ACTUALISÉ AVEC TOOLS
import { RenderAPIClient } from './render'
import { NavigationAPIClient, navigationAPI } from './navigation'
import { ToolsAPIClient, toolsAPI } from './tools'
import { HeaderConfigService } from '../services/header-config'
import type {
  RenderResponse,
  SitemapResponse,
  NavigationResponse
} from '@/lib/types/api'

// Export WEBSITE_ID pour usage dans les pages
export const WEBSITE_ID = 34

// ✅ Instances principales
const renderAPIInstance = new RenderAPIClient()

// Classe APIClient étendue avec Tools
export class APIClient {
  private renderClient: RenderAPIClient
  private navigationClient: NavigationAPIClient
  private toolsClient: ToolsAPIClient

  constructor() {
    this.renderClient = renderAPIInstance
    this.navigationClient = navigationAPI
    this.toolsClient = toolsAPI
  }

  // ========== RENDER API ==========
  async getPageForRender(slugArray: string[]): Promise<RenderResponse | null> {
    return this.renderClient.getPageForRender(slugArray)
  }

  async getSitemapData(): Promise<SitemapResponse> {
    return this.renderClient.getSitemapData()
  }

  async getSitemapPages(): Promise<import('@/lib/types/api').SitemapPage[]> {
    const response = await this.getSitemapData()
    return response.pages
  }

  // ========== NAVIGATION API ==========
  async getNavigation(websiteId: number): Promise<NavigationResponse | null> {
    return this.navigationClient.getNavigation(websiteId)
  }

  async generateHeaderConfig(websiteId: number) {
    return HeaderConfigService.generateDynamicHeaderConfig(websiteId)
  }

  // ========== TOOLS API ==========
  async getToolsCategories(websiteId: number = WEBSITE_ID) {
    return this.toolsClient.getCategories(websiteId)
  }

  async getCategoryTools(categoryId: number, websiteId: number = WEBSITE_ID) {
    return this.toolsClient.getCategoryTools(categoryId, websiteId)
  }

  async getCategoryToolsByPath(categoryPath: string, websiteId: number = WEBSITE_ID) {
    return this.toolsClient.getCategoryToolsByPath(categoryPath, websiteId)
  }

  async getAllTools(websiteId: number = WEBSITE_ID) {
    return this.toolsClient.getAllTools(websiteId)
  }

  async getToolsMainPage(websiteId: number = WEBSITE_ID) {
    return this.toolsClient.getMainPage(websiteId)
  }

  async getToolsSitemap(websiteId: number = WEBSITE_ID) {
    return this.toolsClient.getSitemap(websiteId)
  }

  async getToolsStats(websiteId: number = WEBSITE_ID) {
    return this.toolsClient.getStats(websiteId)
  }

  // ========== CACHE MANAGEMENT ==========
  clearCache(): void {
    this.renderClient.clearCache()
    this.navigationClient.clearCache()
    this.toolsClient.clearCache()
  }

  invalidateNavigationCache(websiteId: number): void {
    this.navigationClient.invalidateNavigationCache(websiteId)
  }

  invalidateToolsCache(websiteId: number = WEBSITE_ID): void {
    this.toolsClient.invalidateToolsCache(websiteId)
  }
}

// Instance singleton
export const apiClient = new APIClient()

// ✅ Exports directs
export const renderAPI = renderAPIInstance
export { navigationAPI }
export { toolsAPI }
export { HeaderConfigService }

// Exports de classes
export { RenderAPIClient } from './render'
export { NavigationAPIClient } from './navigation'
export { ToolsAPIClient } from './tools'
export { BaseAPIClient } from './base'

// Exports de types API
export type {
  RenderResponse,
  SitemapResponse,
  SitemapPage,
  NavigationResponse,
  NavigationItem
} from '@/lib/types/api'

// Exports de types Tools
export type {
  ToolCategory,
  Tool,
  ToolsByCategoryResponse,
  CategoriesResponse,
  AllToolsResponse,
  MainPageResponse,
  ToolsSitemapResponse,
  ToolsStatsResponse
} from '@/lib/types/tools'

// Exports de types Header
export type {
  HeaderConfig,
  MenuItem,
  HeaderComponentProps
} from '@/components/layout/headers/types'