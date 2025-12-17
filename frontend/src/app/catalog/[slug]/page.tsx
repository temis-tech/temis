import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import { normalizeHtmlContent } from '@/lib/htmlUtils';
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

  const imagePosition = item.image_position || 'top';
  const hasImage = !!item.image;

  return (
    <main style={{ 
      paddingLeft: '2rem',
      paddingRight: '2rem',
      paddingBottom: '2rem'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', paddingTop: '2rem' }}>
        <h1 style={{ 
          textAlign: 'center', 
          fontSize: '2.5rem', 
          marginBottom: '2rem',
          color: '#FF820E',
          fontWeight: 600
        }}>
          {item.title}
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
            <img
              src={normalizeImageUrl(item.image)}
              alt={item.title}
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
              <img
                src={normalizeImageUrl(item.image)}
                alt={item.title}
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
              <img
                src={normalizeImageUrl(item.image)}
                alt={item.title}
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
            <img
              src={normalizeImageUrl(item.image)}
              alt={item.title}
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
    </main>
  );
}
