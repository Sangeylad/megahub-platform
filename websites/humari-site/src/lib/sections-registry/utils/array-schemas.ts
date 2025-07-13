// /var/www/megahub/websites/humari-site/src/lib/sections-registry/utils/array-schemas.ts
import { SectionPropSchema } from '../types'

export const STATS_ARRAY_SCHEMA: SectionPropSchema = {
  type: 'stats_array',
  label: 'Statistiques',
  required: true,
  minItems: 1,
  maxItems: 6,
  addButtonText: 'Ajouter une statistique',
  removeButtonText: 'Supprimer',
  itemSchema: {
    number: {
      type: 'string',
      label: 'Nombre/Métrique',
      required: true,
      placeholder: '+150'
    },
    label: {
      type: 'string',
      label: 'Label',
      required: true,
      placeholder: 'Clients'
    },
    description: {
      type: 'text',
      label: 'Description',
      placeholder: 'Clients satisfaits depuis 2019',
      rows: 2
    },
    icon: {
      type: 'string',
      label: 'Icône (emoji)',
      placeholder: '👥'
    }
  }
}

export const SERVICES_ARRAY_SCHEMA: SectionPropSchema = {
  type: 'services_array',
  label: 'Services',
  required: true,
  minItems: 1,
  maxItems: 8,
  addButtonText: 'Ajouter un service',
  removeButtonText: 'Supprimer',
  itemSchema: {
    title: {
      type: 'string',
      label: 'Titre du service',
      required: true,
      placeholder: 'SEO & Référencement'
    },
    description: {
      type: 'text',
      label: 'Description',
      required: true,
      rows: 3,
      placeholder: 'Description du service...'
    },
    icon: {
      type: 'string',
      label: 'Icône (emoji)',
      placeholder: '🎯'
    },
    badge: {
      type: 'string',
      label: 'Badge',
      placeholder: 'Expertise #1'
    },
    cta_text: {
      type: 'string',
      label: 'Texte du bouton',
      placeholder: 'Découvrir le SEO'
    },
    cta_url: {
      type: 'url',
      label: 'Lien du bouton',
      placeholder: '/seo'
    }
  }
}

export const TESTIMONIALS_ARRAY_SCHEMA: SectionPropSchema = {
  type: 'testimonials_array',
  label: 'Témoignages',
  required: true,
  minItems: 1,
  maxItems: 10,
  addButtonText: 'Ajouter un témoignage',
  removeButtonText: 'Supprimer',
  itemSchema: {
    content: {
      type: 'text',
      label: 'Contenu du témoignage',
      required: true,
      rows: 4,
      placeholder: 'Humari a transformé notre présence en ligne...'
    },
    author: {
      type: 'string',
      label: 'Nom de l\'auteur',
      required: true,
      placeholder: 'Marie Dubois'
    },
    position: {
      type: 'string',
      label: 'Poste',
      required: true,
      placeholder: 'Directrice Marketing'
    },
    company: {
      type: 'string',
      label: 'Entreprise',
      required: true,
      placeholder: 'TechStartup Pro'
    },
    rating: {
      type: 'number',
      label: 'Note (1-5)',
      placeholder: '5'
    },
    project: {
      type: 'string',
      label: 'Projet réalisé',
      placeholder: 'Refonte SEO complète'
    },
    result: {
      type: 'string',
      label: 'Résultat obtenu',
      placeholder: '+300% de trafic organique'
    },
    avatar: {
      type: 'url',
      label: 'URL de l\'avatar',
      placeholder: 'https://example.com/avatar.jpg'
    }
  }
}

export const FORM_FIELDS_ARRAY_SCHEMA: SectionPropSchema = {
  type: 'fields_array',
  label: 'Champs du formulaire',
  required: true,
  minItems: 1,
  maxItems: 15,
  addButtonText: 'Ajouter un champ',
  removeButtonText: 'Supprimer',
  itemSchema: {
    name: {
      type: 'string',
      label: 'Nom du champ',
      required: true,
      placeholder: 'email'
    },
    label: {
      type: 'string',
      label: 'Label affiché',
      required: true,
      placeholder: 'Adresse email'
    },
    type: {
      type: 'select',
      label: 'Type de champ',
      required: true,
      options: [
        { value: 'text', label: 'Texte' },
        { value: 'email', label: 'Email' },
        { value: 'tel', label: 'Téléphone' },
        { value: 'textarea', label: 'Zone de texte' },
        { value: 'select', label: 'Liste déroulante' },
        { value: 'checkbox', label: 'Case à cocher' },
        { value: 'radio', label: 'Bouton radio' }
      ]
    },
    placeholder: {
      type: 'string',
      label: 'Placeholder',
      placeholder: 'votre@email.fr'
    },
    required: {
      type: 'boolean',
      label: 'Champ obligatoire'
    },
    rows: {
      type: 'number',
      label: 'Nombre de lignes (textarea)',
      placeholder: '4'
    }
  }
}

export const FEATURES_ARRAY_SCHEMA: SectionPropSchema = {
  type: 'services_array', // Réutilise le même schema que services
  label: 'Fonctionnalités',
  required: true,
  minItems: 1,
  maxItems: 12,
  addButtonText: 'Ajouter une fonctionnalité',
  removeButtonText: 'Supprimer',
  itemSchema: {
    title: {
      type: 'string',
      label: 'Titre de la fonctionnalité',
      required: true,
      placeholder: 'Optimisation SEO'
    },
    description: {
      type: 'text',
      label: 'Description',
      required: true,
      rows: 3,
      placeholder: 'Description de la fonctionnalité...'
    },
    icon: {
      type: 'string',
      label: 'Icône (emoji)',
      placeholder: '⚡'
    },
    badge: {
      type: 'string',
      label: 'Badge',
      placeholder: 'Nouveau'
    }
  }
}