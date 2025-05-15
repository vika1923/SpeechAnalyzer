import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        cream: "var(--cream)",
        blackbase: "var(--blackbase)",
        deepgreen: "var(--deepgreen)",
        lime: "var(--lime)",
        mintgreen: "var(--mintgreen)",
        aqua: "var(--aqua)",
        burgundy: "var(--burgundy)",
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: "var(--primary)",
        "primary-foreground": "var(--primary-foreground)",
        secondary: "var(--secondary)",
        "secondary-foreground": "var(--secondary-foreground)",
        destructive: "var(--destructive)",
        "destructive-foreground": "var(--destructive-foreground)",
        muted: "var(--muted)",
        "muted-foreground": "var(--muted-foreground)",
        accent: "var(--accent)",
        "accent-foreground": "var(--accent-foreground)",
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "var(--popover-foreground)",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "var(--card-foreground)",
        },
      },
      borderRadius: {
        DEFAULT: "var(--radius)",
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        floating: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        gradientShift: {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
        "pulse-slow": {
          "0%, 100%": { 
            opacity: "1",
            transform: "scale(1)"
          },
          "50%": { 
            opacity: "0.8",
            transform: "scale(1.05)"
          },
        },
      },
      animation: {
        floating: "floating 3s ease-in-out infinite",
        gradientShift: "gradientShift 15s ease infinite",
        "pulse-slow": "pulse-slow 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;