'use client'
import { useState, useEffect } from 'react'
import Image from 'next/image'
import type { SectionComponentProps } from '@/lib/types/sections'

interface TestimonialCarouselProps {
  // Contenu
  title?: string
  subtitle?: string
  testimonials: Array<{
    content: string
    author: string
    position: string
    company: string
    avatar?: string
    rating?: number
    project?: string
    result?: string
  }>
  
  // 🎯 VARIANTS & BEHAVIOR
  variant: 'minimal' | 'standard' | 'impact' | 'featured'
  layout: 'carousel' | 'grid' | 'masonry' | 'single'
  style: 'cards' | 'quotes' | 'bubbles' | 'testimonial-wall'
  background: 'transparent' | 'light' | 'dark' | 'brand'
  autoplay: boolean
  autoplay_delay: number
  show_navigation: boolean
  show_dots: boolean
  show_ratings: boolean
}

export function TestimonialCarousel({ data }: SectionComponentProps<TestimonialCarouselProps>) {
  const {
    title,
    subtitle,
    testimonials,
    variant = 'standard',
    layout = 'carousel',
    style = 'cards',
    background = 'transparent',
    autoplay = true,
    autoplay_delay = 5000,
    show_navigation = true,
    show_dots = true,
    show_ratings = true
  } = data

  // 🎮 STATE CAROUSEL
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(autoplay)

  // 🧠 LOGIQUE VARIANTS
  const isFeatured = variant === 'featured'
  const isCarousel = layout === 'carousel'
  const showHeader = title || subtitle

  // Auto-corrections
  const finalShowNav = show_navigation && isCarousel && testimonials.length > 1
  const finalShowDots = show_dots && isCarousel && testimonials.length > 1
  const finalShowRatings = show_ratings && testimonials.some(t => t.rating)

  // 🔄 AUTOPLAY LOGIC
  useEffect(() => {
    if (!isPlaying || !isCarousel || testimonials.length <= 1) return

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length)
    }, autoplay_delay)

    return () => clearInterval(interval)
  }, [isPlaying, isCarousel, testimonials.length, autoplay_delay])

  // 🎨 CLASSES DYNAMIQUES
  const getBackgroundClass = () => {
    const backgrounds = {
      'transparent': 'bg-transparent',
      'light': 'bg-neutral-50',
      'dark': 'bg-dark-900',
      'brand': 'bg-gradient-to-br from-brand-50 via-white to-neutral-50'
    }
    return backgrounds[background]
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

  const getGridClass = () => {
    if (layout === 'single') return 'max-w-4xl mx-auto'
    if (layout === 'masonry') return 'columns-1 md:columns-2 lg:columns-3 gap-8 space-y-8'
    
    const grids = {
      2: 'grid-cols-1 lg:grid-cols-2',
      3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
      4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
    }
    
    const cols = testimonials.length >= 3 ? 3 : testimonials.length
    return `grid gap-8 ${grids[cols as keyof typeof grids]}`
  }

  const isDark = background === 'dark'
  const textColor = isDark ? 'text-white' : 'text-dark-900'
  const subtitleColor = isDark ? 'text-neutral-300' : 'text-neutral-600'

  // 🎮 CONTROLS
  const goToPrev = () => {
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length)
  }

  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length)
  }

  const goToSlide = (index: number) => {
    setCurrentIndex(index)
  }

  return (
    <section className={`${getPadding()} ${getBackgroundClass()} relative overflow-hidden`}>
      {/* 🌟 BACKGROUND EFFECTS */}
      {isFeatured && (
        <>
          <div className="absolute inset-0 bg-gradient-radial from-brand-500/5 via-transparent to-transparent" />
          <div className="absolute top-20 left-10 w-32 h-32 bg-brand-500/5 rounded-full blur-2xl" />
          <div className="absolute bottom-20 right-10 w-40 h-40 bg-neutral-500/5 rounded-full blur-3xl" />
        </>
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

        {/* 🗣️ TESTIMONIALS CONTENT */}
        {isCarousel ? (
          <div className="relative">
            {/* Carousel Container */}
            <div className="overflow-hidden rounded-3xl">
              <div 
                className="flex transition-transform duration-500 ease-in-out"
                style={{ transform: `translateX(-${currentIndex * 100}%)` }}
              >
                {testimonials.map((testimonial, index) => (
                  <div key={index} className="w-full flex-shrink-0 px-4">
                    <TestimonialCard
                      testimonial={testimonial}
                      variant={variant}
                      style={style}
                      background={background}
                      showRatings={finalShowRatings}
                      isCarousel={true}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Navigation Arrows */}
            {finalShowNav && (
              <div className="absolute inset-y-0 left-0 right-0 flex items-center justify-between pointer-events-none">
                <button
                  onClick={goToPrev}
                  onMouseEnter={() => setIsPlaying(false)}
                  onMouseLeave={() => setIsPlaying(autoplay)}
                  className={`pointer-events-auto -ml-4 p-3 rounded-full transition-all duration-200 ${
                    isDark ? 'bg-dark-800 text-white hover:bg-dark-700' : 'bg-white text-dark-900 hover:bg-neutral-100'
                  } shadow-lg hover:shadow-xl transform hover:scale-105`}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <button
                  onClick={goToNext}
                  onMouseEnter={() => setIsPlaying(false)}
                  onMouseLeave={() => setIsPlaying(autoplay)}
                  className={`pointer-events-auto -mr-4 p-3 rounded-full transition-all duration-200 ${
                    isDark ? 'bg-dark-800 text-white hover:bg-dark-700' : 'bg-white text-dark-900 hover:bg-neutral-100'
                  } shadow-lg hover:shadow-xl transform hover:scale-105`}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            )}

            {/* Dots Navigation */}
            {finalShowDots && (
              <div className="flex justify-center gap-3 mt-8">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => goToSlide(index)}
                    className={`w-3 h-3 rounded-full transition-all duration-200 ${
                      index === currentIndex 
                        ? 'bg-brand-500 scale-125' 
                        : isDark ? 'bg-neutral-600 hover:bg-neutral-500' : 'bg-neutral-300 hover:bg-neutral-400'
                    }`}
                  />
                ))}
              </div>
            )}
          </div>
        ) : (
          // Grid/Masonry Layout
          <div className={getGridClass()}>
            {testimonials.map((testimonial, index) => (
              <TestimonialCard
                key={`${testimonial.author}-${index}`}
                testimonial={testimonial}
                variant={variant}
                style={style}
                background={background}
                showRatings={finalShowRatings}
                isCarousel={false}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

// 🧩 COMPOSANT TESTIMONIAL CARD
function TestimonialCard({
  testimonial,
  variant,
  style,
  background,
  showRatings,
  isCarousel
}: {
  testimonial: TestimonialCarouselProps['testimonials'][0]
  variant: TestimonialCarouselProps['variant']
  style: TestimonialCarouselProps['style']
  background: TestimonialCarouselProps['background']
  showRatings: boolean
  isCarousel: boolean
}) {

  const isDark = background === 'dark'
  const isFeatured = variant === 'featured'

  // 🎨 STYLES DE CARTE
  const getCardClass = () => {
    const base = 'relative transition-all duration-300'
    
    const styles = {
      'cards': `${base} p-8 rounded-2xl ${isDark ? 'bg-dark-800' : 'bg-white'} shadow-lg hover:shadow-xl ${isCarousel ? '' : 'transform hover:-translate-y-1'}`,
      'quotes': `${base} p-8 ${isDark ? 'text-white' : 'text-dark-900'}`,
      'bubbles': `${base} p-6 rounded-3xl ${isDark ? 'bg-dark-800/50' : 'bg-neutral-100'} backdrop-blur-sm`,
      'testimonial-wall': `${base} p-6 rounded-xl border ${isDark ? 'border-dark-700 bg-dark-800/30' : 'border-neutral-200 bg-white/50'} backdrop-blur-sm`
    }
    
    return styles[style]
  }

  const textColor = isDark ? 'text-white' : 'text-dark-900'
  const contentColor = isDark ? 'text-neutral-200' : 'text-neutral-700'
  const metaColor = isDark ? 'text-neutral-400' : 'text-neutral-500'

  return (
    <div className={getCardClass()}>
      {/* 🔥 QUOTE ICON pour style quotes */}
      {style === 'quotes' && (
        <div className={`absolute -top-4 left-8 text-6xl ${isDark ? 'text-brand-400/20' : 'text-brand-500/20'}`}>
          &ldquo;
        </div>
      )}

      {/* ⭐ RATING */}
      {showRatings && testimonial.rating && (
        <div className="flex items-center gap-1 mb-4">
          {[...Array(5)].map((_, i) => (
            <svg
              key={i}
              className={`w-5 h-5 ${i < testimonial.rating! ? 'text-yellow-400' : 'text-neutral-300'}`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          ))}
        </div>
      )}

      {/* 💬 CONTENU */}
      <blockquote className={`${contentColor} leading-relaxed mb-6 ${
        isFeatured ? 'text-lg md:text-xl' : 'text-base'
      } ${style === 'quotes' ? 'relative z-10' : ''}`}>
        {style === 'quotes' ? `"${testimonial.content}"` : testimonial.content}
      </blockquote>

      {/* 👤 AUTEUR */}
      <div className="flex items-center gap-4">
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isFeatured ? 'w-16 h-16' : 'w-12 h-12'} rounded-full overflow-hidden ${
          !testimonial.avatar ? (isDark ? 'bg-dark-700' : 'bg-neutral-200') : ''
        }`}>
          {testimonial.avatar ? (
            <Image 
              src={testimonial.avatar} 
              alt={testimonial.author}
              width={isFeatured ? 64 : 48}
              height={isFeatured ? 64 : 48}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <span className={`${isDark ? 'text-neutral-500' : 'text-neutral-400'} text-xl font-bold`}>
                {testimonial.author.charAt(0)}
              </span>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className={`font-semibold ${textColor} ${isFeatured ? 'text-lg' : 'text-base'}`}>
            {testimonial.author}
          </div>
          <div className={`${metaColor} text-sm leading-tight`}>
            {testimonial.position}
            {testimonial.company && (
              <>
                <br />
                <span className="font-medium">{testimonial.company}</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 📊 PROJET/RÉSULTAT */}
      {(testimonial.project || testimonial.result) && (
        <div className={`mt-4 pt-4 border-t ${isDark ? 'border-dark-700' : 'border-neutral-200'}`}>
          {testimonial.project && (
            <div className={`text-sm ${metaColor} mb-1`}>
              <span className="font-medium">Projet:</span> {testimonial.project}
            </div>
          )}
          {testimonial.result && (
            <div className={`text-sm font-medium ${isDark ? 'text-brand-400' : 'text-brand-600'}`}>
              <span className="font-normal text-current opacity-70">Résultat:</span> {testimonial.result}
            </div>
          )}
        </div>
      )}

      {/* ✨ EFFET FEATURED */}
      {isFeatured && style === 'cards' && (
        <div className="absolute inset-0 bg-gradient-to-r from-brand-500/5 to-transparent rounded-2xl pointer-events-none" />
      )}
    </div>
  )
}