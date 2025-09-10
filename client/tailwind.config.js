/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'golden': {
          'light': '#C0D5AE',
          'medium': '#E3EDC9', 
          'cream': '#FEFAE0',
          'warm': '#FAEDCD',
          'amber': '#D4A373'
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}