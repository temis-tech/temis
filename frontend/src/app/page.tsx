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
  try {
    // Пробуем найти страницу с slug 'home'
    const response = await contentApi.getContentPageBySlug('home').catch(() => null);
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
          content_page_type: b.content_page_data?.page_type
        }))
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
      {hasContent && <ContentPage page={homePage} />}
    </main>
  );
}

