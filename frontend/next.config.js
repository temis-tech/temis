const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  // Оптимизация CSS для уменьшения блокирующих запросов
  swcMinify: true,
  compress: true,
  poweredByHeader: false,
  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
    };
    
    // Оптимизация CSS модулей
    if (!isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          ...config.optimization.splitChunks,
          cacheGroups: {
            ...config.optimization.splitChunks?.cacheGroups,
            styles: {
              name: 'styles',
              test: /\.(css|scss|sass)$/,
              chunks: 'all',
              enforce: true,
            },
          },
        },
      };
    }
    
    return config;
  },
  images: {
    domains: ['api.temis.ooo'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'api.temis.ooo',
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
      // Оптимизация кэширования для CSS файлов
      {
        source: '/_next/static/css/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
}

module.exports = nextConfig

