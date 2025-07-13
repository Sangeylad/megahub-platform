// src/components/tools/glossary-search/components/shared/LoadingSpinner.tsx
interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  className?: string
}

export function LoadingSpinner({ size = 'medium', className = '' }: LoadingSpinnerProps) {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6', 
    large: 'w-8 h-8'
  }
  
  return (
    <div className={`inline-flex items-center justify-center ${className}`}>
      <div className={`${sizeClasses[size]} border-2 border-brand-200 border-t-brand-500 rounded-full animate-spin`} />
    </div>
  )
}