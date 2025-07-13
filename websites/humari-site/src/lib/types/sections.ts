// /var/www/megahub/websites/humari-site/src/lib/types/sections.ts

import type { TabType } from '@/components/tools/calories-calculator/types'

// Types de base pour les champs de formulaire
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'tel' | 'textarea' | 'select' | 'checkbox' | 'radio'
  placeholder?: string
  required?: boolean
  options?: string[]
  rows?: number
  validation?: string
}

export interface Feature {
  title: string
  description: string
  icon?: string
  image?: string
  cta_text?: string
  cta_url?: string
  badge?: string
  features?: string[]
}

export interface Stat {
  number: string
  label: string
  description?: string
  icon?: string
}

export interface Testimonial {
  content: string
  author: string
  position: string
  company: string
  avatar?: string
  rating?: number
  project?: string
  result?: string
}

// Interface pour les menus de navigation
export interface MenuItem {
  label: string
  href: string
  children?: MenuItem[]
}

// Props des composants (alignés avec les vrais composants)
export interface HeroBannerProps {
  title: string
  subtitle?: string
  cta_text?: string
  cta_url?: string
  secondary_cta_text?: string
  secondary_cta_url?: string
  variant: 'minimal' | 'standard' | 'impact' | 'hero'
  layout: 'centered' | 'split'
  background: 'gradient-brand' | 'gradient-dark' | 'solid-light' | 'solid-dark'
  show_badge?: boolean
  badge_text?: string
  show_stats?: boolean
  stats?: Stat[]
}

export interface HeaderProps {
  variant: 'default' | 'none'
  logo_url?: string
  logo_alt?: string
  navigation?: MenuItem[]
  cta_text?: string
  cta_url?: string
  show_contact_info?: boolean
  contact_phone?: string
  contact_email?: string
}

export interface CtaBannerProps {
  title: string
  subtitle?: string
  description?: string
  primary_cta_text: string
  primary_cta_url: string
  secondary_cta_text?: string
  secondary_cta_url?: string
  variant: 'minimal' | 'standard' | 'impact' | 'urgent'
  layout: 'centered' | 'split' | 'banner' | 'floating'
  style: 'solid' | 'gradient' | 'outlined' | 'glass'
  background: 'brand' | 'dark' | 'light' | 'gradient' | 'image'
  urgency_level: 'none' | 'low' | 'medium' | 'high'
  show_guarantee?: boolean
  guarantee_text?: string
  show_social_proof?: boolean
  social_proof?: string
  show_countdown?: boolean
  countdown_text?: string
  badge_text?: string
  stats?: Stat[]
}

export interface FeaturesGridProps {
  title?: string
  subtitle?: string
  features: Feature[]
  variant: 'minimal' | 'standard' | 'impact' | 'featured'
  layout: 'grid' | 'masonry' | 'carousel' | 'alternating'
  card_style: 'flat' | 'elevated' | 'bordered' | 'gradient'
  background: 'transparent' | 'light' | 'dark' | 'brand'
  columns: 2 | 3 | 4
  show_cta: boolean
}

export interface ServicesGridProps {
  title?: string
  subtitle?: string
  services: Feature[] // Réutilise le type Feature
  variant: 'minimal' | 'standard' | 'impact' | 'featured'
  layout: 'grid' | 'masonry' | 'carousel' | 'alternating'
  card_style: 'flat' | 'elevated' | 'bordered' | 'gradient'
  background: 'transparent' | 'light' | 'dark' | 'brand'
  columns: 2 | 3 | 4
  show_cta: boolean
}

export interface StatsSectionProps {
  title?: string
  subtitle?: string
  stats: Stat[]
  variant: 'minimal' | 'standard' | 'impact' | 'featured'
  layout: 'grid' | 'inline' | 'cards'
  background: 'transparent' | 'light' | 'dark' | 'brand'
  animation: 'none' | 'counter' | 'reveal'
}

export interface TestimonialCarouselProps {
  title?: string
  subtitle?: string
  testimonials: Testimonial[]
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

export interface ContactFormProps {
  title?: string
  subtitle?: string
  description?: string
  success_message?: string
  fields: FormField[]
  variant: 'minimal' | 'standard' | 'impact' | 'embedded'
  layout: 'centered' | 'split' | 'inline' | 'modal'
  style: 'modern' | 'classic' | 'floating' | 'outlined'
  background: 'transparent' | 'light' | 'dark' | 'brand'
  submit_text: string
  show_privacy: boolean
  privacy_text?: string
}

export interface RichTextProps {
  content: string
  max_width?: 'full' | 'prose' | 'narrow'
  text_align?: 'left' | 'center'
}

export interface BeroasCalculatorProps {
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

// Calculateur de Calories avec nouveau système d'onglets
export interface CalorieCalculatorSectionProps {
  title?: string
  subtitle?: string
  initial_tab: TabType
  show_export: boolean
  variant: 'full' | 'embedded' | 'minimal'
  background: 'neutral' | 'white' | 'brand' | 'transparent'
  custom_cta_text?: string
  custom_cta_url?: string
  tracking_id?: string
}

// Props du Glossaire
export interface GlossarySearchSectionProps {
  title?: string
  subtitle?: string
  variant: 'full' | 'embedded' | 'minimal'
  show_categories: boolean
  show_popular: boolean
  show_filters: boolean
  popular_limit: number
  results_per_page: number
  auto_search: boolean
  placeholder?: string
  background: 'neutral' | 'white' | 'brand' | 'transparent'
  custom_cta_text?: string
  custom_cta_url?: string
  tracking_id?: string
}

export interface GlossaryTermSectionProps {
  // Props injectées par le backend
  term?: {
    slug: string
    title: string
    definition: string
    examples?: string
    formula?: string
    benchmarks?: string
    sources?: string
    category: {
      name: string
      slug: string
      color: string
      description: string
    }
    difficulty_level: string
    is_essential: boolean
    popularity_score: number
    meta_title: string
    meta_description: string
    related_terms: Array<{
      slug: string
      title: string
      relation_type: string
    }>
  }
  slug?: string
  
