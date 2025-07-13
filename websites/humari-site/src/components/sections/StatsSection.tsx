// /var/www/megahub/websites/humari-site/src/components/sections/StatsSection.tsx
import type { SectionComponentProps } from '@/lib/types/sections'

interface StatsSectionProps {
  // Contenu
  title?: string
  subtitle?: string
  stats: Array<{
    number: string
    label: string
    description?: string
    icon?: string
  }>
  
  // 🎯 VARIANTS & STYLE
  variant: 'minimal' | 'standard' | 'impact' | 'featured'
  layout: 'grid' | 'inline' | 'cards'
  background: 'transparent' | 'light' | 'dark' | 'brand'
  animation: 'none' | 'counter' | 'reveal'
}

export function StatsSection({ data }: SectionComponentProps<StatsSectionProps>) {
  const {
    title,
    subtitle,
    stats,
    variant = 'standard',
    layout = 'grid',
    background = 'transparent',
    animation = 'reveal'
  } = data

  // 🧠 LOGIQUE VARIANTS
  const isMinimal = variant === 'minimal'
  const isFeatured = variant === 'featured'
  const showHeader = title || subtitle
  
  // Auto-corrections
  const finalLayout = stats.length <= 2 ? 'inline' : layout
  const showAnimation = animation !== 'none' && !isMinimal

  // 🎨 CLASSES DYNAMIQUES
  const getBackgroundClass = () => {
    const backgrounds = {
      'transparent': 'bg-transparent',
      'light': 'bg-neutral-50',
      'dark': 'bg-dark-900',
      'brand': 'bg-gradient-to-r from-brand-500/10 to-brand-600/5'
    }
    return backgrounds[background]
  }

  const getLayoutClass = () => {
    const layouts = {
      'grid': `grid gap-8 ${stats.length === 2 ? 'grid-cols-1 md:grid-cols-2' : 
                        stats.length === 3 ? 'grid-cols-1 md:grid-cols-3' :
                        'grid-cols-2 md:grid-cols-4'}`,
      'inline': 'flex flex-wrap justify-center gap-12',
      'cards': `grid gap-6 ${stats.length <= 2 ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`
    }
    return layouts[finalLayout]
  }

  const getPadding = () => {
    const paddings = {
      'minimal': 'py-8',
      'standard': 'py-12',
      'impact': 'py-16', 
      'featured': 'py-20'
    }
    return paddings[variant]
  }

  const isDark = background === 'dark'
  const textColor = isDark ? 'text-white' : 'text-dark-900'
  const subtitleColor = isDark ? 'text-neutral-300' : 'text-neutral-600'

  return (
    <section className={`${getPadding()} ${getBackgroundClass()} relative overflow-hidden`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* 🎨 HEADER */}
        {showHeader && (
          <div className={`text-center mb-12 ${isFeatured ? 'mb-16' : ''}`}>
            {title && (
              <h2 className={`text-3xl md:text-4xl font-bold ${textColor} mb-4`}>
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
              <p className={`text-lg md:text-xl ${subtitleColor} max-w-3xl mx-auto`}>
                {subtitle}
              </p>
            )}
          </div>
        )}

        {/* 📊 STATS GRID */}
        <div className={getLayoutClass()}>
          {stats.map((stat, index) => (
            <StatItem 
              key={index} 
              stat={stat} 
              index={index}
              variant={variant}
              layout={finalLayout}
              background={background}
              animation={showAnimation}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

// 🧩 COMPOSANT STAT INDIVIDUEL
function StatItem({ 
  stat, 
  index, 
  variant, 
  layout, 
  background, 
  animation 
}: {
  stat: StatsSectionProps['stats'][0]
  index: number
  variant: StatsSectionProps['variant']
  layout: string
  background: StatsSectionProps['background']
  animation: boolean
}) {
  
  const isCard = layout === 'cards'
  const isDark = background === 'dark'
  const isFeatured = variant === 'featured'
  
  const baseClasses = isCard 
    ? `p-6 rounded-2xl border transition-all duration-300 ${
        isDark ? 'bg-dark-800 border-dark-700 hover:bg-dark-700' : 
        'bg-white border-neutral-200 hover:border-neutral-300 hover:shadow-lg'
      }`
    : 'text-center'

  const numberColor = isDark ? 'text-white' : 
                     isFeatured ? 'text-brand-500' : 'text-dark-900'
  const labelColor = isDark ? 'text-neutral-300' : 'text-neutral-600'
  const descColor = isDark ? 'text-neutral-400' : 'text-neutral-500'

  const animationDelay = animation ? { animationDelay: `${index * 150}ms` } : {}

  return (
    <div 
      className={`${baseClasses} ${animation ? 'animate-fadeIn' : ''}`}
      style={animationDelay}
    >
      {/* 🎨 ICÔNE */}
      {stat.icon && (
        <div className={`${isCard ? 'mb-4' : 'mb-3'} ${layout === 'inline' ? 'mb-2' : ''}`}>
          <span className="text-4xl">{stat.icon}</span>
        </div>
      )}

      {/* 🔢 NOMBRE */}
      <div className={`font-bold ${numberColor} mb-2 ${
        variant === 'featured' ? 'text-5xl md:text-6xl' :
        variant === 'impact' ? 'text-4xl md:text-5xl' :
        variant === 'standard' ? 'text-3xl md:text-4xl' :
        'text-2xl md:text-3xl'
      }`}>
        {animation ? (
          <CounterAnimation target={stat.number} />
        ) : (
          stat.number
        )}
      </div>

      {/* 🏷️ LABEL */}
      <div className={`font-semibold ${labelColor} mb-1 ${
        variant === 'featured' ? 'text-lg' : 
        variant === 'minimal' ? 'text-sm' : 'text-base'
      } uppercase tracking-wide`}>
        {stat.label}
      </div>

      {/* 📝 DESCRIPTION */}
      {stat.description && (
        <p className={`${descColor} text-sm leading-relaxed`}>
          {stat.description}
        </p>
      )}

      {/* ✨ EFFECT pour featured */}
      {isFeatured && (
        <div className="absolute inset-0 bg-gradient-to-r from-brand-500/5 to-transparent rounded-2xl"></div>
      )}
    </div>
  )
}

// 🎯 ANIMATION COMPTEUR
function CounterAnimation({ target }: { target: string }) {
  // ✅ Option 1: Supprimer les variables non utilisées
  return (
    <span className="inline-block tabular-nums">
      <span className="animate-pulse-brand">{target}</span>
    </span>
  )
}