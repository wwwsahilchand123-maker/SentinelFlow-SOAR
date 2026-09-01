/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0B0F19',
          800: '#111827',
          700: '#1F2937',
          600: '#374151',
        },
        cyber: {
          blue: '#00F0FF',
          purple: '#8B5CF6',
          red: '#EF4444',
          orange: '#F97316',
          yellow: '#FBBF24',
          green: '#10B981',
        }
      }
    },
  },
  plugins: [],
}
