// /var/www/megahub/websites/humari-site/src/lib/sections-registry/utils/defaults.ts
import { SelectOption } from '../types'

// ✅ Types stricts pour tous les defaults
export const HUMARI_STATS_DEFAULT: Record<string, unknown>[] = [
  {
    number: "+150",
    label: "Clients",
    description: "Clients accompagnés depuis 2019",
    icon: "👥"
  },
  {
    number: "4.9/5",
    label: "Satisfaction",
    description: "Note moyenne clients",
    icon: "⭐"
  },
  {
    number: "+200%",
    label: "ROI Moyen",
    description: "Retour sur investissement",
    icon: "📈"
  },
  {
    number: "5 ans",
    label: "Expertise",
    description: "D'expérience terrain",
    icon: "🎯"
  }
]

export const HUMARI_SERVICES_DEFAULT: Record<string, unknown>[] = [
  {
    title: "SEO & Référencement",
    description: "Positionnez-vous en première page Google. Audit technique, optimisation on-page, netlinking.",
    icon: "🎯",
    badge: "Expertise #1",
    cta_text: "Découvrir le SEO",
    cta_url: "/seo"
  },
  {
    title: "Développement Web",
    description: "Sites web performants et convertisseurs. WordPress, e-commerce, applications sur mesure.",
    icon: "💻",
    badge: "Sur Mesure",
    cta_text: "Voir nos Réalisations",
    cta_url: "/dev-web"
  },
  {
    title: "Publicité Digitale",
    description: "Campagnes Google Ads et Meta rentables. Maximisez votre ROI publicitaire.",
    icon: "📊",
    badge: "ROI Garanti",
    cta_text: "Lancer mes Campagnes",
    cta_url: "/ads"
  },
  {
    title: "Réseaux Sociaux",
    description: "Community management et social media marketing pour engager votre audience.",
    icon: "📱",
    badge: "Engagement+",
    cta_text: "Booster ma Présence",
    cta_url: "/reseaux-sociaux"
  }
]

export const HUMARI_TESTIMONIALS_DEFAULT: Record<string, unknown>[] = [
  {
    content: "Humari a transformé notre présence en ligne. +300% de trafic organique en 8 mois et des ventes qui explosent. Une équipe à l'écoute et ultra-compétente.",
    author: "Marie Dubois",
    position: "Directrice Marketing",
    company: "TechStartup Pro",
    rating: 5,
    project: "Refonte SEO complète",
    result: "+300% de trafic organique"
  },
  {
    content: "Notre nouveau site e-commerce développé par Humari convertit 4x mieux que l'ancien. ROI de nos campagnes Google Ads multiplié par 3. Investissement rentabilisé en 2 mois.",
    author: "Jean-Pierre Martin",
    position: "CEO",
    company: "Boutique Mode & Style",
    rating: 5,
    project: "Site e-commerce + Ads",
    result: "ROI x3 en 2 mois"
  },
  {
    content: "Social media strategy au top ! +5000 followers qualifiés en 6 mois, engagement rate de 8.2%. L'équipe comprend parfaitement notre secteur B2B.",
    author: "Sophie Laurent",
    position: "Responsable Communication",
    company: "InnovTech Solutions",
    rating: 5,
    project: "Social Media Management",
    result: "+5K followers qualifiés"
  },
  {
    content: "Audit SEO révélateur ! 47 optimisations critiques identifiées. En 4 mois, première page Google sur nos 3 mots-clés stratégiques. Chiffre d'affaires +65%.",
    author: "Thomas Petit",
    position: "Fondateur",
    company: "Consultant Expert-Comptable",
    rating: 5,
    project: "Stratégie SEO locale",
    result: "CA +65% en 4 mois"
  }
]

