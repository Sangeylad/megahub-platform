// lib/api/health.ts
import { BaseAPIClient } from './base'

export class HealthAPIClient extends BaseAPIClient {
  /**
   * Health check public
   * GET /public/health/status/
   */
  async checkPublicHealth(): Promise<boolean> {
    const response = await this.fetchWithErrorHandling<{ status: string }>(
      '/seo/public/health/status/'
    )
    
    return response?.status === 'healthy'
  }

  /**
   * Health check global (si besoin)
   * GET /seo/health/
   */
  async checkGlobalHealth(): Promise<boolean> {
    const response = await this.fetchWithErrorHandling<{ status: string }>(
      '/seo/health/'
    )
    
    return response?.status === 'healthy'
  }
}