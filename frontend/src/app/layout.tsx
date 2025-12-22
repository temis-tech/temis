import type { Metadata } from 'next'
import './globals.css'
import { contentApi } from '@/lib/api'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

// Metadata будет динамически генерироваться в generateMetadata
export async function generateMetadata(): Promise<Metadata> {
  try {
    const siteSettings = await contentApi.getSiteSettings().then(res => res.data).catch(() => null);
    const siteName = siteSettings?.site_name || 'Temis';
    const pageTitle = siteSettings?.page_title || 'Temis';
    
    return {
      title: pageTitle,
      description: siteSettings?.description || 'Temis',
      icons: {
        icon: siteSettings?.favicon || '/favicon.ico',
      },
    };
  } catch {
    return {
      title: 'Temis',
      description: 'Temis',
      icons: {
        icon: '/favicon.ico',
      },
    };
  }
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
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  )
}

