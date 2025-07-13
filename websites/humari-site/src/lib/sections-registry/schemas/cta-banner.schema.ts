// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/cta-banner.schema.ts
import { SectionSchema } from '../types'

export const ctaSchema: SectionSchema = {
  type: "cta_banner",
  name: "CTA Banner",
  category: "cta", 
  description: "Bandeau d'appel à l'action puissant",
  icon: "📢",
  props: {
    title: {
      type: 'string',
      label: 'Titre',
      required: true,
      placeholder: 'Prêt à commencer ?'
    },
    subtitle: {
      type: 'string',
      label: 'Sous-titre',
      placeholder: 'Ne perdez plus de temps'
    },
    description: {
      type: 'text',
      label: 'Description',
      rows: 2,
      placeholder: 'Description plus détaillée'
    },
    primary_cta_text: {
      type: 'string',
      label: 'Bouton principal',
      required: true,
      placeholder: 'Commencer maintenant'
    },
    primary_cta_url: {
      type: 'url',
      label: 'Lien bouton principal',
      required: true,
      placeholder: '/contact'
    },
    secondary_cta_text: {
      type: 'string',
      label: 'Bouton secondaire',
      placeholder: 'En savoir plus'
    },
    secondary_cta_url: {
      type: 'url',
      label: 'Lien bouton secondaire',
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
        { value: 'urgent', label: 'Urgent' }
      ]
    },
    layout: {
      type: 'select',
      label: 'Layout',
      default: 'centered',
      required: true,
      options: [
        { value: 'centered', label: 'Centré' },
        { value: 'split', label: 'Split' },
        { value: 'banner', label: 'Banner horizontal' },
        { value: 'floating', label: 'Flottant' }
      ]
    },
    style: {
      type: 'select',
      label: 'Style',
      default: 'solid',
      required: true,
      options: [
        { value: 'solid', label: 'Solide' },
        { value: 'gradient', label: 'Gradient' },
        { value: 'outlined', label: 'Contours' },
        { value: 'glass', label: 'Verre' }
      ]
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      default: 'brand',
      required: true,
      options: [
        { value: 'brand', label: 'Couleur marque' },
        { value: 'dark', label: 'Sombre' },
        { value: 'light', label: 'Clair' },
        { value: 'gradient', label: 'Gradient' },
        { value: 'image', label: 'Image' }
      ]
    },
    urgency_level: {
      type: 'select',
      label: 'Niveau d\'urgence',
      default: 'none',
      required: true,
      options: [
        { value: 'none', label: 'Aucune' },
        { value: 'low', label: 'Faible' },
        { value: 'medium', label: 'Moyenne' },
        { value: 'high', label: 'Élevée' }
      ]
    },
    show_guarantee: {
      type: 'boolean',
      label: 'Afficher garantie',
      default: false
    },
    guarantee_text: {
      type: 'string',
      label: 'Texte de garantie',
      placeholder: '✅ 100% Gratuit - Aucun engagement'
    },
    show_social_proof: {
      type: 'boolean',
      label: 'Afficher preuve sociale',
      default: false
    },
    social_proof: {
      type: 'string',
      label: 'Texte preuve sociale',
      placeholder: '⭐ Rejoint par +500 entreprises'
    },
    show_countdown: {
      type: 'boolean',
      label: 'Afficher compte à rebours',
      default: false
    },
    countdown_text: {
      type: 'string',
      label: 'Texte compte à rebours',
      placeholder: '⏰ Offre limitée - Plus que 3 jours'
    },
    badge_text: {
      type: 'string',
      label: 'Texte du badge',
      placeholder: 'Offre Spéciale'
    }
  }
}