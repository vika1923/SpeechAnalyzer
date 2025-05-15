import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        deepgreen: '#003432',
        burgundy: '#80003A',
        blueaccent: '#2C43DE',
        gold: '#A87026',
        blackbase: '#21201E',
        mintgreen: '#CCEFBA',
        aqua: '#AADED9',
        cream: '#F0EFE3',
        lime: '#E3FF70',
      },
      animation: {
        'rotate-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;

export default config;