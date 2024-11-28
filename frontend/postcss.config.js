// postcss.config.js
// This configuration explicitly defines the plugins array in a way Next.js expects
const config = {
    plugins: [
      // Include Tailwind CSS first
      require('tailwindcss'),
      // Then include autoprefixer
      require('autoprefixer'),
    ],
  }
  
  // Export the configuration
  module.exports = config