// components/sections/SectionRenderer.tsx - COMPLET AVEC TOOLS
import React from 'react'
import type { 
  SectionProps, 
  HeroBannerProps, 
  CtaBannerProps, 
  FeaturesGridProps, 
  RichTextProps, 
  ContactFormProps,
  HeaderProps,
  GlossarySearchSectionProps,
  GlossaryTermSectionProps,
  ToolsListingSectionProps  // 🆕 AJOUTÉ
} from '@/lib/types/sections'

// 🔧 Import normal (pas type) pour les helpers de validation
import { 
  isCalorieCalculatorSectionProps,
  isBeroasCalculatorProps
} from '@/lib/types/sections'

import { HeroSection } from './HeroSection'
import { CtaSection } from './CtaSection'
import { FeaturesSection } from './FeaturesSection'
import { RichTextSection } from './RichTextSection'
import { ContactFormSection } from './ContactFormSection'
import { BeroasCalculatorSection } from './BeroasCalculatorSection'
import { CalorieCalculatorSection } from './CalorieCalculatorSection'
import { GlossarySearchSection } from './GlossarySearchSection'
import { GlossaryTermSection } from './GlossaryTermSection'
import { ToolsListingSection } from './ToolsListingSection'  // 🆕 AJOUTÉ
import { HeaderRenderer } from '@/components/layout/headers/HeaderRenderer'
import { LayoutRenderer } from './LayoutRenderer'
import { SectionValidator } from '@/lib/sections-registry/validator'

// Type guards stricts
const isHeroBannerData = (data: unknown): data is HeroBannerProps => {
  return typeof data === 'object' && 
         data !== null && 
         typeof (data as HeroBannerProps).title === 'string'
}

const isCtaBannerData = (data: unknown): data is CtaBannerProps => {
  const typed = data as CtaBannerProps
  return typeof data === 'object' && 
         data !== null && 
         typeof typed.title === 'string' && 
         typeof typed.primary_cta_text === 'string' && 
         typeof typed.primary_cta_url === 'string'
}

const isFeaturesGridData = (data: unknown): data is FeaturesGridProps => {
  return typeof data === 'object' && 
         data !== null && 
         Array.isArray((data as FeaturesGridProps).features)
}

const isRichTextData = (data: unknown): data is RichTextProps => {
  return typeof data === 'object' && 
         data !== null && 
         typeof (data as RichTextProps).content === 'string'
}

const isContactFormData = (data: unknown): data is ContactFormProps => {
  return typeof data === 'object' && 
         data !== null && 
         Array.isArray((data as ContactFormProps).fields)
}

const isHeaderData = (data: unknown): data is HeaderProps => {
  return typeof data === 'object' && 
         data !== null && 
         ['default', 'none'].includes((data as HeaderProps).variant)
}

// Type guard pour Glossaire Search
const isGlossarySearchData = (data: unknown): data is GlossarySearchSectionProps => {
  return typeof data === 'object' && 
         data !== null && 
         ['full', 'embedded', 'minimal'].includes((data as GlossarySearchSectionProps).variant)
}

// Type guard pour Glossaire Term
const isGlossaryTermData = (data: unknown): data is GlossaryTermSectionProps => {
  const typed = data as GlossaryTermSectionProps
  return typeof data === 'object' && 
         data !== null && 
         // Slug optionnel (sera extrait de l'URL si non fourni)
         (typed.slug === undefined || typeof typed.slug === 'string') &&
         // Language optionnel avec défaut 'fr'
         (typed.language === undefined || typeof typed.language === 'string')
}

// 🆕 Type guard pour Tools Listing
const isToolsListingData = (data: unknown): data is ToolsListingSectionProps => {
  const typed = data as ToolsListingSectionProps
  
  // 🔧 CONVERSION SAFE : string → number pour grid_columns
  let gridCols: number | undefined
  if (typeof typed.grid_columns === 'string') {
    gridCols = parseInt(typed.grid_columns)
  } else if (typeof typed.grid_columns === 'number') {
    gridCols = typed.grid_columns
  }
  
  return typeof data === 'object' && 
         data !== null && 
         // Au moins un des deux paramètres requis
         (typeof typed.category_id === 'number' || typeof typed.category_path === 'string') &&
         // display_mode optionnel avec valeurs valides
         (typed.display_mode === undefined || ['grid', 'list', 'compact'].includes(typed.display_mode)) &&
         // grid_columns avec conversion string/number
         (gridCols === undefined || [2, 3, 4].includes(gridCols)) &&
         // card_style optionnel avec valeurs valides
         (typed.card_style === undefined || ['default', 'minimal', 'elevated'].includes(typed.card_style))
}

