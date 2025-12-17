import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import { normalizeHtmlContent } from '@/lib/htmlUtils';
import BookingForm from '@/components/BookingForm';
import Gallery from '@/components/Gallery';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { CatalogItem } from '@/types';

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

  // Позиция изображения по умолчанию
  const imagePosition = item.image_position || 'top';
  const hasImage = !!item.image;

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
          
          {/* Изображение сверху */}
          {hasImage && imagePosition === 'top' && (
            <div style={{ 
              width: '100%', 
              maxWidth: item.image_target_width ? `${item.image_target_width}px` : '800px',
              margin: '0 auto 2rem',
              borderRadius: '12px',
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#f5f5f5',
              height: item.image_target_height ? `${item.image_target_height}px` : 'auto',
              minHeight: item.image_target_height ? `${item.image_target_height}px` : (item.image_target_width ? 'auto' : '400px')
            }}>
              <Image
                src={normalizeImageUrl(item.image)}
                alt={item.title || 'Изображение'}
                width={item.image_target_width || 800}
                height={item.image_target_height || 600}
                style={{ 
                  width: item.image_target_width ? `${item.image_target_width}px` : '100%',
                  height: item.image_target_height ? `${item.image_target_height}px` : 'auto',
                  maxWidth: '100%',
                  maxHeight: '100%',
                  objectFit: 'contain',
                  objectPosition: 'center'
                }}
              />
            </div>
          )}
          
          {/* Контейнер для бокового расположения */}
          <div style={{ 
            display: hasImage && (imagePosition === 'left' || imagePosition === 'right') ? 'flex' : 'block',
            flexDirection: hasImage && imagePosition === 'left' ? 'row' : imagePosition === 'right' ? 'row-reverse' : 'column',
            gap: hasImage && (imagePosition === 'left' || imagePosition === 'right') ? '2rem' : '0',
            alignItems: hasImage && (imagePosition === 'left' || imagePosition === 'right') ? 'flex-start' : 'stretch'
          }}>
            {/* Изображение слева */}
            {hasImage && imagePosition === 'left' && (
              <div style={{ 
                flexShrink: 0,
                width: item.image_target_width ? `${item.image_target_width}px` : '400px',
                height: item.image_target_height ? `${item.image_target_height}px` : 'auto',
                minHeight: item.image_target_height ? `${item.image_target_height}px` : (item.image_target_width ? 'auto' : '300px'),
                borderRadius: '12px',
                overflow: 'hidden',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#f5f5f5'
              }}>
                <Image
                  src={normalizeImageUrl(item.image)}
                  alt={item.title || 'Изображение'}
                  width={item.image_target_width || 400}
                  height={item.image_target_height || 300}
                  style={{ 
                    width: item.image_target_width ? `${item.image_target_width}px` : '100%',
                    height: item.image_target_height ? `${item.image_target_height}px` : 'auto',
                    maxWidth: '100%',
                    maxHeight: '100%',
                    objectFit: 'contain',
                    objectPosition: 'center'
                  }}
                />
              </div>
            )}
            
            {/* Описание */}
            {item.description && (
              <div 
                style={{ 
                  fontSize: '1.1rem',
                  lineHeight: '1.7',
                  color: '#666',
                  marginBottom: '2rem',
                  flex: hasImage && (imagePosition === 'left' || imagePosition === 'right') ? '1' : 'none'
                }}
                dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(item.description) }}
              />
            )}
            
            {/* Изображение справа */}
            {hasImage && imagePosition === 'right' && (
              <div style={{ 
                flexShrink: 0,
                width: item.image_target_width ? `${item.image_target_width}px` : '400px',
                height: item.image_target_height ? `${item.image_target_height}px` : 'auto',
                minHeight: item.image_target_height ? `${item.image_target_height}px` : (item.image_target_width ? 'auto' : '300px'),
                borderRadius: '12px',
                overflow: 'hidden',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#f5f5f5'
              }}>
                <Image
                  src={normalizeImageUrl(item.image)}
                  alt={item.title || 'Изображение'}
                  width={item.image_target_width || 400}
                  height={item.image_target_height || 300}
                  style={{ 
                    width: item.image_target_width ? `${item.image_target_width}px` : '100%',
                    height: item.image_target_height ? `${item.image_target_height}px` : 'auto',
                    maxWidth: '100%',
                    maxHeight: '100%',
                    objectFit: 'contain',
                    objectPosition: 'center'
                  }}
                />
              </div>
            )}
          </div>
          
          {/* Изображение снизу */}
          {hasImage && imagePosition === 'bottom' && (
            <div style={{ 
              width: '100%', 
              maxWidth: item.image_target_width ? `${item.image_target_width}px` : '800px',
              margin: '2rem auto 0',
              borderRadius: '12px',
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#f5f5f5',
              height: item.image_target_height ? `${item.image_target_height}px` : 'auto',
              minHeight: item.image_target_height ? `${item.image_target_height}px` : (item.image_target_width ? 'auto' : '400px')
            }}>
              <Image
                src={normalizeImageUrl(item.image)}
                alt={item.title || 'Изображение'}
                width={item.image_target_width || 800}
                height={item.image_target_height || 600}
                style={{ 
                  width: item.image_target_width ? `${item.image_target_width}px` : '100%',
                  height: item.image_target_height ? `${item.image_target_height}px` : 'auto',
                  maxWidth: '100%',
                  maxHeight: '100%',
                  objectFit: 'contain',
                  objectPosition: 'center'
                }}
              />
            </div>
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
          
          {item.button_type === 'booking' && item.button_booking_form_id && typeof item.button_booking_form_id === 'number' && (
            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
              <BookingForm
                formId={item.button_booking_form_id}
                serviceId={0}
                serviceTitle={item.title || ''}
                onClose={() => {}}
              />
            </div>
          )}
        </div>
    </main>
  );
}
