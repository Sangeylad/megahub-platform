// components/sections/index.ts - MISE À JOUR COMPLÈTE
// Layout containers
export { LayoutRenderer } from './LayoutRenderer'

// Core sections
export { SectionRenderer } from './SectionRenderer'

// Content sections
export { HeroSection } from './HeroSection'
export { CtaSection } from './CtaSection'
export { ContactFormSection } from './ContactFormSection'
export { ServicesGrid } from './ServicesGrid'
export { StatsSection } from './StatsSection'
export { TestimonialCarousel } from './TestimonialCarousel'
export { GlossaryTermSection } from './GlossaryTermSection'
export { ToolsListingSection } from './ToolsListingSection' // 🆕 AJOUTÉ

// Simple sections
export { FeaturesSection } from './FeaturesSection'
export { RichTextSection } from './RichTextSection'
export { CalorieCalculatorSection } from './CalorieCalculatorSection'

// Types
export type {
  HeroBannerProps,
  CtaBannerProps,
  ContactFormProps,
  ServicesGridProps,
  StatsSectionProps,
  CalorieCalculatorSectionProps,
  TestimonialCarouselProps,
  FeaturesGridProps,
  RichTextProps,
  SectionProps,
  SectionComponentProps,
  LayoutConfig,
  FormField,
  Feature,
  Stat,
  Testimonial,
  GlossaryTermSectionProps,
  ToolsListingSectionProps // 🆕 AJOUTÉ
} from '@/lib/types/sections'