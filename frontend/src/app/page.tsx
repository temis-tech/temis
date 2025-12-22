import Hero from '@/components/Hero';
import WelcomeBanners from '@/components/WelcomeBanners';
import ContentPage from '@/components/ContentPage';
import { contentApi } from '@/lib/api';
import { HomePageBlock } from '@/types';

// Отключаем статическую генерацию для главной страницы, чтобы меню обновлялось динамически
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function Home() {
  // Пытаемся найти главную страницу через конструктор
  // Если есть страница с типом 'home', используем её
  // Иначе показываем только Hero
  let homePage = null;
  let errorMessage = null;
  
  try {
    // Пробуем найти главную страницу по типу 'home'
    console.log('[Home Page] Attempting to load home page...');
    const response = await contentApi.getHomePage().catch((err) => {
      console.error('[Home Page] API Error:', err);
      console.error('[Home Page] Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText
      });
      errorMessage = err.response?.data || err.message || 'Unknown error';
      return null;
    });
    
    console.log('[Home Page] API Response:', {
      hasResponse: !!response,
      hasData: !!response?.data,
      status: response?.status
    });
    
    if (response?.data) {
      homePage = response.data;
      console.log('[Home Page] Home page loaded:', {
        title: homePage.title,
        page_type: homePage.page_type,
        is_active: homePage.is_active,
        blocks_count: homePage.home_blocks?.length || 0,
        blocks: homePage.home_blocks?.map((b: HomePageBlock) => ({
          id: b.id,
          is_active: b.is_active,
          has_content_page_data: !!b.content_page_data,
          content_page_type: b.content_page_data?.page_type,
          content_page_title: b.content_page_data?.title,
          has_description: !!b.content_page_data?.description,
          description_length: b.content_page_data?.description?.length || 0,
          has_faq_items: !!b.content_page_data?.faq_items,
          faq_items_count: b.content_page_data?.faq_items?.length || 0,
          faq_items: b.content_page_data?.faq_items,
          has_image: !!b.content_page_data?.image
        }))
      });
    } else {
      console.warn('[Home Page] Home page not found or empty response');
      console.warn('[Home Page] Response object:', response);
    }
  } catch (error: any) {
    console.error('[Home Page] Error loading home page:', error);
    console.error('[Home Page] Error stack:', error.stack);
    errorMessage = error.message || 'Unknown error';
  }

  const hasContent = homePage && homePage.page_type === 'home' && homePage.is_active;
  
  console.log('[Home Page] Final check:', {
    hasHomePage: !!homePage,
    pageType: homePage?.page_type,
    isActive: homePage?.is_active,
    hasContent: hasContent,
    errorMessage: errorMessage
  });
  
  if (!hasContent && errorMessage) {
    console.error('[Home Page] Content check failed:', {
      hasHomePage: !!homePage,
      pageType: homePage?.page_type,
      isActive: homePage?.is_active,
      error: errorMessage
    });
  }

  // Если бэкенд недоступен и нет данных, не показываем старый контент
  if (!homePage && errorMessage) {
    return (
      <main>
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h1>Temis</h1>
          <p>Сервис временно недоступен. Пожалуйста, попробуйте позже.</p>
        </div>
      </main>
    );
  }

  // Если нет активного контента, не показываем ничего
  if (!hasContent) {
    return (
      <main>
        <Hero />
        <WelcomeBanners />
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h1>Temis</h1>
          <p>Контент временно недоступен. Пожалуйста, попробуйте позже.</p>
        </div>
      </main>
    );
  }

  return (
    <main>
      <Hero />
      <WelcomeBanners />
      {/* Показываем ContentPage только если страница загружена и активна */}
      {homePage && hasContent && <ContentPage page={homePage} />}
      {/* Отладочная информация всегда видна в development */}
      {(process.env.NODE_ENV === 'development' || !hasContent) && (
        <div style={{ padding: '2rem', background: hasContent ? '#d4edda' : '#fff3cd', border: `1px solid ${hasContent ? '#28a745' : '#ffc107'}`, borderRadius: '4px', margin: '2rem', textAlign: 'left', fontFamily: 'monospace', fontSize: '0.9rem' }}>
          <strong>Отладка главной страницы:</strong>
          <br />
          <div style={{ marginTop: '1rem' }}>
            <strong>Статус:</strong> {hasContent ? '✓ Загружена и активна' : '✗ Не загружена или не активна'}
            <br />
            {homePage ? (
              <>
                <strong>Страница:</strong> {homePage.title}
                <br />
                <strong>Тип:</strong> {homePage.page_type}
                <br />
                <strong>Активна:</strong> {homePage.is_active ? 'Да' : 'НЕТ!'}
                <br />
                <strong>Блоков всего:</strong> {homePage.home_blocks?.length || 0}
                <br />
                <strong>Блоков активных:</strong> {homePage.home_blocks?.filter((b: HomePageBlock) => b.is_active).length || 0}
                <br />
                <strong>Детали блоков:</strong>
                <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                  {homePage.home_blocks?.map((b: HomePageBlock) => (
                    <li key={b.id}>
                      Блок #{b.id}: активен={b.is_active ? 'да' : 'НЕТ'}, 
                      тип={b.content_page_data?.page_type || 'нет данных'}, 
                      название={b.content_page_data?.title || 'нет'},
                      FAQ элементов={b.content_page_data?.faq_items?.length || 0}
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <>
                <strong>Страница не найдена</strong>
                <br />
                {errorMessage && <span>Ошибка: {JSON.stringify(errorMessage)}</span>}
              </>
            )}
          </div>
        </div>
      )}
    </main>
  );
}

