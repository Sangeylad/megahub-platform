// frontend/src/utils/formatting/cn.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combine classes avec Tailwind merge
 * @param inputs - Classes à combiner
 * @returns Classes optimisées
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export default cn;
