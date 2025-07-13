// /var/www/megahub/websites/humari-site/src/components/sections/HeroSection.tsx
import Link from 'next/link'
import type { SectionComponentProps } from '@/lib/types/sections'

interface HeroSectionProps {
  // Contenu de base
  title: string
  subtitle?: string
  cta_text?: string
  cta_url?: string
  secondary_cta_text?: string
  secondary_cta_url?: string
  
  // 🎯 VARIANTS SCALABLES
  variant: 'minimal' | 'standard' | 'impact' | 'hero'
  layout: 'centered' | 'split'
  background: 'gradient-brand' | 'gradient-dark' | 'solid-light' | 'solid-dark'
  
  // 🎨 OPTIONS IMPACT (conditionnelles)
  show_badge?: boolean
  badge_text?: string
  show_stats?: boolean
  stats?: Array<{
    number: string
    label: string
  }>
}

export function HeroSection({ data }: SectionComponentProps<HeroSectionProps>) {
  const {
    title,
    subtitle,
    cta_text,
    cta_url,
    secondary_cta_text,
    secondary_cta_url,
    variant = 'standard',
    layout = 'centered',
    background = 'gradient-brand',
    show_badge = false,
    badge_text,
    show_stats = false,
    stats
  } = data

  // 🧠 LOGIQUE DE VARIANTS
  const isMinimal = variant === 'minimal'
  const isStandard = variant === 'standard'
  const isImpact = variant === 'impact'
  const isHero = variant === 'hero'
  
  const isDark = background.includes('dark')
  const isLight = background === 'solid-light'
  
  // Auto-corrections intelligentes
  const finalLayout = isMinimal ? 'centered' : layout
  const showBadge = show_badge && badge_text && (isImpact || isHero)
  const showStats = show_stats && stats && stats.length > 0 && (isImpact || isHero)
  const showSecondary = secondary_cta_text && secondary_cta_url && !isMinimal

  // 🎨 CLASSES DYNAMIQUES
  const getBackgroundClass = () => {
    const backgrounds = {
      'gradient-brand': 'bg-gradient-to-br from-brand-500 via-brand-600 to-brand-800',
      'gradient-dark': 'bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700',
      'solid-light': 'bg-neutral-50',
      'solid-dark': 'bg-dark-900'
    }
    return backgrounds[background]
  }

  const getSizeClass = () => {
    const sizes = {
      'minimal': 'min-h-[400px] py-16',
      'standard': 'min-h-[500px] py-20',
      'impact': 'min-h-[600px] py-24',
      'hero': 'min-h-[700px] py-32'
    }
    return sizes[variant]
  }

  const getTitleSize = () => {
    const sizes = {
      'minimal': 'text-3xl md:text-4xl',
      'standard': 'text-4xl md:text-5xl', 
      'impact': 'text-5xl md:text-6xl lg:text-7xl',
      'hero': 'text-6xl md:text-7xl lg:text-8xl'
    }
    return sizes[variant]
  }

  const getSubtitleSize = () => {
    const sizes = {
      'minimal': 'text-base md:text-lg',
      'standard': 'text-lg md:text-xl',
      'impact': 'text-xl md:text-2xl',
      'hero': 'text-2xl md:text-3xl'
    }
    return sizes[variant]
  }

  // 🎨 COULEURS
  const textColor = isDark ? 'text-white' : isLight ? 'text-dark-900' : 'text-white'
  const subtitleColor = isDark ? 'text-neutral-200' : isLight ? 'text-neutral-600' : 'text-white/90'
  
  const primaryBtnClass = isDark || !isLight
    ? 'bg-white text-dark-900 hover:bg-neutral-100 hover:shadow-xl'
    : 'bg-brand-500 text-white hover:bg-brand-600 hover:shadow-brand'
    
  const secondaryBtnClass = isDark || !isLight
    ? 'border-white text-white hover:bg-white hover:text-dark-900'
    : 'border-dark-900 text-dark-900 hover:bg-dark-900 hover:text-white'

  return (
    <section className={`${getSizeClass()} ${getBackgroundClass()} relative overflow-hidden flex items-center`}>
      
      {/* 🌟 BACKGROUND EFFECTS pour impact/hero */}
      {(isImpact || isHero) && (
        <>
          {/* Mesh gradient overlay */}
          <div className="absolute inset-0 bg-gradient-radial from-transparent via-black/5 to-black/20" />
          
          {/* Floating elements */}
          <div className="absolute top-20 left-10 w-32 h-32 bg-white/5 rounded-full blur-xl animate-float" />
          <div className="absolute bottom-20 right-10 w-24 h-24 bg-white/5 rounded-full blur-lg animate-float" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-white/3 rounded-full blur-md animate-float" style={{ animationDelay: '2s' }} />
        </>
      )}

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        {finalLayout === 'split' ? (
          // 🔄 SPLIT LAYOUT
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <div className="text-left">
              <HeroContent />
            </div>
            <div className="relative lg:justify-self-end">
              <SplitVisual />
            </div>
          </div>
        ) : (
          // 📍 CENTERED LAYOUT
          <div className="max-w-5xl mx-auto text-center">
            <HeroContent />
          </div>
        )}
      </div>
    </section>
  )

  // 🧩 CONTENU PRINCIPAL
  function HeroContent() {
    return (
      <>
        {/* 🏷️ BADGE pour impact/hero */}
        {showBadge && (
          <div className="inline-flex items-center px-6 py-3 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white text-sm font-medium mb-8 animate-pulse-brand">
            <span className="w-2 h-2 bg-brand-400 rounded-full mr-3 animate-pulse"></span>
            {badge_text}
          </div>
        )}

        {/* 📝 TITRE */}
        <h1 className={`font-bold ${textColor} ${getTitleSize()} leading-tight`}>
          {(isImpact || isHero) ? (
            // Titre avec effet gradient pour variants élevés
            <>
              {title.split(' ').map((word, index) => (
                <span key={index} className={index % 2 === 0 ? 'inline-block' : 'bg-gradient-to-r from-brand-400 to-brand-600 bg-clip-text text-transparent inline-block'}>
                  {word}{' '}
                </span>
              ))}
            </>
          ) : (
            title
          )}
        </h1>

        {/* 📄 SOUS-TITRE */}
        {subtitle && (
          <p className={`mt-6 ${getSubtitleSize()} ${subtitleColor} max-w-3xl ${
            finalLayout === 'centered' ? 'mx-auto' : ''
          } leading-relaxed`}>
            {subtitle}
          </p>
        )}

        {/* 📊 STATS pour impact/hero */}
        {showStats && (
          <div className={`mt-10 grid grid-cols-2 ${stats!.length > 2 ? 'md:grid-cols-4' : 'md:grid-cols-2'} gap-8`}>
            {stats!.map((stat, index) => (
              <div key={index} className={`${finalLayout === 'centered' ? 'text-center' : 'text-left'}`}>
                <div className={`text-3xl md:text-4xl font-bold ${textColor} mb-2`}>
                  {stat.number}
                </div>
                <div className={`text-sm ${subtitleColor} font-medium uppercase tracking-wide`}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 🎯 BOUTONS CTA */}
        {(cta_text || secondary_cta_text) && (
          <div className={`mt-12 flex flex-col sm:flex-row gap-4 ${
            finalLayout === 'centered' ? 'justify-center' : 'justify-start'
          }`}>
            {/* Bouton principal */}
            {cta_text && cta_url && (
              <Link
                href={cta_url}
                className={`group inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-2xl transition-all duration-300 transform hover:scale-105 ${primaryBtnClass}`}
              >
                {cta_text}
                <svg className="ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </Link>
            )}

            {/* Bouton secondaire */}
            {showSecondary && (
              <Link
                href={secondary_cta_url!}
                className={`inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-2xl border-2 transition-all duration-300 ${secondaryBtnClass}`}
              >
                {secondary_cta_text}
              </Link>
            )}
          </div>
        )}
      </>
    )
  }

  // 🎨 VISUEL SPLIT
  function SplitVisual() {
    return (
      <div className="relative">
        {/* Container principal */}
        <div className="aspect-square max-w-lg mx-auto relative">
          
          {/* Background shapes */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-white/5 rounded-3xl backdrop-blur-sm border border-white/20 transform rotate-6"></div>
          <div className="absolute inset-4 bg-gradient-to-tr from-brand-500/20 to-brand-400/10 rounded-2xl transform -rotate-3"></div>
          
          {/* Contenu central */}
          <div className="absolute inset-8 bg-white/10 backdrop-blur-md rounded-xl border border-white/30 flex items-center justify-center">
            {/* Icône ou illustration */}
            <div className="text-8xl">
              {isHero ? '🚀' : isImpact ? '🎯' : isStandard ? '⚡' : '💡'}
            </div>
          </div>
          
          {/* Floating elements */}
          {(isImpact || isHero) && (
            <>
              <div className="absolute -top-4 -right-4 w-16 h-16 bg-brand-400/20 rounded-full blur-md animate-float"></div>
              <div className="absolute -bottom-4 -left-4 w-12 h-12 bg-white/20 rounded-full blur-sm animate-float" style={{ animationDelay: '1s' }}></div>
            </>
          )}
        </div>
      </div>
    )
  }
}