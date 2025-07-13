'use client'

import Link from 'next/link'
import { BeroasCalculator } from '../tools/beroas-calculator/BeroasCalculator'
import type { SectionComponentProps } from '@/lib/types/sections'

interface BeroasCalculatorSectionProps {
  title?: string
  subtitle?: string
  initial_tab: 'basic' | 'advanced' | 'volume' | 'matrix'
  show_export: boolean
  variant: 'full' | 'embedded' | 'minimal'
  background: 'neutral' | 'white' | 'brand' | 'transparent'
  custom_cta_text?: string
  custom_cta_url?: string
  tracking_id?: string
}

export function BeroasCalculatorSection({ data }: SectionComponentProps<BeroasCalculatorSectionProps>) {
  const {
    title,
    subtitle,
    initial_tab = 'basic',
    show_export = true,
    variant = 'full',
    background = 'neutral',
    custom_cta_text,
    custom_cta_url,
    tracking_id
  } = data

  // 🧠 Logique de variants
  const isEmbedded = variant === 'embedded'
  const isMinimal = variant === 'minimal'
  const isBrand = background === 'brand'

  // Auto-corrections intelligentes
  const showHeader = isEmbedded && (title || subtitle)
  const showCta = custom_cta_text && custom_cta_url

  // 🎨 Classes dynamiques
  const getBackgroundClass = () => {
    const backgrounds = {
      'neutral': 'bg-neutral-50',
      'white': 'bg-white',
      'brand': 'bg-gradient-to-br from-brand-50 to-brand-100',
      'transparent': 'bg-transparent'
    }
    return backgrounds[background]
  }

  const getSizeClass = () => {
    const sizes = {
      'full': 'py-20',
      'embedded': 'py-16', 
      'minimal': 'py-12'
    }
    return sizes[variant]
  }

  const getContainerClass = () => {
    const containers = {
      'full': 'max-w-7xl mx-auto',
      'embedded': 'max-w-6xl mx-auto',
      'minimal': 'max-w-4xl mx-auto'
    }
    return containers[variant]
  }

  // 🎨 Couleurs texte
  const titleColor = isBrand ? 'text-brand-800' : 'text-neutral-800'
  const subtitleColor = isBrand ? 'text-brand-600' : 'text-neutral-600'

  return (
    <section 
      className={`${getSizeClass()} ${getBackgroundClass()} relative`}
      data-section="beroas-calculator"
      data-tracking-id={tracking_id}
    >
      <div className={`${getContainerClass()} px-4 sm:px-6 lg:px-8`}>
        
        {showHeader && (
          <HeaderContent />
        )}

        <CalculatorContent />

        {showCta && (
          <CtaContent />
        )}

      </div>
    </section>
  )

  // 🧩 Header Content
  function HeaderContent() {
    return (
      <div className="text-center mb-12">
        {title && (
          <h2 className={`text-3xl md:text-4xl font-bold ${titleColor} mb-6`}>
            {title}
          </h2>
        )}
        {subtitle && (
          <p className={`text-lg md:text-xl ${subtitleColor} max-w-3xl mx-auto leading-relaxed`}>
            {subtitle}
          </p>
        )}
      </div>
    )
  }

  // 🧮 Calculator Content
  function CalculatorContent() {
    return (
      <div className="relative">
        <div className={isMinimal ? 'shadow-sm' : 'shadow-lg rounded-xl overflow-hidden'}>
          <BeroasCalculator
            initialTab={initial_tab}
            showExport={show_export}
            className="w-full"
          />
        </div>
      </div>
    )
  }

  // 🎯 CTA Content
  function CtaContent() {
    return (
      <div className="text-center mt-12">
        <Link
          href={custom_cta_url!}
          className="group inline-flex items-center justify-center gap-3 bg-brand-500 hover:bg-brand-600 text-white font-semibold px-8 py-4 rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-brand/20 hover:-translate-y-1"
          data-tracking-id={tracking_id}
        >
          {custom_cta_text}
          <svg 
            className="w-5 h-5 transition-transform group-hover:translate-x-1" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M17 8l4 4m0 0l-4 4m4-4H3" 
            />
          </svg>
        </Link>
      </div>
    )
  }
}