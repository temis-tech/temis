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
    // Пробуем найти страницу с slug 'home'
    const response = await contentApi.getContentPageBySlug('home').catch((err) => {
      console.error('API Error:', err);
      errorMessage = err.response?.data || err.message || 'Unknown error';
      return null;
    });
    
    if (response?.data) {
      homePage = response.data;
      console.log('Home page loaded:', {
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
          has_image: !!b.content_page_data?.image
        }))
      });
    } else {
      console.warn('Home page not found or empty response');
    }
  } catch (error: any) {
    console.error('Error loading home page:', error);
    errorMessage = error.message || 'Unknown error';
  }

  const hasContent = homePage && homePage.page_type === 'home' && homePage.is_active;
  
  if (!hasContent && errorMessage) {
    console.error('Home page content check failed:', {
      hasHomePage: !!homePage,
      pageType: homePage?.page_type,
      isActive: homePage?.is_active,
      error: errorMessage
    });
  }

  return (
    <main>
      <Hero />
      <WelcomeBanners />
      {hasContent && <ContentPage page={homePage} />}
      {!hasContent && process.env.NODE_ENV === 'development' && (
        <div style={{ padding: '2rem', background: '#fff3cd', border: '1px solid #ffc107', borderRadius: '4px', margin: '2rem', textAlign: 'center' }}>
          <strong>Отладка:</strong> Главная страница не загружена или не активна.
          <br />
          {errorMessage && <span>Ошибка: {JSON.stringify(errorMessage)}</span>}
          <br />
          {homePage && (
            <span>
              Страница найдена: {homePage.title}, тип: {homePage.page_type}, активна: {homePage.is_active ? 'да' : 'нет'}
            </span>
          )}
        </div>
      )}
    </main>
  );
}

