// src/components/tools/glossary-search/components/CategoryFilter.tsx
'use client'

import { useCategories } from '../hooks/useCategories'

interface CategoryFilterProps {
  selectedCategory: string
  onCategoryChange: (category: string) => void
  className?: string
}

export function CategoryFilter({
  selectedCategory,
  onCategoryChange,
  className = ''
}: CategoryFilterProps) {
  
  const { categories, isLoading, error } = useCategories()
  
  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="h-12 bg-neutral-200 rounded-lg"></div>
      </div>
    )
  }
  
  if (error || categories.length === 0) {
    return null
  }
  
  // ✅ Handler avec debug et vérification
  const handleCategoryChange = (value: string) => {
    console.log('🏷️ CategoryFilter: Category changed from', selectedCategory, 'to', value) // Debug
    onCategoryChange(value)
  }
  
  console.log('🏷️ CategoryFilter: Current selectedCategory:', selectedCategory) // Debug
  console.log('🏷️ CategoryFilter: Available categories:', categories.map(c => ({ id: c.id, slug: c.slug, name: c.name }))) // Debug
  
  return (
    <div className={className}>
      <label htmlFor="category-filter" className="block text-sm font-medium text-neutral-700 mb-2">
        Filtrer par catégorie
      </label>
      
      <select
        id="category-filter"
        value={selectedCategory}
        onChange={(e) => handleCategoryChange(e.target.value)}
        className="
          w-full px-4 py-3 bg-white border border-neutral-300 rounded-lg
          focus:border-brand-400 focus:ring-2 focus:ring-brand-200 focus:outline-none
          transition-colors duration-200
        "
      >
        <option value="">Toutes les catégories</option>
        
        {categories.map((category) => (
          <option key={category.id} value={category.slug}>
            {category.name}
            {category.terms_count && ` (${category.terms_count})`}
          </option>
        ))}
      </select>
    </div>
  )
}