export const DEFAULT_CONTACT_FIELDS: Record<string, unknown>[] = [
  {
    name: "nom",
    label: "Nom de l'entreprise",
    type: "text",
    required: true,
    placeholder: "Votre entreprise"
  },
  {
    name: "prenom",
    label: "Votre prénom",
    type: "text",
    required: true,
    placeholder: "John"
  },
  {
    name: "email",
    label: "Email professionnel",
    type: "email",
    required: true,
    placeholder: "john@entreprise.fr"
  },
  {
    name: "telephone",
    label: "Téléphone",
    type: "tel",
    required: false,
    placeholder: "06 12 34 56 78"
  },
  {
    name: "secteur",
    label: "Secteur d'activité",
    type: "select",
    required: true,
    options: [
      "E-commerce",
      "Services B2B",
      "Services B2C",
      "Industrie",
      "Santé",
      "Immobilier",
      "Formation",
      "Restauration",
      "Tech/SaaS",
      "Autre"
    ]
  },
  {
    name: "objectif",
    label: "Votre objectif principal",
    type: "select",
    required: true,
    options: [
      "Augmenter ma visibilité Google",
      "Développer mes ventes en ligne",
      "Créer/refondre mon site web",
      "Optimiser mes publicités",
      "Développer ma présence sociale",
      "Stratégie marketing complète"
    ]
  },
  {
    name: "budget",
    label: "Budget mensuel envisagé",
    type: "select",
    required: false,
    options: [
      "< 1 500€",
      "1 500€ - 3 000€",
      "3 000€ - 5 000€",
      "5 000€ - 10 000€",
      "+ 10 000€"
    ]
  },
  {
    name: "details",
    label: "Décrivez votre projet",
    type: "textarea",
    required: false,
    rows: 4,
    placeholder: "Contexte, objectifs spécifiques, contraintes particulières..."
  }
]

export const DEFAULT_HERO_STATS: Record<string, unknown>[] = [
  {
    number: "+150",
    label: "Clients Accompagnés"
  },
  {
    number: "4.9/5",
    label: "Satisfaction Client"
  },
  {
    number: "+200%",
    label: "ROI Moyen"
  },
  {
    number: "5 ans",
    label: "d'Expertise"
  }
]

export const DEFAULT_CTA_STATS: Record<string, unknown>[] = [
  {
    number: "< 2s",
    label: "Temps de chargement"
  },
  {
    number: "+15%",
    label: "Taux de conversion"
  }
]

// Options communes réutilisables
export const VARIANT_OPTIONS: SelectOption[] = [
  { value: 'minimal', label: 'Minimal' },
  { value: 'standard', label: 'Standard' },
  { value: 'impact', label: 'Impact' },
  { value: 'featured', label: 'Featured' }
]

export const HERO_VARIANT_OPTIONS: SelectOption[] = [
  { value: 'minimal', label: 'Minimal' },
  { value: 'standard', label: 'Standard' },
  { value: 'impact', label: 'Impact' },
  { value: 'hero', label: 'Hero XL' }
]

export const CTA_VARIANT_OPTIONS: SelectOption[] = [
  { value: 'minimal', label: 'Minimal' },
  { value: 'standard', label: 'Standard' },
  { value: 'impact', label: 'Impact' },
  { value: 'urgent', label: 'Urgent' }
]

export const BACKGROUND_OPTIONS: SelectOption[] = [
  { value: 'transparent', label: 'Transparent' },
  { value: 'light', label: 'Clair' },
  { value: 'dark', label: 'Sombre' },
  { value: 'brand', label: 'Couleur marque' }
]

export const HERO_BACKGROUND_OPTIONS: SelectOption[] = [
  { value: 'gradient-brand', label: 'Gradient Marque' },
  { value: 'gradient-dark', label: 'Gradient Sombre' },
  { value: 'solid-light', label: 'Clair Uni' },
  { value: 'solid-dark', label: 'Sombre Uni' }
]

export const CTA_BACKGROUND_OPTIONS: SelectOption[] = [
  { value: 'brand', label: 'Couleur marque' },
  { value: 'dark', label: 'Sombre' },
  { value: 'light', label: 'Clair' },
  { value: 'gradient', label: 'Gradient' },
  { value: 'image', label: 'Image' }
]

export const LAYOUT_OPTIONS: SelectOption[] = [
  { value: 'centered', label: 'Centré' },
  { value: 'split', label: 'Split' }
]

export const CTA_LAYOUT_OPTIONS: SelectOption[] = [
  { value: 'centered', label: 'Centré' },
  { value: 'split', label: 'Split' },
  { value: 'banner', label: 'Banner horizontal' },
  { value: 'floating', label: 'Flottant' }
]

export const TESTIMONIAL_LAYOUT_OPTIONS: SelectOption[] = [
  { value: 'carousel', label: 'Carrousel' },
  { value: 'grid', label: 'Grille' },
  { value: 'masonry', label: 'Masonry' },
  { value: 'single', label: 'Unique' }
]

