// /var/www/megahub/websites/humari-site/src/lib/sections-registry/schemas/rich-text.schema.ts
import { SectionSchema } from '../types'

export const richTextSchema: SectionSchema = {
  type: "rich_text",
  name: "Contenu Riche",
  category: "content",
  description: "Bloc de contenu avec support Markdown", 
  icon: "📝",
  props: {
    content: {
      type: 'text',
      label: 'Contenu Markdown',
      required: true,
      rows: 8,
      placeholder: '# Titre\n\nVotre contenu en **Markdown**...'
    },
    max_width: {
      type: 'select',
      label: 'Largeur maximale',
      default: 'prose',
      options: [
        { value: 'full', label: 'Pleine largeur' },
        { value: 'prose', label: 'Largeur prose' },
        { value: 'narrow', label: 'Étroit' }
      ]
    },
    text_align: {
      type: 'select',
      label: 'Alignement du texte',
      default: 'left',
      options: [
        { value: 'left', label: 'Gauche' },
        { value: 'center', label: 'Centre' }
      ]
    }
  }
}