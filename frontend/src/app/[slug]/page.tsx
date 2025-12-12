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

    return (
      <main>
        <div style={{ paddingTop: '2rem' }}>
          <h1 style={{ 
            textAlign: 'center', 
            fontSize: '2.5rem', 
            marginBottom: '2rem',
            color: '#FF820E',
            fontWeight: 600
          }}>
            {page.title}
          </h1>
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

