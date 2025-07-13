import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Validation responsive images
export function getOptimizedImageProps(src: string, alt: string) {
  return {
    src,
    alt,
    loading: 'lazy' as const,
    decoding: 'async' as const,
    sizes: "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  }
}

// Format des dates FR
export function formatDate(date: string | Date, options?: Intl.DateTimeFormatOptions): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options
  })
}
