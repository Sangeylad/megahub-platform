// lib/types/tools.ts
export interface ToolCategory {
  id: number
  title: string
  url_path: string
  tools_count: number
  description: string
  status: string
  last_updated: string
}

export interface Tool {
  id: number
  title: string
  url_path: string
  description: string
  status?: string
  last_updated?: string
}

export interface ToolsByCategoryResponse {
  category: {
    id: number
    title: string
    url_path: string
    description: string
  }
  tools: Tool[]
  tools_count: number
  generated_at: string
}

export interface CategoriesResponse {
  categories: ToolCategory[]
  total_categories: number
  website_id: number
  generated_at: string
}

export interface AllToolsResponse {
  tools_by_category: Array<{
    category: {
      id: number
      title: string
      url_path: string
      description: string
    }
    tools: Tool[]
    tools_count: number
  }>
  total_tools: number
  total_categories: number
  website_id: number
  generated_at: string
}

export interface MainPageResponse {
  main_page: {
    id: number
    title: string
    url_path: string
    description: string
    status: string
    last_updated: string
  }
  categories_preview: ToolCategory[]
  total_categories: number
  website_id: number
  generated_at: string
}

export interface ToolsSitemapResponse {
  tools_sitemap: Array<{
    url: string
    lastmod: string
    priority: number
    changefreq: string
    page_type: string
    hierarchy_level: number
  }>
  total_pages: number
  website_id: number
  generated_at: string
}

export interface ToolsStatsResponse {
  stats: {
    total_tools: number
    total_categories: number
    tools_by_status: Record<string, number>
    most_active_category: {
      id: number
      title: string
      tools_count: number
    } | null
    last_updated: string
  }
  website_id: number
}