// src/components/tools/glossary-search/components/SearchInput.tsx
'use client'

import { useState } from 'react'
import { LoadingSpinner } from './shared/LoadingSpinner'

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  onClear: () => void
  placeholder?: string
  isLoading?: boolean
  disabled?: boolean
  className?: string
}

export function SearchInput({ 
  value, 
  onChange, 
  onClear,
  placeholder = 'Rechercher un terme...', 
  isLoading = false,
  disabled = false,
  className = ''
}: SearchInputProps) {
  
  const [isFocused, setIsFocused] = useState(false)
  
  return (
    <div className={`relative ${className}`}>
      <div className={`
        relative flex items-center bg-white border-2 rounded-xl transition-all duration-200
        ${isFocused ? 'border-brand-400 shadow-lg shadow-brand/10' : 'border-neutral-300'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-brand-300'}
      `}>
        {/* Icône de recherche */}
        <div className="absolute left-4 text-neutral-400">
          {isLoading ? (
            <LoadingSpinner size="small" />
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          )}
        </div>
        
        {/* Input */}
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          disabled={disabled}
          className="
            w-full pl-12 pr-12 py-4 text-lg bg-transparent border-none outline-none
            placeholder-neutral-500 text-neutral-800
            disabled:cursor-not-allowed
          "
        />
        
        {/* Bouton clear */}
        {value && !disabled && (
          <button
            onClick={onClear}
            className="
              absolute right-4 p-1 text-neutral-400 hover:text-neutral-600 
              transition-colors duration-200
            "
            aria-label="Effacer la recherche"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
      
      {/* Raccourci clavier hint */}
      {!isFocused && !value && (
        <div className="absolute right-4 top-1/2 transform -translate-y-1/2 hidden md:flex items-center">
          <kbd className="px-2 py-1 text-xs font-semibold text-neutral-500 bg-neutral-100 border border-neutral-300 rounded">
            Ctrl+K
          </kbd>
        </div>
      )}
    </div>
  )
}