export const TESTIMONIAL_STYLE_OPTIONS: SelectOption[] = [
  { value: 'cards', label: 'Cartes' },
  { value: 'quotes', label: 'Citations' },
  { value: 'bubbles', label: 'Bulles' },
  { value: 'testimonial-wall', label: 'Mur de témoignages' }
]

export const COLUMNS_OPTIONS: SelectOption[] = [
  { value: '2', label: '2 colonnes' },
  { value: '3', label: '3 colonnes' },
  { value: '4', label: '4 colonnes' }
]

export const STATS_LAYOUT_OPTIONS: SelectOption[] = [
  { value: 'grid', label: 'Grille' },
  { value: 'inline', label: 'En ligne' },
  { value: 'cards', label: 'Cartes' }
]

export const STATS_ANIMATION_OPTIONS: SelectOption[] = [
  { value: 'none', label: 'Aucune' },
  { value: 'counter', label: 'Compteur' },
  { value: 'reveal', label: 'Révélation' }
]

export const SERVICES_LAYOUT_OPTIONS: SelectOption[] = [
  { value: 'grid', label: 'Grille' },
  { value: 'masonry', label: 'Masonry' },
  { value: 'carousel', label: 'Carrousel' },
  { value: 'alternating', label: 'Alterné' }
]

export const CARD_STYLE_OPTIONS: SelectOption[] = [
  { value: 'flat', label: 'Plat' },
  { value: 'elevated', label: 'Élevé' },
  { value: 'bordered', label: 'Bordure' },
  { value: 'gradient', label: 'Gradient' }
]

export const CTA_STYLE_OPTIONS: SelectOption[] = [
  { value: 'solid', label: 'Solide' },
  { value: 'gradient', label: 'Gradient' },
  { value: 'outlined', label: 'Contours' },
  { value: 'glass', label: 'Verre' }
]

export const URGENCY_LEVEL_OPTIONS: SelectOption[] = [
  { value: 'none', label: 'Aucune' },
  { value: 'low', label: 'Faible' },
  { value: 'medium', label: 'Moyenne' },
  { value: 'high', label: 'Élevée' }
]

export const CONTACT_VARIANT_OPTIONS: SelectOption[] = [
  { value: 'minimal', label: 'Minimal' },
  { value: 'standard', label: 'Standard' },
  { value: 'impact', label: 'Impact' },
  { value: 'embedded', label: 'Intégré' }
]

export const CONTACT_LAYOUT_OPTIONS: SelectOption[] = [
  { value: 'centered', label: 'Centré' },
  { value: 'split', label: 'Split' },
  { value: 'inline', label: 'En ligne' },
  { value: 'modal', label: 'Modal' }
]

export const CONTACT_STYLE_OPTIONS: SelectOption[] = [
  { value: 'modern', label: 'Moderne' },
  { value: 'classic', label: 'Classique' },
  { value: 'floating', label: 'Flottant' },
  { value: 'outlined', label: 'Contours' }
]

export const RICH_TEXT_WIDTH_OPTIONS: SelectOption[] = [
  { value: 'full', label: 'Pleine largeur' },
  { value: 'prose', label: 'Largeur prose' },
  { value: 'narrow', label: 'Étroit' }
]

export const TEXT_ALIGN_OPTIONS: SelectOption[] = [
  { value: 'left', label: 'Gauche' },
  { value: 'center', label: 'Centre' }
]

export const LAYOUT_COLUMNS_OPTIONS: SelectOption[] = [
  { value: '[12]', label: '1 colonne (12/12)' },
  { value: '[6, 6]', label: '2 colonnes égales (6/6)' },
  { value: '[8, 4]', label: '2 colonnes (8/4)' },
  { value: '[4, 8]', label: '2 colonnes (4/8)' },
  { value: '[4, 4, 4]', label: '3 colonnes égales (4/4/4)' },
  { value: '[3, 6, 3]', label: '3 colonnes (3/6/3)' },
  { value: '[3, 3, 3, 3]', label: '4 colonnes égales (3/3/3/3)' }
]

export const GAP_OPTIONS: SelectOption[] = [
  { value: '1rem', label: 'Petit (1rem)' },
  { value: '2rem', label: 'Moyen (2rem)' },
  { value: '3rem', label: 'Grand (3rem)' },
  { value: '4rem', label: 'Très grand (4rem)' }
]

export const ALIGN_ITEMS_OPTIONS: SelectOption[] = [
  { value: 'start', label: 'Haut' },
  { value: 'center', label: 'Centre' },
  { value: 'end', label: 'Bas' }
]