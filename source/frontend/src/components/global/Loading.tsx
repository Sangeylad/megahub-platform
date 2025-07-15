// frontend/src/components/global/Loading.tsx
import { cn } from '@/utils';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  message?: string;
}

export default function Loading({ 
  size = 'md', 
  className,
  message = 'Chargement...'
}: LoadingProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  };

  return (
    <div className={cn(
      'flex flex-col items-center justify-center gap-3 p-6',
      className
    )}>
      <div className={cn('spinner', sizeClasses[size])} />
      {message && (
        <p className="text-sm text-neutral-600 animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
}