// Composant d'erreur réutilisable
function SectionError({ message, sectionType }: { message: string; sectionType: string }) {
  return (
    <div className="py-4 px-6 bg-red-50 border border-red-200 rounded-lg">
      <p className="text-red-800">
        ⚠️ Erreur section &quot;{sectionType}&quot;: {message}
      </p>
    </div>
  )
}

function SectionRendererCore({ section }: { section: SectionProps }): React.ReactNode {
  
  // Validation basée sur le registre
  const validation = SectionValidator.validateSectionData(section.type, section.data)
  
  if (!validation.isValid) {
    console.error(`Validation failed for section ${section.type}:`, validation.errors)
    return (
      <SectionError 
        message={validation.errors.join(', ')} 
        sectionType={section.type}
      />
    )
  }

  // Gestion des sections de contenu avec type guards
  switch (section.type) {
    case 'header': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isHeaderData
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données header invalides" sectionType={section.type} />
      }
      
      return <HeaderRenderer config={specificValidation.data} />
    }

    case 'hero_banner': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type, 
        validation.sanitizedData, 
        isHeroBannerData
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données hero banner invalides" sectionType={section.type} />
      }
      
      return <HeroSection data={specificValidation.data} />
    }
    
    case 'cta_banner': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isCtaBannerData
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données CTA banner invalides" sectionType={section.type} />
      }
      
      return <CtaSection data={specificValidation.data} />
    }

    case 'beroas_calculator': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isBeroasCalculatorProps
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données calculateur BEROAS invalides" sectionType={section.type} />
      }
      
      return <BeroasCalculatorSection data={specificValidation.data} />
    }

    case 'calorie_calculator': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isCalorieCalculatorSectionProps
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données calculateur de calories invalides" sectionType={section.type} />
      }
      
      return <CalorieCalculatorSection data={specificValidation.data} />
    }

    case 'glossary_search': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isGlossarySearchData
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données glossaire invalides" sectionType={section.type} />
      }
      
      return <GlossarySearchSection data={specificValidation.data} />
    }

    case 'glossary_term': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isGlossaryTermData
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données terme glossaire invalides" sectionType={section.type} />
      }
      
      return <GlossaryTermSection data={specificValidation.data} />
    }

    // 🆕 NOUVEAU CASE TOOLS LISTING
    case 'tools_listing': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isToolsListingData
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données liste d'outils invalides" sectionType={section.type} />
      }
      
      return <ToolsListingSection data={specificValidation.data} />
    }
    
    case 'features_grid': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isFeaturesGridData
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données features grid invalides" sectionType={section.type} />
      }
      
      return <FeaturesSection data={specificValidation.data} />
    }
    
    case 'rich_text': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isRichTextData
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données rich text invalides" sectionType={section.type} />
      }
      
      return <RichTextSection data={specificValidation.data} />
    }
    
    case 'contact_form': {
      const specificValidation = SectionValidator.validateSpecificType(
        section.type,
        validation.sanitizedData,
        isContactFormData
      )
      
      if (!specificValidation.isValid || !specificValidation.data) {
        return <SectionError message="Données formulaire invalides" sectionType={section.type} />
      }
      
      return <ContactFormSection data={specificValidation.data} />
    }
    
    default:
      return (
        <div className="py-8 px-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800">
            Section &quot;{section.type}&quot; en développement
          </p>
        </div>
      )
  }
}

export function SectionRenderer({ section }: { section: SectionProps }) {
  
  // Gestion des layouts
  if (section.type.startsWith('layout_')) {
    const layoutType = section.type.replace('layout_', '') as 'columns' | 'grid' | 'stack'
    return (
      <LayoutRenderer
        type={layoutType}
        config={section.layout_config || {}}
        sections={section.children || []}
        renderSection={(childSection) => <SectionRenderer section={childSection} />}
      />
    )
  }

  return <>{SectionRendererCore({ section })}</>
}