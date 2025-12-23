import { contentApi } from '@/lib/api';
import ContentPage from '@/components/ContentPage';
import { notFound } from 'next/navigation';

// Отключаем статическую генерацию для динамических страниц
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function DynamicPage({ params }: { params: { slug: string } }) {
  try {
    console.log('Fetching page with slug:', params.slug);
    const response = await contentApi.getContentPageBySlug(params.slug);
    console.log('Response status:', response?.status);
    console.log('Response data:', JSON.stringify(response?.data || null).substring(0, 200));
    const page = response.data;
    
    if (!page) {
      console.log('Page is null/undefined');
      notFound();
    }
    
    if (!page.is_active) {
      console.log('Page is inactive:', page.is_active);
      notFound();
    }

    // Отладочный вывод для проверки значения show_title
    console.log('🔍 DEBUG show_title:', {
      value: page.show_title,
      type: typeof page.show_title,
      isTrue: page.show_title === true,
      isFalse: page.show_title === false,
      isUndefined: page.show_title === undefined,
      isNull: page.show_title === null,
      stringTrue: page.show_title === 'true',
      stringFalse: page.show_title === 'false',
      pageTitle: page.title,
      pageType: page.page_type
    });

    // Нормализуем значение show_title (на случай если приходит строка)
    const shouldShowTitle = page.show_title === true || page.show_title === 'true';

    return (
      <main>
        <div style={{ paddingTop: '2rem' }}>
          {/* Показываем заголовок для всех типов страниц (catalog, gallery, text, faq), только если show_title === true */}
          {/* Если show_title === false или undefined, заголовок не показываем */}
          {shouldShowTitle && page.title && (
            <h1 style={{ 
              textAlign: 'center', 
              fontSize: '2.5rem', 
              marginBottom: '2rem',
              color: '#FF820E',
              fontWeight: 600
            }}>
              {page.title}
            </h1>
          )}
          <ContentPage page={page} />
        </div>
      </main>
    );
  } catch (error: any) {
    if (error.response?.status === 404) {
      notFound();
    }
    console.error('Error loading content page:', error);
    notFound();
  }
}

