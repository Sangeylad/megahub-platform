// src/components/tools/beroas-calculator/components/shared/MetricCard.tsx
'use client';

interface MetricCardProps {
  icon: string;
  label: string;
  value: string;
  subtitle?: string;
  status?: string;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  className?: string;
}

export function MetricCard({ 
  icon, 
  label, 
  value, 
  subtitle, 
  status, 
  variant = 'default',
  className = ''
}: MetricCardProps) {
  const variantClasses = {
    default: 'bg-white border-neutral-200',
    primary: 'bg-gradient-to-br from-brand-50 to-brand-100 border-brand-200',
    success: 'bg-gradient-to-br from-green-50 to-green-100 border-green-200',
    warning: 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200',
    danger: 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
  };

  return (
    <div className={`
      ${variantClasses[variant]}
      rounded-xl border p-6 transition-all duration-300 hover:shadow-lg hover:-translate-y-1
      ${className}
    `}>
      <div className="flex items-center gap-4">
        <div className="text-3xl flex-shrink-0">{icon}</div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-neutral-600 uppercase tracking-wide">
            {label}
          </div>
          <div className="text-2xl font-bold text-neutral-900 mt-1">
            {value}
          </div>
          {subtitle && (
            <div className="text-sm text-neutral-500 mt-1">{subtitle}</div>
          )}
          {status && (
            <div className="text-sm font-medium mt-2">{status}</div>
          )}
        </div>
      </div>
    </div>
  );
}