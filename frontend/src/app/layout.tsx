import type { Metadata } from 'next'
import './globals.css'
import { contentApi } from '@/lib/api'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

// Metadata будет динамически генерироваться в generateMetadata
export async function generateMetadata(): Promise<Metadata> {
  try {
    const siteSettings = await contentApi.getSiteSettings().then(res => res.data).catch(() => null);
    
    // Если нет настроек, используем минимальные значения без упоминания логопедии
    if (!siteSettings) {
      return {
        title: 'Temis',
        description: 'Temis',
        icons: {
          icon: '/favicon.ico',
        },
        openGraph: {
          title: 'Temis',
          description: 'Temis',
          url: 'https://temis.ooo',
          siteName: 'Temis',
          type: 'website',
        },
        twitter: {
          card: 'summary',
          title: 'Temis',
          description: 'Temis',
        },
      };
    }
    
    const pageTitle = siteSettings.page_title || 'Temis';
    const description = siteSettings.description || 'Temis';
    const siteName = siteSettings.site_name || 'Temis';
    const siteUrl = 'https://temis.ooo';
    
    return {
      title: pageTitle,
      description: description,
      icons: {
        icon: siteSettings.favicon || '/favicon.ico',
      },
      openGraph: {
        title: pageTitle,
        description: description,
        url: siteUrl,
        siteName: siteName,
        type: 'website',
        images: siteSettings.favicon ? [
          {
            url: siteSettings.favicon.startsWith('http') 
              ? siteSettings.favicon 
              : `${siteUrl}${siteSettings.favicon.startsWith('/') ? '' : '/'}${siteSettings.favicon}`,
            width: 1200,
            height: 630,
            alt: siteName,
          }
        ] : undefined,
      },
      twitter: {
        card: 'summary',
        title: pageTitle,
        description: description,
        images: siteSettings.favicon ? [
          siteSettings.favicon.startsWith('http') 
            ? siteSettings.favicon 
            : `${siteUrl}${siteSettings.favicon.startsWith('/') ? '' : '/'}${siteSettings.favicon}`
        ] : undefined,
      },
    };
  } catch (error) {
    console.error('Error generating metadata:', error);
    // При ошибке возвращаем минимальные значения
    return {
      title: 'Temis',
      description: 'Temis',
      icons: {
        icon: '/favicon.ico',
      },
      openGraph: {
        title: 'Temis',
        description: 'Temis',
        url: 'https://temis.ooo',
        siteName: 'Temis',
        type: 'website',
      },
      twitter: {
        card: 'summary',
        title: 'Temis',
        description: 'Temis',
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

