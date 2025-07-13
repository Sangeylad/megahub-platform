// /var/www/megahub/websites/humari-site/src/lib/api/base.ts
export abstract class BaseAPIClient {
  protected baseURL: string
  protected cache = new Map<string, { data: unknown; timestamp: number; ttl: number }>()
  protected readonly defaultTTL = 3600000 // 1 heure

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  protected isValidCache(key: string): boolean {
    const entry = this.cache.get(key)
    if (!entry) return false
    
    const isExpired = Date.now() - entry.timestamp > entry.ttl
    if (isExpired) {
      this.cache.delete(key)
      return false
    }
    
    return true
  }

  protected setCache<T>(key: string, data: T, ttl = this.defaultTTL): void {
    this.cache.set(key, { data, timestamp: Date.now(), ttl })
  }

  protected async fetchWithErrorHandling<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T | null> {
    try {
      // 🔒 SÉCURISÉ : toujours utiliser l'URL relative
      const url = endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`
      
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers
        },
        cache: 'no-store',
        ...options
      })

      if (!response.ok) {
        console.error(`API Error: ${response.status} ${response.statusText}`)
        return null
      }

      return await response.json()
    } catch (error) {
      console.error('Network error:', error)
      return null
    }
  }

  clearCache(): void {
    this.cache.clear()
  }
}