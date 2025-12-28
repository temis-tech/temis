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
    
    // Очищаем описание от HTML тегов, если они есть
    const cleanDescription = description.replace(/<[^>]*>/g, '').trim() || 'Temis';
    
    return {
      title: pageTitle,
      description: cleanDescription,
      icons: {
        icon: siteSettings.favicon || '/favicon.ico',
      },
      openGraph: {
        title: pageTitle,
        description: cleanDescription,
        url: siteUrl,
        siteName: siteName,
        type: 'website',
        locale: 'ru_RU',
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
        card: 'summary_large_image',
        title: pageTitle,
        description: cleanDescription,
        images: siteSettings.favicon ? [
          siteSettings.favicon.startsWith('http') 
            ? siteSettings.favicon 
            : `${siteUrl}${siteSettings.favicon.startsWith('/') ? '' : '/'}${siteSettings.favicon}`
        ] : undefined,
      },
      // Дополнительные мета-теги
      keywords: undefined, // Можно добавить поле keywords в SiteSettings если нужно
      authors: [{ name: siteName }],
      creator: siteName,
      publisher: siteName,
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
  // На мобильных используем полную высоту хедера или минимум 120px для достаточного отступа
  // Увеличиваем минимум, чтобы учесть возможные изменения высоты хедера на мобильных
  const mobileHeaderHeight = Math.max(headerHeight, 120);

  // Если не удалось загрузить настройки шапки, все равно показываем минимальный layout
  // но Header и Footer сами проверят наличие данных и вернут null при ошибках
  
  return (
    <html lang="ru" suppressHydrationWarning>
      <head>
        <meta httpEquiv="Permissions-Policy" content="local-network-access=()" />
        
        {/* Критический CSS inline для избежания блокировки рендеринга */}
        <style dangerouslySetInnerHTML={{
          __html: `
            /* Критические стили для предотвращения FOUC */
            * {
              box-sizing: border-box;
            }
            html, body {
              margin: 0;
              padding: 0;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
              -webkit-font-smoothing: antialiased;
              -moz-osx-font-smoothing: grayscale;
              font-size: 16px;
              color: #000;
              background-color: #fff;
            }
            :root {
              --header-height: ${headerHeight}px !important;
            }
            @media (max-width: 768px) {
              :root {
                --header-height: ${mobileHeaderHeight}px !important;
              }
            }
            main {
              padding-top: var(--header-height, 140px) !important;
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

