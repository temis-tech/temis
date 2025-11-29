/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  images: {
    domains: ['api.rainbow-say.estenomada.es'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'api.rainbow-say.estenomada.es',
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

