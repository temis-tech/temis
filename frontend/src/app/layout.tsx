import type { Metadata } from 'next'
import './globals.css'
import { contentApi } from '@/lib/api'

export const metadata: Metadata = {
  title: 'Логопедический центр "Радуга слов" - СПб',
  description: 'Детский логопед в Санкт-Петербурге. Занятия с опытным логопедом, запуск речи, постановка звуков.',
  icons: {
    icon: '/favicon.ico',
  },
}

// Отключаем кэширование для layout, чтобы настройки шапки всегда были актуальными
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Получаем настройки шапки для установки CSS переменной глобально
  const headerSettings = await contentApi.getHeaderSettings().then(res => res.data).catch(() => null);
  const headerHeight = headerSettings?.header_height || 140;
  const mobileHeaderHeight = Math.min(headerHeight * 0.85, 120);

  return (
    <html lang="ru" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://static.tildacdn.com" crossOrigin="anonymous" />
        <meta httpEquiv="Permissions-Policy" content="local-network-access=()" />
        <style dangerouslySetInnerHTML={{
          __html: `
            :root {
              --header-height: ${headerHeight}px !important;
            }
            @media (max-width: 768px) {
              :root {
                --header-height: ${mobileHeaderHeight}px !important;
              }
            }
          `
        }} />
      </head>
      <body suppressHydrationWarning>
        {children}
      </body>
    </html>
  )
}

