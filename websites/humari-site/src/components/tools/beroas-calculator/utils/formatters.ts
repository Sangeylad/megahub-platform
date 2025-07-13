export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(value);
};

export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('fr-FR').format(Math.round(value));
};

export const formatPercent = (value: number): string => {
  return `${value.toFixed(1)}%`;
};

export const getBeroasStatusText = (beroas: number, unitMargin: number): string => {
  if (unitMargin <= 0) return '❌ Non rentable';
  if (beroas <= 2) return '🚀 Excellent (≤ 2.0)';
  if (beroas <= 3) return '✅ Très bon (≤ 3.0)';
  if (beroas <= 4) return '👍 Bon (≤ 4.0)';
  return '⚠️ Difficile (> 4.0)';
};

export const getBeroasCellClass = (beroas: number, margin: number): string => {
  if (margin <= 0) return 'bg-neutral-100 text-neutral-400';
  if (beroas <= 2.0) return 'bg-green-200 text-green-900';
  if (beroas <= 2.5) return 'bg-green-100 text-green-800';
  if (beroas <= 3.5) return 'bg-blue-100 text-blue-800';
  if (beroas <= 5.0) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
};