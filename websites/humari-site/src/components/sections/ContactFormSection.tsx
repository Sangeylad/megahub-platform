// /var/www/megahub/websites/humari-site/src/components/sections/ContactFormSection.tsx
'use client'
import { useState } from 'react'
import type { SectionComponentProps } from '@/lib/types/sections'

interface ContactFormSectionProps {
  // Contenu
  title?: string
  subtitle?: string
  description?: string
  success_message?: string
  
  // 🎯 FORM CONFIG
  fields: Array<{
    name: string
    label: string
    type: 'text' | 'email' | 'tel' | 'textarea' | 'select' | 'checkbox' | 'radio'
    placeholder?: string
    required?: boolean
    options?: string[] // pour select/radio
    rows?: number // pour textarea
    validation?: string
  }>
  
  // 🎨 VARIANTS & STYLE
  variant: 'minimal' | 'standard' | 'impact' | 'embedded'
  layout: 'centered' | 'split' | 'inline' | 'modal'
  style: 'modern' | 'classic' | 'floating' | 'outlined'
  background: 'transparent' | 'light' | 'dark' | 'brand'
  submit_text: string
  show_privacy: boolean
  privacy_text?: string
}

interface FormData {
  [key: string]: string | boolean
}

export function ContactFormSection({ data }: SectionComponentProps<ContactFormSectionProps>) {
  const {
    title,
    subtitle,
    description,
    success_message = "Merci ! Nous vous recontacterons rapidement.",
    fields,
    variant = 'standard',
    layout = 'centered',
    style = 'modern',
    background = 'transparent',
    submit_text = "Envoyer",
    show_privacy = true,
    privacy_text = "En soumettant ce formulaire, vous acceptez notre politique de confidentialité."
  } = data

  // 🎮 FORM STATE
  const [formData, setFormData] = useState<FormData>({})
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  // 🧠 LOGIQUE VARIANTS

  const isEmbedded = variant === 'embedded'
  const isSplit = layout === 'split'
  const showHeader = title || subtitle || description

  // 🎨 CLASSES DYNAMIQUES
  const getBackgroundClass = () => {
    const backgrounds = {
      'transparent': 'bg-transparent',
      'light': 'bg-neutral-50',
      'dark': 'bg-dark-900',
      'brand': 'bg-gradient-to-br from-brand-50 to-white'
    }
    return backgrounds[background]
  }

  const getPadding = () => {
    if (isEmbedded) return 'py-0'
    const paddings = {
      'minimal': 'py-12',
      'standard': 'py-16',
      'impact': 'py-20',
      'embedded': 'py-0'
    }
    return paddings[variant]
  }

  const getFormStyle = () => {
    const isDark = background === 'dark'
    
    const styles = {
      'modern': `p-8 rounded-3xl ${isDark ? 'bg-dark-800' : 'bg-white'} shadow-xl`,
      'classic': `p-6 rounded-lg ${isDark ? 'bg-dark-800 border border-dark-700' : 'bg-white border border-neutral-200'}`,
      'floating': `p-8 rounded-2xl ${isDark ? 'bg-dark-800/80' : 'bg-white/80'} backdrop-blur-lg shadow-2xl border ${isDark ? 'border-white/10' : 'border-white/20'}`,
      'outlined': `p-6 rounded-xl border-2 ${isDark ? 'border-dark-600 bg-dark-900' : 'border-neutral-300 bg-transparent'}`
    }
    return styles[style]
  }

  const isDark = background === 'dark'
  const textColor = isDark ? 'text-white' : 'text-dark-900'
  const subtitleColor = isDark ? 'text-neutral-300' : 'text-neutral-600'

  // 🔧 FORM HANDLERS
  const handleInputChange = (name: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    fields.forEach(field => {
      const value = formData[field.name]
      
      if (field.required && (!value || value === '')) {
        newErrors[field.name] = `${field.label} est requis`
      }
      
      if (field.type === 'email' && value && typeof value === 'string') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(value)) {
          newErrors[field.name] = 'Email invalide'
        }
      }
    })
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setIsSubmitting(true)
    
    try {
      // Simulation API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      setIsSubmitted(true)
    } catch (error) {
      console.error('Erreur envoi formulaire:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <section className={`${getPadding()} ${getBackgroundClass()}`}>
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className={getFormStyle()}>
            <div className="text-6xl mb-6">✅</div>
            <h3 className={`text-2xl font-bold ${textColor} mb-4`}>Message envoyé !</h3>
            <p className={subtitleColor}>{success_message}</p>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className={`${getPadding()} ${getBackgroundClass()} relative overflow-hidden`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {isSplit ? (
          // 🔄 SPLIT LAYOUT
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Contenu */}
            <div>
              <FormHeader />
            </div>
            
            {/* Formulaire */}
            <div>
              <FormContent />
            </div>
          </div>
        ) : (
          // 📍 CENTERED LAYOUT
          <div className="max-w-2xl mx-auto">
            {showHeader && <FormHeader />}
            <FormContent />
          </div>
        )}
      </div>
    </section>
  )

  function FormHeader() {
    return (
      <div className={`${isSplit ? 'text-left' : 'text-center'} ${showHeader ? 'mb-12' : ''}`}>
        {title && (
          <h2 className={`text-3xl md:text-4xl font-bold ${textColor} mb-6`}>
            {title}
          </h2>
        )}
        {subtitle && (
          <p className={`text-xl ${subtitleColor} mb-4`}>
            {subtitle}
          </p>
        )}
        {description && (
          <p className={`${subtitleColor} leading-relaxed`}>
            {description}
          </p>
        )}
      </div>
    )
  }

  function FormContent() {
    return (
      <form onSubmit={handleSubmit} className={isEmbedded ? '' : getFormStyle()}>
        <div className="space-y-6">
          {fields.map((field) => (
  <FormField 
    key={field.name} 
    field={field} 
    value={formData[field.name] || ''} 
    {...(errors[field.name] && { error: errors[field.name] })}  // ✅ Passer la prop seulement si elle existe
    onChange={handleInputChange}
    isDark={isDark}
  />
          ))}
        </div>

        {/* 📋 PRIVACY */}
        {show_privacy && privacy_text && (
          <div className="mt-6">
            <label className="flex items-start gap-3 cursor-pointer">
              <input 
                type="checkbox"
                required
                className="mt-1 w-4 h-4 text-brand-500 border-neutral-300 rounded focus:ring-brand-500"
              />
              <span className={`text-sm ${isDark ? 'text-neutral-400' : 'text-neutral-600'}`}>
                {privacy_text}
              </span>
            </label>
          </div>
        )}

        {/* 🎯 SUBMIT */}
        <div className="mt-8">
          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-4 px-8 text-lg font-semibold rounded-2xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
              isDark 
                ? 'bg-brand-500 text-white hover:bg-brand-600' 
                : 'bg-dark-900 text-white hover:bg-dark-800'
            }`}
          >
            {isSubmitting ? (
              <span className="flex items-center justify-center gap-3">
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Envoi en cours...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                {submit_text}
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </span>
            )}
          </button>
        </div>
      </form>
    )
  }
}

// 🧩 COMPOSANT CHAMP
function FormField({
  field,
  value,
  error,
  onChange,
  isDark
}: {
  field: ContactFormSectionProps['fields'][0]
  value: string | boolean
  error?: string  // ✅ Rendre optionnel
  onChange: (name: string, value: string | boolean) => void
  isDark: boolean
}) {

  const baseInputClass = `w-full px-4 py-3 rounded-xl border transition-all duration-200 ${
    isDark 
      ? 'bg-dark-700 border-dark-600 text-white placeholder-neutral-400 focus:border-brand-400' 
      : 'bg-white border-neutral-300 text-dark-900 placeholder-neutral-500 focus:border-brand-500'
  } focus:ring-2 focus:ring-brand-500/20 focus:outline-none`

  const labelClass = `block text-sm font-medium mb-2 ${isDark ? 'text-neutral-200' : 'text-neutral-700'}`
  const errorClass = `mt-1 text-sm text-red-500`

  const renderInput = () => {
    switch (field.type) {
      case 'textarea':
        return (
          <textarea
            name={field.name}
            value={value as string}
            onChange={(e) => onChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            rows={field.rows || 4}
            required={field.required}
            className={baseInputClass}
          />
        )
      
      case 'select':
        return (
          <select
            name={field.name}
            value={value as string}
            onChange={(e) => onChange(field.name, e.target.value)}
            required={field.required}
            className={baseInputClass}
          >
            <option value="">{field.placeholder || `Choisir ${field.label}`}</option>
            {field.options?.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        )
      
      case 'checkbox':
        return (
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              name={field.name}
              checked={value as boolean}
              onChange={(e) => onChange(field.name, e.target.checked)}
              required={field.required}
              className="w-4 h-4 text-brand-500 border-neutral-300 rounded focus:ring-brand-500"
            />
            <span className={isDark ? 'text-neutral-200' : 'text-neutral-700'}>
              {field.label}
            </span>
          </label>
        )
      
      default:
        return (
          <input
            type={field.type}
            name={field.name}
            value={value as string}
            onChange={(e) => onChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
            className={baseInputClass}
          />
        )
    }
  }

  return (
    <div>
      {field.type !== 'checkbox' && (
        <label htmlFor={field.name} className={labelClass}>
          {field.label} {field.required && <span className="text-red-500">*</span>}
        </label>
      )}
      
      {renderInput()}
      
      {error && <p className={errorClass}>{error}</p>}
    </div>
  )
}