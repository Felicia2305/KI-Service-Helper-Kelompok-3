/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'deep-sea': '#003366',
        'light-bg': '#F5F7FA',
      }
    },
  },
  plugins: [],
}