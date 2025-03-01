/** @type {import('next').NextConfig} */
const nextConfig = {
    env: {
        NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
    },
    async rewrites() {
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
        return [
            {
                source: '/api/:path*',
                destination: `${backendUrl}/api/:path*`
            }
        ];
    },
    webpack: (config, { isServer }) => {
        // Exclude canvas.node from being processed
        config.module.rules.push({
          test: /\.node$/,
          use: 'node-loader',
        });

        if (!isServer) {
            // Don't attempt to load native modules on client-side
            config.resolve.fallback = {
                ...config.resolve.fallback,
                canvas: false,
            };
        }

        return config;
    },
};

module.exports = nextConfig;