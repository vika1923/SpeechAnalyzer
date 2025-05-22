// postcss.config.js (or .cjs)
module.exports = {
  plugins: {
    // Use the require('@tailwindcss/postcss') syntax
    '@tailwindcss/postcss': {}, // This is often the fix for "tailwindcss directly as a PostCSS plugin"
    autoprefixer: {}, // Only if you also use autoprefixer
  },
};