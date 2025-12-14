import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import { normalizeHtmlContent } from '@/lib/htmlUtils';
import BookingForm from '@/components/BookingForm';
import Gallery from '@/components/Gallery';
import GalleryDebug from '@/components/GalleryDebug';
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

  // Отладочная информация
  console.log('🔍 Catalog item full data:', {
    title: item.title,
    has_own_page: item.has_own_page,
    has_gallery_page: !!item.gallery_page,
    gallery_page: item.gallery_page ? {
      id: item.gallery_page.id,
      title: item.gallery_page.title,
      is_active: item.gallery_page.is_active,
      gallery_images_count: item.gallery_page.gallery_images?.length || 0,
      gallery_images: item.gallery_page.gallery_images?.map(img => ({
        id: img.id,
        content_type: img.content_type,
        has_image: !!img.image,
        has_video_url: !!img.video_url,
        has_video_file: !!img.video_file,
        has_video_embed_url: !!img.video_embed_url
      })),
      gallery_display_type: item.gallery_page.gallery_display_type,
      gallery_enable_fullscreen: item.gallery_page.gallery_enable_fullscreen
    } : null
  });

  return (
    <main style={{ 
      paddingLeft: '2rem',
      paddingRight: '2rem',
      paddingBottom: '2rem'
    }}>
        <GalleryDebug item={item} />
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ 
            textAlign: 'center', 
            fontSize: '2.5rem', 
            marginBottom: '2rem',
            color: '#FF820E',
            fontWeight: 600
          }}>
            {item.title}
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
                src={normalizeImageUrl(item.image)}
                alt={item.title}
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
              dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(item.description) }}
            />
          )}
          
          {/* Галерея, если выбрана страница галереи */}
          {item.gallery_page ? (
            item.gallery_page.gallery_images && item.gallery_page.gallery_images.length > 0 ? (
              <div style={{ marginBottom: '2rem' }}>
                <h2 style={{ 
                  fontSize: '2rem', 
                  marginBottom: '1.5rem',
                  color: '#FF820E',
                  fontWeight: 600,
                  textAlign: 'center'
                }}>
                  {item.gallery_page.title || 'Галерея'}
                </h2>
                <Gallery
                  images={item.gallery_page.gallery_images}
                  displayType={item.gallery_page.gallery_display_type || 'grid'}
                  enableFullscreen={item.gallery_page.gallery_enable_fullscreen !== false}
                />
              </div>
            ) : (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#999', marginBottom: '2rem' }}>
                Галерея &quot;{item.gallery_page.title || 'Галерея'}&quot; не содержит активных элементов. Добавьте изображения или видео в админке.
              </div>
            )
          ) : (
            <div style={{ padding: '1rem', textAlign: 'center', color: '#999', marginBottom: '2rem', fontSize: '0.9rem' }}>
              {/* Отладочное сообщение - можно убрать после проверки */}
              {process.env.NODE_ENV === 'development' && (
                <div style={{ padding: '0.5rem', background: '#f0f0f0', borderRadius: '4px', marginTop: '1rem' }}>
                  Debug: gallery_page = {item.gallery_page ? 'exists' : 'null'}
                </div>
              )}
            </div>
          )}
          
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

