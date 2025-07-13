// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/contact-form.schema.ts
import { SectionSchema } from '../types'
import { FORM_FIELDS_ARRAY_SCHEMA } from '../utils/array-schemas'
import { DEFAULT_CONTACT_FIELDS, BACKGROUND_OPTIONS } from '../utils/defaults'

export const contactFormSchema: SectionSchema = {
  type: "contact_form",
  name: "Formulaire de Contact",
  category: "forms",
  description: "Formulaire de contact configurable",
  icon: "📧",
  props: {
    title: {
      type: 'string',
      label: 'Titre',
      placeholder: 'Contactez-nous'
    },
    subtitle: {
      type: 'string',
      label: 'Sous-titre',
      placeholder: 'Nous vous répondons rapidement'
    },
    description: {
      type: 'text',
      label: 'Description',
      rows: 2,
      placeholder: 'Décrivez votre projet ou besoin'
    },
    success_message: {
      type: 'text',
      label: 'Message de succès',
      rows: 2,
      default: 'Merci ! Nous vous recontacterons rapidement.'
    },
    fields: {
      ...FORM_FIELDS_ARRAY_SCHEMA,
      default: DEFAULT_CONTACT_FIELDS
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
        { value: 'embedded', label: 'Intégré' }
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
        { value: 'inline', label: 'En ligne' },
        { value: 'modal', label: 'Modal' }
      ]
    },
    style: {
      type: 'select',
      label: 'Style',
      default: 'modern',
      required: true,
      options: [
        { value: 'modern', label: 'Moderne' },
        { value: 'classic', label: 'Classique' },
        { value: 'floating', label: 'Flottant' },
        { value: 'outlined', label: 'Contours' }
      ]
    },
    background: {
      type: 'select',
      label: 'Arrière-plan',
      default: 'transparent',
      required: true,
      options: BACKGROUND_OPTIONS
    },
    submit_text: {
      type: 'string',
      label: 'Texte du bouton',
      default: 'Envoyer',
      required: true
    },
    show_privacy: {
      type: 'boolean',
      label: 'Afficher clause de confidentialité',
      default: true,
      required: true
    },
    privacy_text: {
      type: 'text',
      label: 'Texte de confidentialité',
      rows: 2,
      default: 'En soumettant ce formulaire, vous acceptez notre politique de confidentialité.'
    }
  }
}