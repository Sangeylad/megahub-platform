// src/lib/sections-registry/schemas/header.schema.ts
import { SectionSchema } from '../types'

export const headerSchema: SectionSchema = {
  type: "header",
  name: "Header",
  category: "layout",
  description: "En-tête du site avec navigation",
  icon: "🔝",
  props: {
    variant: {
      type: 'select',
      label: 'Type de header',
      default: 'default',
      required: true,
      options: [
        { value: 'default', label: 'Header avec navigation' },
        { value: 'none', label: 'Pas de header' }
      ]
    },
    logo_url: {
      type: 'url',
      label: 'URL du logo',
      default: '/logo.svg',
      placeholder: '/logo.svg'
    },
    logo_alt: {
      type: 'string',
      label: 'Texte alternatif du logo',
      default: 'Logo',
      placeholder: 'Nom de votre entreprise'
    },
    cta_text: {
      type: 'string',
      label: 'Texte du bouton CTA',
      placeholder: 'Nous contacter'
    },
    cta_url: {
      type: 'url',
      label: 'Lien du bouton CTA',
      placeholder: '/contact'
    },
    show_contact_info: {
      type: 'boolean',
      label: 'Afficher barre de contact',
      default: false
    },
    contact_phone: {
      type: 'string',
      label: 'Téléphone de contact',
      placeholder: '01 23 45 67 89'
    },
    contact_email: {
      type: 'string',
      label: 'Email de contact',
      placeholder: 'contact@entreprise.fr'
    }
  }
}