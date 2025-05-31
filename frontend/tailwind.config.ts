// tailwind.config.ts
import type { Config } from 'tailwindcss'; // Good practice to import Config type
import tailwindcssAnimate from 'tailwindcss-animate'; // <-- ADD THIS LINE

const config: Config = {
  // Specifies the files to scan for Tailwind classes.
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}', // For Pages Router (if applicable)
    './components/**/*.{js,ts,jsx,tsx,mdx}', // For components
    './app/**/*.{js,ts,jsx,tsx,mdx}' // This covers all files within the 'src' directory

  ],
  darkMode: ['class'],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        purple: '#9b87f5',
        indigo: {
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5'
        },
        orange: {
          100: '#ffe6cc',
          300: '#ffb366',
          400: '#ff9933',
          500: '#ff8000'
        },
        cyan: {
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4'
        },
        pink: {
          300: '#f9a8d4',
          400: '#f472b6',
          500: '#ec4899'
        },
        deepgreen: '#9b87f5',
        burgundy: '#818cf8',
        blueaccent: '#ffe6cc',
        gold: '#67e8f9',
        blackbase: '#ec4899',
        mintgreen: '#CCEFBA',
        aqua: '#AADED9',
        cream: '#F0EFE3',
        lime: '#E3FF70',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'rotate-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'fadeIn': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1'},
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'rotate-slow': 'rotate-slow 3s linear infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
      },
    },
  },
  // Corrected plugins usage
  plugins: [tailwindcssAnimate], // <-- CHANGE THIS LINE
};

export default config;