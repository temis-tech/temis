import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import { normalizeHtmlContent } from '@/lib/htmlUtils';
import BookingForm from '@/components/BookingForm';
import Gallery from '@/components/Gallery';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { CatalogItem, ContentPage } from '@/types';

export const revalidate = 0;

export default async function CatalogItemPage({ params }: { params: { slug: string } }) {
  let item: CatalogItem | null = null;
  
  try {
    const response = await contentApi.getCatalogItemBySlug(params.slug);
    item = response.data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      notFound();
    }
    console.error('Error loading catalog item:', error);
    notFound();
  }

  if (!item || !item.has_own_page) {
    notFound();
  }

  // Проверяем обязательные поля
  if (!item.title) {
    console.error('Catalog item missing title:', item);
    notFound();
  }

  // Безопасно обрабатываем gallery_page
  const galleryPage = item.gallery_page && typeof item.gallery_page === 'object' 
    ? item.gallery_page 
    : null;
  
  const galleryImages = galleryPage?.gallery_images && Array.isArray(galleryPage.gallery_images)
    ? galleryPage.gallery_images
    : [];

  return (
    <main style={{ 
      paddingLeft: '2rem',
      paddingRight: '2rem',
      paddingBottom: '2rem'
    }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ 
            textAlign: 'center', 
            fontSize: '2.5rem', 
            marginBottom: '2rem',
            color: '#FF820E',
            fontWeight: 600
          }}>
            {item.title || 'Элемент каталога'}
          </h1>
          
          {item.image && (
            <div style={{ 
              width: '100%', 
              maxWidth: '800px', 
              margin: '0 auto 2rem',
              borderRadius: '12px',
              overflow: 'hidden'
            }}>
              <Image
                src={normalizeImageUrl(item.image || '')}
                alt={item.title || 'Изображение'}
                width={800}
                height={600}
                style={{ width: '100%', height: 'auto', objectFit: 'cover' }}
              />
            </div>
          )}
          
          {item.description && (
            <div 
              style={{ 
                fontSize: '1.1rem',
                lineHeight: '1.7',
                color: '#666',
                marginBottom: '2rem'
              }}
              dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(item.description || '') }}
            />
          )}
          
          {/* Галерея, если выбрана страница галереи */}
          {galleryPage ? (
            galleryImages.length > 0 ? (
              <div style={{ marginBottom: '2rem' }}>
                {galleryPage.show_title !== false && (
                  <h2 style={{ 
                    fontSize: '2rem', 
                    marginBottom: '1.5rem',
                    color: '#FF820E',
                    fontWeight: 600,
                    textAlign: 'center'
                  }}>
                    {galleryPage.title || 'Галерея'}
                  </h2>
                )}
                <Gallery
                  images={galleryImages}
                  displayType={galleryPage.gallery_display_type || 'grid'}
                  enableFullscreen={galleryPage.gallery_enable_fullscreen !== false}
                />
              </div>
            ) : (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#999', marginBottom: '2rem' }}>
                Галерея &quot;{galleryPage.title || 'Галерея'}&quot; не содержит активных элементов. Добавьте изображения или видео в админке.
              </div>
            )
          ) : null}
          
          {item.button_type === 'booking' && item.button_booking_form_id && (
            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
              <BookingForm
                formId={item.button_booking_form_id}
                serviceId={0}
                serviceTitle={item.title}
                onClose={() => {}}
              />
            </div>
          )}
        </div>
      </main>
  );
}

