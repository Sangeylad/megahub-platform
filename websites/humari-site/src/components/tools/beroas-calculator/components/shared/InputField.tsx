// src/components/tools/beroas-calculator/components/shared/InputField.tsx
'use client';

import { forwardRef } from 'react';

interface InputFieldProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  type?: 'number';
  step?: number;
  min?: number;
  max?: number;
  suffix?: string;
  helpText?: string;
  required?: boolean;
  className?: string;
}

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(
  ({ 
    label, 
    value, 
    onChange, 
    step = 0.01, 
    min = 0,
    max,
    suffix = '€',
    helpText,
    required = false,
    className = ''
  }, ref) => {
    return (
      <div className={`space-y-2 ${className}`}>
        <label className="block text-sm font-semibold text-neutral-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        <div className="relative">
          <input
            ref={ref}
            type="number"
            value={value}
            onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
            step={step}
            min={min}
            max={max}
            className="
              w-full px-4 py-3 pr-12 bg-white border-2 border-neutral-200 rounded-lg
              focus:border-brand-500 focus:ring-4 focus:ring-brand-100
              transition-all duration-200 font-semibold text-neutral-900
              hover:border-neutral-300
            "
          />
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-500 font-medium">
            {suffix}
          </span>
        </div>
        {helpText && (
          <p className="text-xs text-neutral-500 leading-relaxed">{helpText}</p>
        )}
      </div>
    );
  }
);

InputField.displayName = 'InputField';