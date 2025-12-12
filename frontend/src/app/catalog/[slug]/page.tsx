import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import BookingForm from '@/components/BookingForm';
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

  return (
    <main style={{ 
      minHeight: '80vh',
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
              dangerouslySetInnerHTML={{ __html: item.description }}
            />
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

