// /var/www/megahub/websites/humari-site/src/components/sections/ServicesGrid.tsx
import Link from 'next/link'
import type { SectionComponentProps } from '@/lib/types/sections'

interface ServicesGridProps {
  // Contenu
  title?: string
  subtitle?: string
  services: Array<{
    title: string
    description: string
    icon?: string
    image?: string
    cta_text?: string
    cta_url?: string
    badge?: string
    features?: string[]
  }>
  
  // 🎯 VARIANTS & LAYOUT
  variant: 'minimal' | 'standard' | 'impact' | 'featured'
  layout: 'grid' | 'masonry' | 'carousel' | 'alternating'
  card_style: 'flat' | 'elevated' | 'bordered' | 'gradient'
  background: 'transparent' | 'light' | 'dark' | 'brand'
  columns: 2 | 3 | 4
  show_cta: boolean
}

export function ServicesGrid({ data }: SectionComponentProps<ServicesGridProps>) {
  const {
    title,
    subtitle,
    services,
    variant = 'standard',
    layout = 'grid',
    card_style = 'elevated',
    background = 'transparent',
    columns = 3,
    show_cta = true
  } = data

  // 🧠 LOGIQUE VARIANTS
  const isMinimal = variant === 'minimal'
  const isFeatured = variant === 'featured'
  const showHeader = title || subtitle
  
  // Auto-corrections intelligentes
  const finalColumns = services.length < columns ? services.length : columns
  const finalLayout = services.length <= 2 ? 'grid' : layout
  const showServiceCta = show_cta && !isMinimal

  // 🎨 CLASSES DYNAMIQUES
  const getBackgroundClass = () => {
    const backgrounds = {
      'transparent': 'bg-transparent',
      'light': 'bg-neutral-50',
      'dark': 'bg-dark-900',
      'brand': 'bg-gradient-to-br from-brand-50 to-neutral-50'
    }
    return backgrounds[background]
  }

  const getGridClass = () => {
    if (finalLayout === 'alternating') {
      return 'space-y-16'
    }
    
    const grids = {
      2: 'grid-cols-1 lg:grid-cols-2',
      3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3', 
      4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
    }
    
    return `grid gap-8 ${grids[finalColumns as keyof typeof grids]}`
  }

  const getPadding = () => {
    const paddings = {
      'minimal': 'py-12',
      'standard': 'py-16',
      'impact': 'py-20',
      'featured': 'py-24'
    }
    return paddings[variant]
  }

  const isDark = background === 'dark'
  const textColor = isDark ? 'text-white' : 'text-dark-900'
  const subtitleColor = isDark ? 'text-neutral-300' : 'text-neutral-600'

  return (
    <section className={`${getPadding()} ${getBackgroundClass()} relative overflow-hidden`}>
      {/* 🌟 BACKGROUND EFFECTS pour featured */}
      {isFeatured && (
        <div className="absolute inset-0 bg-gradient-radial from-brand-500/5 via-transparent to-transparent" />
      )}

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* 🎨 HEADER */}
        {showHeader && (
          <div className={`text-center mb-16 ${isFeatured ? 'mb-20' : ''}`}>
            {title && (
              <h2 className={`text-3xl md:text-4xl lg:text-5xl font-bold ${textColor} mb-6`}>
                {isFeatured ? (
                  <span className="bg-gradient-to-r from-brand-500 to-brand-700 bg-clip-text text-transparent">
                    {title}
                  </span>
                ) : (
                  title
                )}
              </h2>
            )}
            {subtitle && (
              <p className={`text-lg md:text-xl ${subtitleColor} max-w-3xl mx-auto leading-relaxed`}>
                {subtitle}
              </p>
            )}
          </div>
        )}

        {/* 🗂️ SERVICES GRID */}
        <div className={finalLayout === 'alternating' ? 'space-y-16' : getGridClass()}>
          {services.map((service, index) => (
            <ServiceCard
              key={index}
              service={service}
              index={index}
              variant={variant}
              cardStyle={card_style}
              background={background}
              showCta={showServiceCta}
              isAlternating={finalLayout === 'alternating'}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

// 🧩 COMPOSANT SERVICE CARD
function ServiceCard({
  service,
  index,
  variant,
  cardStyle,
  background,
  showCta,
  isAlternating
}: {
  service: ServicesGridProps['services'][0]
  index: number
  variant: ServicesGridProps['variant']
  // layout: string  // ✅ Commenter le type aussi
  cardStyle: ServicesGridProps['card_style']
  background: ServicesGridProps['background']
  showCta: boolean
  isAlternating: boolean
}) {

  const isDark = background === 'dark'
  const isFeatured = variant === 'featured'
  const isMinimal = variant === 'minimal'
  
  // 🎨 STYLES DE CARTE
  const getCardClass = () => {
    const base = 'group relative transition-all duration-300 rounded-2xl overflow-hidden'
    
    const styles = {
      'flat': `${base} bg-transparent`,
      'elevated': `${base} ${isDark ? 'bg-dark-800 hover:bg-dark-700' : 'bg-white hover:shadow-xl'} shadow-lg hover:shadow-2xl transform hover:-translate-y-1`,
      'bordered': `${base} ${isDark ? 'bg-dark-800 border-dark-700' : 'bg-white border-neutral-200'} border-2 hover:border-brand-300`,
      'gradient': `${base} bg-gradient-to-br from-white to-neutral-50 hover:from-brand-50 hover:to-white shadow-lg hover:shadow-xl`
    }
    
    return styles[cardStyle]
  }

  const textColor = isDark ? 'text-white' : 'text-dark-900'
  const descColor = isDark ? 'text-neutral-300' : 'text-neutral-600'
  const featureColor = isDark ? 'text-neutral-400' : 'text-neutral-500'

  // Layout alternating (un à gauche, un à droite)
  if (isAlternating) {
    const isEven = index % 2 === 0
    
    return (
      <div className={`grid lg:grid-cols-2 gap-12 items-center ${!isEven ? 'lg:flex-row-reverse' : ''}`}>
        {/* Contenu */}
        <div className={`${!isEven ? 'lg:order-2' : ''}`}>
          <ServiceContent />
        </div>
        
        {/* Visuel */}
        <div className={`${!isEven ? 'lg:order-1' : ''}`}>
          <div className="aspect-square bg-gradient-to-br from-brand-100 to-brand-200 rounded-3xl flex items-center justify-center">
            <span className="text-6xl">{service.icon || '⚡'}</span>
          </div>
        </div>
      </div>
    )
  }

  // Layout standard
  return (
    <div className={getCardClass()}>
      <div className={`p-8 ${isFeatured ? 'p-10' : ''} ${isMinimal ? 'p-6' : ''} h-full flex flex-col`}>
        <ServiceContent />
      </div>
      
      {/* Effet hover pour carte elevated */}
      {cardStyle === 'elevated' && (
        <div className="absolute inset-0 bg-gradient-to-r from-brand-500/0 via-brand-500/5 to-brand-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl" />
      )}
    </div>
  )

  function ServiceContent() {
    return (
      <>
        {/* 🏷️ BADGE */}
        {service.badge && (
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-brand-100 text-brand-700 text-sm font-medium mb-4">
            {service.badge}
          </div>
        )}

        {/* 🎨 ICÔNE + TITRE */}
        <div className="flex items-start gap-4 mb-4">
          {service.icon && (
            <div className={`flex-shrink-0 ${isFeatured ? 'text-5xl' : 'text-4xl'}`}>
              {service.icon}
            </div>
          )}
          <div className="flex-1">
            <h3 className={`font-bold ${textColor} mb-2 ${
              isFeatured ? 'text-2xl' : 'text-xl'
            }`}>
              {service.title}
            </h3>
          </div>
        </div>

        {/* 📝 DESCRIPTION */}
        <p className={`${descColor} leading-relaxed flex-1 mb-6`}>
          {service.description}
        </p>

        {/* ✨ FEATURES */}
        {service.features && service.features.length > 0 && (
          <ul className="space-y-2 mb-6">
            {service.features.map((feature, idx) => (
              <li key={idx} className={`flex items-center gap-3 ${featureColor} text-sm`}>
                <span className="w-1.5 h-1.5 bg-brand-500 rounded-full flex-shrink-0"></span>
                {feature}
              </li>
            ))}
          </ul>
        )}

        {/* 🎯 CTA */}
        {showCta && service.cta_text && service.cta_url && (
          <div className="mt-auto">
            <Link
              href={service.cta_url}
              className={`group inline-flex items-center font-semibold transition-all duration-200 ${
                isDark ? 'text-brand-400 hover:text-brand-300' : 'text-brand-600 hover:text-brand-500'
              }`}
            >
              {service.cta_text}
              <svg className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>
        )}
      </>
    )
  }
}