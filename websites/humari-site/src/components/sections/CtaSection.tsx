// /var/www/megahub/websites/humari-site/src/components/sections/CtaSection.tsx
import Link from 'next/link'
import type { SectionComponentProps } from '@/lib/types/sections'

interface CtaSectionProps {
  // Contenu principal
  title: string
  subtitle?: string
  description?: string
  
  // 🎯 ACTIONS
  primary_cta_text: string
  primary_cta_url: string
  secondary_cta_text?: string
  secondary_cta_url?: string
  
  // 🎨 VARIANTS & STYLE
  variant: 'minimal' | 'standard' | 'impact' | 'urgent'
  layout: 'centered' | 'split' | 'banner' | 'floating'
  style: 'solid' | 'gradient' | 'outlined' | 'glass'
  background: 'brand' | 'dark' | 'light' | 'gradient' | 'image'
  urgency_level: 'none' | 'low' | 'medium' | 'high'
  
  // 🔥 ENHANCEMENTS
  show_guarantee?: boolean
  guarantee_text?: string
  show_social_proof?: boolean
  social_proof?: string
  show_countdown?: boolean
  countdown_text?: string
  badge_text?: string
  
  // 📊 STATS rapides
  stats?: Array<{
    number: string
    label: string
  }>
}

export function CtaSection({ data }: SectionComponentProps<CtaSectionProps>) {
  const {
    title,
    subtitle,
    description,
    primary_cta_text,
    primary_cta_url,
    secondary_cta_text,
    secondary_cta_url,
    variant = 'standard',
    layout = 'centered',
    style = 'solid',
    background = 'brand',
    urgency_level = 'none',
    show_guarantee = false,
    guarantee_text,
    show_social_proof = false,
    social_proof,
    show_countdown = false,
    countdown_text,
    badge_text,
    stats
  } = data

  // 🧠 LOGIQUE VARIANTS
  const isMinimal = variant === 'minimal'
  const isUrgent = variant === 'urgent'
  const isImpact = variant === 'impact'
  const hasUrgency = urgency_level !== 'none'
  const showSecondary = secondary_cta_text && secondary_cta_url && !isMinimal

  // 🎨 CLASSES DYNAMIQUES
  const getBackgroundClass = () => {
    const backgrounds = {
      'brand': 'bg-gradient-to-r from-brand-500 to-brand-600',
      'dark': 'bg-gradient-to-r from-dark-900 to-dark-800',
      'light': 'bg-neutral-50',
      'gradient': 'bg-gradient-to-br from-brand-500 via-brand-600 to-dark-700',
      'image': 'bg-gradient-to-r from-brand-500/90 to-brand-600/90' // overlay sur image
    }
    return backgrounds[background]
  }

  const getContainerStyle = () => {
    const styles = {
      'solid': '',
      'gradient': 'bg-gradient-to-r from-white/10 to-white/5 backdrop-blur-sm',
      'outlined': `border-2 ${isDark ? 'border-white/20' : 'border-brand-200'} bg-transparent`,
      'glass': 'bg-white/10 backdrop-blur-lg border border-white/20'
    }
    return styles[style]
  }

  const getPadding = () => {
    const paddings = {
      'minimal': 'py-12',
      'standard': 'py-16',
      'impact': 'py-20',
      'urgent': 'py-16'
    }
    return paddings[variant]
  }

  const getUrgencyColor = () => {
    const colors = {
      'none': '',
      'low': 'text-yellow-400',
      'medium': 'text-orange-400',
      'high': 'text-red-400'
    }
    return colors[urgency_level]
  }

  const isDark = background !== 'light'
  const textColor = isDark ? 'text-white' : 'text-dark-900'
  const subtitleColor = isDark ? 'text-white/90' : 'text-neutral-600'
  
  const primaryBtnClass = isDark 
    ? 'bg-white text-dark-900 hover:bg-neutral-100 hover:shadow-xl'
    : 'bg-brand-500 text-white hover:bg-brand-600 hover:shadow-brand'
    
  const secondaryBtnClass = isDark
    ? 'border-white text-white hover:bg-white hover:text-dark-900'
    : 'border-brand-500 text-brand-500 hover:bg-brand-500 hover:text-white'

  return (
    <section className={`${getPadding()} ${getBackgroundClass()} relative overflow-hidden`}>
      
      {/* 🌟 BACKGROUND EFFECTS */}
      {(isImpact || isUrgent) && (
        <>
          <div className="absolute inset-0 bg-gradient-radial from-transparent via-black/10 to-black/20" />
          <div className="absolute top-10 left-10 w-40 h-40 bg-white/5 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-10 right-10 w-32 h-32 bg-white/5 rounded-full blur-2xl animate-float" style={{ animationDelay: '1s' }} />
        </>
      )}

      {/* ⚡ URGENCY PULSE pour variant urgent */}
      {isUrgent && (
        <div className="absolute inset-0 bg-red-500/10 animate-pulse" />
      )}

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {layout === 'split' ? (
          // 🔄 SPLIT LAYOUT
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="text-left">
              <CtaContent />
            </div>
            <div className="lg:justify-self-end">
              <CtaActions />
            </div>
          </div>
        ) : layout === 'banner' ? (
          // 📏 BANNER LAYOUT
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
            <div className="flex-1">
              <CtaContent />
            </div>
            <div className="flex-shrink-0">
              <CtaActions />
            </div>
          </div>
        ) : (
          // 📍 CENTERED LAYOUT
          <div className={`text-center max-w-4xl mx-auto ${getContainerStyle()} ${style !== 'solid' ? 'p-12 rounded-3xl' : ''}`}>
            <CtaContent />
            <CtaActions />
          </div>
        )}
      </div>
    </section>
  )

  function CtaContent() {
    return (
      <div className={layout !== 'centered' ? 'mb-8 lg:mb-0' : 'mb-10'}>
        
        {/* 🏷️ BADGE */}
        {badge_text && (
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-white/10 text-white text-sm font-medium mb-6">
            <span className="w-2 h-2 bg-brand-400 rounded-full mr-3 animate-pulse"></span>
            {badge_text}
          </div>
        )}

        {/* ⏰ COUNTDOWN pour urgency */}
        {show_countdown && countdown_text && hasUrgency && (
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/20 text-red-300 text-sm font-medium mb-4 ${
            urgency_level === 'high' ? 'animate-pulse' : ''
          }`}>
            <span className="text-red-400">⏰</span>
            {countdown_text}
          </div>
        )}

        {/* 📝 TITRE */}
        <h2 className={`font-bold ${textColor} mb-6 ${
          isImpact ? 'text-4xl md:text-5xl lg:text-6xl' :
          isUrgent ? 'text-3xl md:text-4xl lg:text-5xl' :
          variant === 'standard' ? 'text-3xl md:text-4xl' :
          'text-2xl md:text-3xl'
        }`}>
          {isUrgent || hasUrgency ? (
            <span className={`${getUrgencyColor()} font-extrabold`}>
              {title}
            </span>
          ) : isImpact ? (
            <span className="bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
              {title}
            </span>
          ) : (
            title
          )}
        </h2>

        {/* 📄 SOUS-TITRE */}
        {subtitle && (
          <p className={`text-xl md:text-2xl ${subtitleColor} mb-4 ${
            layout === 'centered' ? 'max-w-3xl mx-auto' : ''
          }`}>
            {subtitle}
          </p>
        )}

        {/* 📝 DESCRIPTION */}
        {description && (
          <p className={`text-lg ${subtitleColor} leading-relaxed ${
            layout === 'centered' ? 'max-w-2xl mx-auto' : ''
          }`}>
            {description}
          </p>
        )}

        {/* 📊 STATS rapides */}
        {stats && stats.length > 0 && (
          <div className={`mt-8 grid grid-cols-2 gap-6 ${layout === 'centered' ? 'max-w-md mx-auto' : ''}`}>
            {stats.map((stat, index) => (
              <div key={index} className={layout === 'centered' ? 'text-center' : 'text-left'}>
                <div className={`text-2xl md:text-3xl font-bold ${textColor}`}>
                  {stat.number}
                </div>
                <div className={`text-sm ${subtitleColor} uppercase tracking-wide`}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  function CtaActions() {
    return (
      <div className="space-y-6">
        
        {/* 🎯 BOUTONS */}
        <div className={`flex flex-col sm:flex-row gap-4 ${
          layout === 'centered' ? 'justify-center' : 'justify-start'
        }`}>
          
          {/* Bouton principal */}
          <Link
            href={primary_cta_url}
            className={`group inline-flex items-center justify-center px-8 py-4 text-lg font-bold rounded-2xl transition-all duration-300 transform hover:scale-105 ${primaryBtnClass} ${
              isUrgent ? 'animate-pulse-brand shadow-glow' : ''
            }`}
          >
            {primary_cta_text}
            <svg className="ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>

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

        {/* 🛡️ GARANTIE */}
        {show_guarantee && guarantee_text && (
          <div className={`flex items-center gap-3 ${layout === 'centered' ? 'justify-center' : 'justify-start'}`}>
            <span className="text-green-400 text-xl">🛡️</span>
            <span className={`text-sm ${subtitleColor}`}>
              {guarantee_text}
            </span>
          </div>
        )}

        {/* 👥 SOCIAL PROOF */}
        {show_social_proof && social_proof && (
          <div className={`flex items-center gap-3 ${layout === 'centered' ? 'justify-center' : 'justify-start'}`}>
            <span className="text-yellow-400 text-xl">⭐</span>
            <span className={`text-sm ${subtitleColor}`}>
              {social_proof}
            </span>
          </div>
        )}
      </div>
    )
  }
}