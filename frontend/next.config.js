/** @type {import('next').NextConfig} */
const nextConfig = {
    env: {
        NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000',
    },

    webpack: (config) => {
        config.resolve.alias.canvas = false;
        config.resolve.alias.encoding = false;

        return config;
    },
    eslint: {
        dirs: ['.'], // Specify directories to lint
    },
    experimental: {
        esmExternals: true,
    },
};

module.exports = nextConfig;