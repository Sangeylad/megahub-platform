// tailwind.config.js - NOUVELLE PALETTE HUMARI
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // 🔥 BRAND HUMARI
        brand: {
          50: '#fef2f4',
          100: '#fde6e9', 
          200: '#fbd0d9',
          300: '#f7aab9',
          400: '#f27a93',
          500: '#fe0049', // 🎯 COULEUR PRINCIPALE
          600: '#e8003f',
          700: '#c4003a',
          800: '#a30335',
          900: '#8b0732',
        },
        
        // 🌙 DARK THEME
        dark: {
          50: '#f1f3f7',
          100: '#e0e5ed',
          200: '#c1ccdc',
          300: '#95a8c2',
          400: '#6280a2',
          500: '#4a628a',
          600: '#3a4f73',
          700: '#30405e',
          800: '#2a364f',
          900: '#141B2A', // 🎯 COULEUR FONCÉE
        },
        
        // Gris neutres modernisés
        neutral: {
          50: '#fafbfc',
          100: '#f4f6f8', 
          200: '#e5e9ed',
          300: '#d1d8e0',
          400: '#9aa4b2',
          500: '#6b7684',
          600: '#4a5568',
          700: '#2d3748',
          800: '#1a202c',
          900: '#171923',
        }
      },
      
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Inter', 'system-ui', 'sans-serif'],
      },
      
      // 🎨 Effets visuels modernes
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-brand': 'linear-gradient(135deg, #fe0049 0%, #8b0732 100%)',
        'gradient-dark': 'linear-gradient(135deg, #141B2A 0%, #2a364f 100%)',
        'gradient-mesh': 'radial-gradient(circle at 25% 25%, #fe0049 0%, transparent 50%), radial-gradient(circle at 75% 75%, #141B2A 0%, transparent 50%)',
      },
      
      boxShadow: {
        'brand': '0 10px 25px -3px rgba(254, 0, 73, 0.1), 0 4px 6px -2px rgba(254, 0, 73, 0.05)',
        'dark': '0 10px 25px -3px rgba(20, 27, 42, 0.1), 0 4px 6px -2px rgba(20, 27, 42, 0.05)',
        'glow': '0 0 20px rgba(254, 0, 73, 0.3)',
      },
      
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'pulse-brand': 'pulse-brand 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-brand': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.8 },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio')
  ],
}