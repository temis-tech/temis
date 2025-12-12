import Hero from '@/components/Hero';
import WelcomeBanners from '@/components/WelcomeBanners';
import ContentPage from '@/components/ContentPage';
import { contentApi } from '@/lib/api';

// Отключаем статическую генерацию для главной страницы, чтобы меню обновлялось динамически
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function Home() {
  // Пытаемся найти главную страницу через конструктор
  // Если есть страница с типом 'home', используем её
  // Иначе показываем только Hero
  let homePage = null;
  try {
    // Пробуем найти страницу с slug 'home'
    const response = await contentApi.getContentPageBySlug('home').catch(() => null);
    if (response?.data) {
      homePage = response.data;
      console.log('Home page loaded:', {
        title: homePage.title,
        page_type: homePage.page_type,
        is_active: homePage.is_active,
        blocks_count: homePage.home_blocks?.length || 0
      });
    }
  } catch (error) {
    console.error('Error loading home page:', error);
  }

  const hasContent = homePage && homePage.page_type === 'home' && homePage.is_active;

  return (
    <main>
      <Hero />
      <WelcomeBanners />
      {hasContent ? (
        <ContentPage page={homePage} />
      ) : (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <p>Создайте главную страницу в админке через конструктор страниц</p>
          {homePage && (
            <p style={{ color: '#999', fontSize: '0.9rem', marginTop: '1rem' }}>
              Debug: page_type={homePage.page_type}, is_active={String(homePage.is_active)}
            </p>
          )}
        </div>
      )}
    </main>
  );
}

