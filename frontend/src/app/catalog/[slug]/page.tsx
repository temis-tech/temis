import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import { normalizeHtmlContent } from '@/lib/htmlUtils';
import BookingForm from '@/components/BookingForm';
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
          {item.gallery_page && item.gallery_page.gallery_images && item.gallery_page.gallery_images.length > 0 && (
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
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '2rem'
              }}>
                {item.gallery_page.gallery_images.map((galleryImage) => (
                  <div key={galleryImage.id} style={{
                    background: 'white',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                    transition: 'transform 0.3s, box-shadow 0.3s'
                  }}>
                    <div style={{ width: '100%', height: '300px', position: 'relative', overflow: 'hidden' }}>
                      <Image
                        src={normalizeImageUrl(galleryImage.image)}
                        alt={galleryImage.description || 'Изображение галереи'}
                        fill
                        style={{ objectFit: 'cover' }}
                      />
                    </div>
                    {galleryImage.description && (
                      <div style={{ padding: '1rem' }}>
                        <div
                          style={{
                            fontSize: '0.95rem',
                            lineHeight: '1.6',
                            color: '#666'
                          }}
                          dangerouslySetInnerHTML={{ __html: normalizeHtmlContent(galleryImage.description) }}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
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

