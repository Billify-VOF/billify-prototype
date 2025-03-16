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
    webpack: (config) => {
        // Tell webpack to ignore these binary modules
        config.resolve.alias.canvas = false;
        config.resolve.alias.encoding = false;
        
        return config;
    }
};

module.exports = nextConfig;