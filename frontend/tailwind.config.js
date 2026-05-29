/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#f8fafc',
          100: '#1e1e2e',
          200: '#181825',
          300: '#11111b',
          400: '#0a0a14',
          500: '#05050a',
          600: '#020205',
          700: '#010102',
          800: '#000001',
          900: '#000000',
        },
        accent: {
          50: '#f0e6ff',
          100: '#d4b8ff',
          200: '#b88aff',
          300: '#9c5cff',
          400: '#8040f0',
          500: '#6c28d9',
          600: '#5810c2',
          700: '#4400ab',
          800: '#300094',
          900: '#1c007d',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(108, 40, 217, 0.3)' },
          '100%': { boxShadow: '0 0 40px rgba(108, 40, 217, 0.6)' },
        },
      },
    },
  },
  plugins: [],
}
