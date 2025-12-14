import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import BookingFormWrapper from '@/components/BookingFormWrapper';

export const revalidate = 0;

interface Service {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description?: string;
  price: number;
  price_with_abonement?: number;
  duration: string;
  image?: string;
  image_align?: 'left' | 'right' | 'center' | 'full';
  image_size?: 'small' | 'medium' | 'large' | 'full';
  has_own_page?: boolean;
  url?: string | null;
  show_booking_button?: boolean;
  booking_form_id?: number;
}

export default async function ServicePage({ params }: { params: { slug: string } }) {
  let service: Service | null = null;
  
  try {
    const response = await contentApi.getServiceBySlug(params.slug);
    service = response.data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      notFound();
    }
    console.error('Error loading service:', error);
    notFound();
  }

  if (!service || !service.has_own_page) {
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
            {service.title}
          </h1>
          
          {service.image && (() => {
            const getImageSize = (size?: string) => {
              switch (size) {
                case 'small': return { width: 200, height: 150 }
                case 'medium': return { width: 400, height: 300 }
                case 'large': return { width: 600, height: 450 }
                case 'full': return { width: 1200, height: 600 }
                default: return { width: 400, height: 300 }
              }
            }

            const getImageStyle = (align?: string, size?: string): React.CSSProperties => {
              const imageSize = getImageSize(size)
              const baseStyle: React.CSSProperties = {
                borderRadius: '12px',
                overflow: 'hidden',
                marginBottom: '2rem'
              }

              if (size === 'full') {
                return {
                  ...baseStyle,
                  width: '100%',
                  margin: '0 auto 2rem'
                }
              }

              switch (align) {
                case 'left':
                  return {
                    ...baseStyle,
                    maxWidth: `${imageSize.width}px`,
                    float: 'left' as const,
                    marginRight: '2rem',
                    marginBottom: '1rem'
                  }
                case 'right':
                  return {
                    ...baseStyle,
                    maxWidth: `${imageSize.width}px`,
                    float: 'right' as const,
                    marginLeft: '2rem',
                    marginBottom: '1rem'
                  }
                case 'center':
                default:
                  return {
                    ...baseStyle,
                    maxWidth: `${imageSize.width}px`,
                    margin: '0 auto 2rem'
                  }
              }
            }

            const imageSize = getImageSize(service.image_size)
            const imageStyle = getImageStyle(service.image_align, service.image_size)

            return (
              <div style={imageStyle}>
                <Image
                  src={normalizeImageUrl(service.image)}
                  alt={service.title}
                  width={imageSize.width}
                  height={imageSize.height}
                  style={{ width: '100%', height: 'auto', objectFit: 'cover' }}
                />
              </div>
            )
          })()}
          
          <div style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1.5rem',
            marginBottom: '2rem'
          }}>
            {service.price && typeof service.price === 'number' && service.price > 0 && (
              <div style={{ 
                background: '#f5f5f5',
                padding: '1.5rem',
                borderRadius: '12px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Цена</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 600, color: '#FF820E' }}>
                  {service.price.toLocaleString('ru-RU')} ₽
                </div>
                {service.price_with_abonement && typeof service.price_with_abonement === 'number' && service.price_with_abonement < service.price && (
                  <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
                    По абонементу: {service.price_with_abonement.toLocaleString('ru-RU')} ₽
                  </div>
                )}
              </div>
            )}
            
            {service.duration && (
              <div style={{ 
                background: '#f5f5f5',
                padding: '1.5rem',
                borderRadius: '12px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>Длительность</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 600, color: '#333' }}>
                  {service.duration}
                </div>
              </div>
            )}
          </div>
          
          {service.short_description && (
            <div 
              style={{ 
                fontSize: '1.2rem',
                lineHeight: '1.7',
                color: '#333',
                marginBottom: '2rem',
                fontWeight: 500
              }}
            >
              {service.short_description}
            </div>
          )}
          
          {service.description && (
            <div 
              style={{ 
                fontSize: '1.1rem',
                lineHeight: '1.7',
                color: '#666',
                marginBottom: '2rem'
              }}
              dangerouslySetInnerHTML={{ __html: service.description }}
            />
          )}
          
          {service.show_booking_button && service.booking_form_id && (
            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
              <BookingFormWrapper
                formId={service.booking_form_id}
                serviceId={service.id}
                serviceTitle={service.title}
              />
            </div>
          )}
        </div>
      </main>
  );
}

