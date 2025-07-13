// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/hero-banner.schema.ts
import { SectionSchema } from '../types'

export const heroSchema: SectionSchema = {
  type: "hero_banner",
  name: "Hero Banner",
  category: "headers",
  description: "Section d'accroche principale avec titre, sous-titre et CTA",
  icon: "🦸",
  props: {
    title: {
      type: 'string',
      label: 'Titre principal',
      required: true,
      placeholder: 'Votre titre accrocheur'
    },
    subtitle: {
      type: 'text',
      label: 'Sous-titre',
      rows: 2,
      placeholder: 'Description qui accompagne le titre'
    },
    cta_text: {
      type: 'string',
      label: 'Texte du bouton principal',
      placeholder: 'Découvrir nos services'
    },
    cta_url: {
      type: 'url',
      label: 'Lien du bouton principal',
      placeholder: '/contact'
    },
    secondary_cta_text: {
      type: 'string',
      label: 'Texte du bouton secondaire',
      placeholder: 'En savoir plus'
    },
    secondary_cta_url: {
      type: 'url',
      label: 'Lien du bouton secondaire',
      placeholder: '/about'
    },
    variant: {
      type: 'select',
      label: 'Variante',
      default: 'standard',
      required: true,
      options: [
        { value: 'minimal', label: 'Minimal' },
        { value: 'standard', label: 'Standard' },
        { value: 'impact', label: 'Impact' },
        { value: 'hero', label: 'Hero XL' }
      ]
    },
    layout: {
      type: 'select',
      label: 'Layout',
      default: 'centered',
      required: true,
      options: [
        { value: 'centered', label: 'Centré' },
        { value: 'split', label: 'Split (texte + visuel)' }
      ]
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      default: 'gradient-brand',
      required: true,
      options: [
        { value: 'gradient-brand', label: 'Gradient Marque' },
        { value: 'gradient-dark', label: 'Gradient Sombre' },
        { value: 'solid-light', label: 'Clair Uni' },
        { value: 'solid-dark', label: 'Sombre Uni' }
      ]
    },
    show_badge: {
      type: 'boolean',
      label: 'Afficher un badge',
      default: false
    },
    badge_text: {
      type: 'string',
      label: 'Texte du badge',
      placeholder: 'Nouveau !'
    },
    show_stats: {
      type: 'boolean',
      label: 'Afficher des statistiques',
      default: false
    }
  }
}