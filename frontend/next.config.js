const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
    };
    return config;
  },
  images: {
    domains: ['api.temis.ooo', 'api.dev.logoped-spb.pro'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'api.temis.ooo',
        pathname: '/media/**',
      },
      {
        protocol: 'https',
        hostname: 'api.dev.logoped-spb.pro',
        pathname: '/media/**',
      },
    ],
    unoptimized: false,
    // Отключаем внутренние запросы к локальной сети
    minimumCacheTTL: 60,
  },
  // Отключаем внутренние запросы к localhost
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  // Убеждаемся, что Next.js не делает запросы к localhost
  async rewrites() {
    return [];
  },
  // Отключаем автоматическое определение локального IP
  // Это предотвратит запросы браузера к локальной сети
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Permissions-Policy',
            value: 'local-network-access=()',
          },
        ],
      },
    ];
  },
}

module.exports = nextConfig

