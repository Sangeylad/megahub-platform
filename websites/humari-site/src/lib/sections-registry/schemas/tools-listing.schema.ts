// lib/sections-registry/schemas/tools-listing.schema.ts - CORRIGÉ
import { z } from 'zod'

export const toolsListingSchema = {
  type: 'tools_listing',
  name: 'Liste d\'outils',
  category: 'tools',
  description: 'Affiche une liste d\'outils d\'une catégorie spécifique',
  layoutContainer: false,
  props: {
    category_id: {
      type: 'number' as const,
      label: 'ID de la catégorie',
      description: 'Identifiant numérique de la catégorie d\'outils',
      required: false
    },
    category_path: {
      type: 'text' as const,
      label: 'Chemin de la catégorie',
      description: 'URL path de la catégorie (ex: /outils/seo)',
      required: false,
      placeholder: '/outils/seo'
    },
    title: {
      type: 'text' as const,
      label: 'Titre',
      description: 'Titre de la section',
      required: false,
      default: 'Nos Outils'
    },
    subtitle: {
      type: 'textarea' as const,
      label: 'Sous-titre',
      description: 'Description sous le titre',
      required: false
    },
    display_mode: {
      type: 'select' as const,
      label: 'Mode d\'affichage',
      description: 'Comment afficher les outils',
      required: false,
      default: 'grid',
      options: [
        { value: 'grid', label: 'Grille' },
        { value: 'list', label: 'Liste' },
        { value: 'compact', label: 'Compact' }
      ]
    },
    show_category_info: {
      type: 'boolean' as const,
      label: 'Afficher info catégorie',
      description: 'Affiche les informations de la catégorie',
      required: false,
      default: true
    },
    show_description: {
      type: 'boolean' as const,
      label: 'Afficher descriptions',
      description: 'Affiche la description de chaque outil',
      required: false,
      default: true
    },
    show_tools_count: {
      type: 'boolean' as const,
      label: 'Afficher nombre d\'outils',
      description: 'Affiche le compteur d\'outils',
      required: false,
      default: true
    },
    grid_columns: {
      type: 'select' as const,
      label: 'Nombre de colonnes',
      description: 'Colonnes dans la grille',
      required: false,
      default: '3',
      options: [
        { value: '2', label: '2 colonnes' },
        { value: '3', label: '3 colonnes' },
        { value: '4', label: '4 colonnes' }
      ]
    },
    card_style: {
      type: 'select' as const,
      label: 'Style des cartes',
      description: 'Style visuel des cartes d\'outils',
      required: false,
      default: 'default',
      options: [
        { value: 'default', label: 'Par défaut' },
        { value: 'minimal', label: 'Minimal' },
        { value: 'elevated', label: 'Élevé' }
      ]
    },
    cta_text: {
      type: 'text' as const,
      label: 'Texte du bouton',
      description: 'Texte du bouton d\'action',
      required: false,
      default: 'Utiliser l\'outil'
    },
    empty_state_message: {
      type: 'textarea' as const,
      label: 'Message état vide',
      description: 'Message quand aucun outil n\'est disponible',
      required: false,
      default: 'Aucun outil disponible dans cette catégorie.'
    },
    loading_message: {
      type: 'text' as const,
      label: 'Message de chargement',
      description: 'Message pendant le chargement',
      required: false,
      default: 'Chargement des outils...'
    }
  }
}

// Export du type inféré pour validation Zod si nécessaire
export const toolsListingZodSchema = z.object({
  category_id: z.number().optional(),
  category_path: z.string().optional(),
  title: z.string().optional().default('Nos Outils'),
  subtitle: z.string().optional(),
  display_mode: z.enum(['grid', 'list', 'compact']).default('grid'),
  show_category_info: z.boolean().default(true),
  show_description: z.boolean().default(true),
  show_tools_count: z.boolean().default(true),
  grid_columns: z.number().min(2).max(4).default(3),
  card_style: z.enum(['default', 'minimal', 'elevated']).default('default'),
  cta_text: z.string().optional().default('Utiliser l\'outil'),
  empty_state_message: z.string().optional().default('Aucun outil disponible dans cette catégorie.'),
  loading_message: z.string().optional().default('Chargement des outils...')
}).refine(
  (data) => data.category_id !== undefined || data.category_path !== undefined,
  {
    message: "Au moins un paramètre category_id ou category_path est requis",
    path: ["category_id"]
  }
)

export type ToolsListingConfig = z.infer<typeof toolsListingZodSchema>