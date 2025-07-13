// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/testimonial-carousel.schema.ts
import { SectionSchema } from '../types'
import { TESTIMONIALS_ARRAY_SCHEMA } from '../utils/array-schemas'
import { HUMARI_TESTIMONIALS_DEFAULT, VARIANT_OPTIONS, BACKGROUND_OPTIONS } from '../utils/defaults'

export const testimonialSchema: SectionSchema = {
  type: "testimonial_carousel",
  name: "Carrousel Témoignages",
  category: "social",
  description: "Témoignages clients en carrousel ou grille",
  icon: "🗣️",
  props: {
    title: {
      type: 'string',
      label: 'Titre',
      placeholder: 'Ce que disent nos clients'
    },
    subtitle: {
      type: 'text',
      label: 'Sous-titre',
      rows: 2,
      placeholder: 'Témoignages authentiques'
    },
    testimonials: {
      ...TESTIMONIALS_ARRAY_SCHEMA,
      default: HUMARI_TESTIMONIALS_DEFAULT
    },
    variant: {
      type: 'select',
      label: 'Variante',
      default: 'standard',
      required: true,
      options: VARIANT_OPTIONS
    },
    layout: {
      type: 'select',
      label: 'Layout',
      default: 'carousel',
      required: true,
      options: [
        { value: 'carousel', label: 'Carrousel' },
        { value: 'grid', label: 'Grille' },
        { value: 'masonry', label: 'Masonry' },
        { value: 'single', label: 'Unique' }
      ]
    },
    style: {
      type: 'select',
      label: 'Style',
      default: 'cards',
      required: true,
      options: [
        { value: 'cards', label: 'Cartes' },
        { value: 'quotes', label: 'Citations' },
        { value: 'bubbles', label: 'Bulles' },
        { value: 'testimonial-wall', label: 'Mur de témoignages' }
      ]
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      default: 'transparent',
      required: true,
      options: BACKGROUND_OPTIONS
    },
    autoplay: {
      type: 'boolean',
      label: 'Lecture automatique',
      default: true,
      required: true
    },
    show_navigation: {
      type: 'boolean',
      label: 'Afficher navigation',
      default: true,
      required: true
    },
    show_dots: {
      type: 'boolean',
      label: 'Afficher les points',
      default: true,
      required: true
    },
    show_ratings: {
      type: 'boolean',
      label: 'Afficher les notes',
      default: true,
      required: true
    }
  }
}