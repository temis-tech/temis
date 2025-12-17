import { contentApi } from '@/lib/api';
import { notFound } from 'next/navigation';

export const revalidate = 0;

export default async function CatalogItemPage({ params }: { params: { slug: string } }) {
  const { slug } = params;
  
  let item;
  try {
    const response = await contentApi.getCatalogItemBySlug(slug);
    item = response.data;
  } catch (error) {
    console.error('API Error:', error);
    notFound();
  }

  if (!item || !item.has_own_page) {
    notFound();
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1>{item.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: item.description || '' }} />
      <hr />
      <pre>{JSON.stringify(item, null, 2)}</pre>
    </div>
  );
}