  // Props configurables
  language?: string
  showRelated?: boolean
  showBreadcrumb?: boolean
  showMetadata?: boolean
  hideNavigation?: boolean
  customTitle?: string
  background?: 'transparent' | 'white' | 'neutral' | 'gradient'
  padding?: 'none' | 'small' | 'normal' | 'large'
  maxWidth?: '3xl' | '4xl' | '5xl' | '6xl' | 'full'
  relatedLimit?: number
  cta_text?: string
  cta_url?: string
  cta_variant?: 'primary' | 'secondary' | 'outline'
  customCSS?: string
  tracking_event?: string
  tracking_category?: string
  tracking_params?: string
}

// Layout config
export interface LayoutConfig {
  columns?: number[]
  gap?: string
  grid_columns?: number
  align_items?: 'start' | 'center' | 'end'
  responsive?: {
    [breakpoint: string]: Partial<LayoutConfig>
  }
}

// Type union SectionData COMPLET
export type SectionData = 
  | HeroBannerProps 
  | HeaderProps
  | CtaBannerProps 
  | FeaturesGridProps 
  | ServicesGridProps
  | StatsSectionProps
  | TestimonialCarouselProps
  | ContactFormProps
  | RichTextProps
  | BeroasCalculatorProps
  | CalorieCalculatorSectionProps
  | GlossarySearchSectionProps
  | GlossaryTermSectionProps

export interface SectionProps {
  type: string
  data: SectionData | Record<string, unknown>
  section_id: number
  layout_config?: LayoutConfig
  children?: SectionProps[]
}

export interface SectionComponentProps<T> {
  data: T
}

// 🔧 Type helper pour éviter any
type ObjectWithInitialTab = {
  initial_tab: unknown
  show_export: unknown
  variant: unknown
}

// 🆕 EXPORT DES FONCTIONS DE VALIDATION (pas en type)
export function isCalorieCalculatorSectionProps(data: unknown): data is CalorieCalculatorSectionProps {
  return (
    typeof data === 'object' &&
    data !== null &&
    'initial_tab' in data &&
    'show_export' in data &&
    'variant' in data
  )
}

export function isBeroasCalculatorProps(data: unknown): data is BeroasCalculatorProps {
  if (
    typeof data !== 'object' ||
    data === null ||
    !('initial_tab' in data) ||
    !('show_export' in data) ||
    !('variant' in data)
  ) {
    return false
  }

  const typedData = data as ObjectWithInitialTab
  const validTabs = ['basic', 'advanced', 'volume', 'matrix']
  
  return (
    typeof typedData.initial_tab === 'string' &&
    validTabs.includes(typedData.initial_tab)
  )
}

// Configurations par défaut pour le page builder MEGAHUB
export const CalorieCalculatorSectionDefaults: CalorieCalculatorSectionProps = {
  title: "Calculateur de Besoins Caloriques",
  subtitle: "Découvrez vos besoins caloriques personnalisés et votre répartition optimale de macronutriments",
  initial_tab: 'calculator',
  show_export: true,
  variant: 'embedded',
  background: 'neutral',
  custom_cta_text: "Obtenir un Plan Nutritionnel Personnalisé",
  custom_cta_url: "/contact",
  tracking_id: "calorie-calculator-section"
}

// Métadonnées pour le page builder
export const CalorieCalculatorSectionMeta = {
  name: "Calculateur de Calories",
  category: "Outils",
  description: "Outil de calcul des besoins caloriques avec interface simplifiée",
  icon: "🧮",
  variants: [
    { value: 'full', label: 'Complet' },
    { value: 'embedded', label: 'Intégré' },
    { value: 'minimal', label: 'Minimal' }
  ],
  backgrounds: [
    { value: 'neutral', label: 'Neutre' },
    { value: 'white', label: 'Blanc' },
    { value: 'brand', label: 'Marque' },
    { value: 'transparent', label: 'Transparent' }
  ],
  tabs: [
    { value: 'calculator', label: 'Calculateur' },
    { value: 'results', label: 'Résultats' }
  ] as Array<{ value: TabType; label: string }>
}

export interface ToolsListingSectionProps {
  category_id?: number
  category_path?: string
  title?: string
  subtitle?: string
  display_mode: 'grid' | 'list' | 'compact'
  show_category_info: boolean
  show_description: boolean
  show_tools_count: boolean
  grid_columns: 2 | 3 | 4
  card_style: 'default' | 'minimal' | 'elevated'
  cta_text?: string
  empty_state_message?: string
  loading_message?: string
}

export interface ToolsListingData {
  category_id?: number
  category_path?: string
  title?: string
  subtitle?: string
  display_mode?: 'grid' | 'list' | 'compact'
  show_category_info?: boolean
  show_description?: boolean
  show_tools_count?: boolean
  grid_columns?: 2 | 3 | 4
  card_style?: 'default' | 'minimal' | 'elevated'
  cta_text?: string
  empty_state_message?: string
  loading_message?: string
}