'use client';

import { ContentPage as ContentPageType } from '@/types';
import { normalizeImageUrl } from '@/lib/utils';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import BookingForm from './BookingForm';
import styles from './ContentPage.module.css';

interface ContentPageProps {
  page: ContentPageType;
}

export default function ContentPage({ page }: ContentPageProps) {
  const router = useRouter();
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [bookingForm, setBookingForm] = useState<any>(null);
  const [bookingFormData, setBookingFormData] = useState<Record<string, any>>({});
  const [submittingBooking, setSubmittingBooking] = useState(false);

  const handleButtonClick = async (item: any) => {
    console.log('Button clicked:', item);
    if (item.button_type === 'booking' && item.button_booking_form_id) {
      console.log('Loading booking form:', item.button_booking_form_id);
      try {
        const { contentApi } = await import('@/lib/api');
        const formResponse = await contentApi.getBookingForm(item.button_booking_form_id);
        console.log('Booking form loaded:', formResponse.data);
        setBookingForm(formResponse.data);
        setBookingFormData({});
        setShowBookingForm(true);
        console.log('Show booking form set to true');
      } catch (error) {
        console.error('Error loading booking form:', error);
        alert('Ошибка загрузки формы записи');
      }
    } else if (item.button_type === 'quiz' && item.button_quiz_slug) {
      router.push(`/quizzes/${item.button_quiz_slug}`);
    } else if (item.button_type === 'external' && item.button_url) {
      window.open(item.button_url, '_blank');
    } else {
      console.log('Button type or data missing:', { button_type: item.button_type, button_booking_form_id: item.button_booking_form_id });
    }
  };

  const handleBookingFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bookingForm) return;
    
    setSubmittingBooking(true);
    try {
      const { contentApi } = await import('@/lib/api');
      await contentApi.submitBooking({
        form_id: bookingForm.id,
        data: bookingFormData,
      });
      
      alert(bookingForm.success_message || 'Спасибо! Мы свяжемся с вами в ближайшее время.');
      setShowBookingForm(false);
    } catch (error) {
      console.error('Error submitting booking form:', error);
      alert('Ошибка при отправке формы. Попробуйте еще раз.');
    } finally {
      setSubmittingBooking(false);
    }
  };

  const renderBookingField = (field: any) => {
    const value = bookingFormData[field.name] || '';
    
    switch (field.field_type) {
      case 'textarea':
        return (
          <textarea
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => setBookingFormData({ ...bookingFormData, [field.name]: e.target.value })}
            placeholder={field.placeholder}
            required={field.is_required}
            className={styles.input}
            rows={4}
          />
        );
      
      case 'select':
        const options = field.options?.split('\n').filter((o: string) => o.trim()) || [];
        return (
          <select
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => setBookingFormData({ ...bookingFormData, [field.name]: e.target.value })}
            required={field.is_required}
            className={styles.input}
          >
            <option value="">Выберите...</option>
            {options.map((opt: string, i: number) => (
              <option key={i} value={opt.trim()}>
                {opt.trim()}
              </option>
            ))}
          </select>
        );
      
      case 'checkbox':
        return (
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              name={field.name}
              checked={!!value}
              onChange={(e) => setBookingFormData({ ...bookingFormData, [field.name]: e.target.checked })}
              required={field.is_required}
            />
            <span>{field.help_text || field.label}</span>
          </label>
        );
      
      default:
        return (
          <input
            type={field.field_type}
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => setBookingFormData({ ...bookingFormData, [field.name]: e.target.value })}
            placeholder={field.placeholder}
            required={field.is_required}
            className={styles.input}
          />
        );
    }
  };

  if (page.page_type === 'catalog') {
    return (
      <div className={styles.container}>
        {page.description && (
          <div 
            className={styles.description}
            dangerouslySetInnerHTML={{ __html: page.description }}
          />
        )}
        <div className={styles.catalogGrid}>
          {page.catalog_items?.map((item) => (
            <div key={item.id} className={styles.catalogItem}>
              {item.image && (
                <div className={styles.imageWrapper}>
                  <Image
                    src={normalizeImageUrl(item.image)}
                    alt={item.title}
                    width={400}
                    height={300}
                    className={styles.image}
                  />
                </div>
              )}
              <h3 className={styles.itemTitle}>{item.title}</h3>
              {item.description && (
                <div 
                  className={styles.itemDescription}
                  dangerouslySetInnerHTML={{ __html: item.description }}
                />
              )}
              {item.button_type !== 'none' && (
                <button
                  type="button"
                  className={styles.button}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Catalog button clicked:', item);
                    handleButtonClick(item);
                  }}
                >
                  {item.button_text || 'Записаться'}
                </button>
              )}
            </div>
          ))}
        </div>
        
        {showBookingForm && bookingForm && (
          <div className={styles.modalOverlay} onClick={() => setShowBookingForm(false)}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <div className={styles.bookingForm}>
            <h3>{bookingForm.title}</h3>
            {bookingForm.description && <p className={styles.description}>{bookingForm.description}</p>}
            
            <form onSubmit={handleBookingFormSubmit} className={styles.form}>
              {bookingForm.fields
                .filter((f: any) => f.field_type !== 'hidden')
                .sort((a: any, b: any) => (a.order || 0) - (b.order || 0))
                .map((field: any) => (
                  <div key={field.id} className={styles.field}>
                    <label htmlFor={field.name} className={styles.label}>
                      {field.label}
                      {field.is_required && <span className={styles.required}>*</span>}
                    </label>
                    {renderBookingField(field)}
                    {field.help_text && field.field_type !== 'checkbox' && (
                      <div className={styles.helpText}>{field.help_text}</div>
                    )}
                  </div>
                ))}
              
              {bookingForm.fields
                .filter((f: any) => f.field_type === 'hidden')
                .map((field: any) => (
                  <div key={field.id}>{renderBookingField(field)}</div>
                ))}
              
              <div className={styles.actions}>
                <button type="submit" className={styles.submitButton} disabled={submittingBooking}>
                  {submittingBooking ? 'Отправка...' : bookingForm.submit_button_text}
                </button>
                <button type="button" onClick={() => setShowBookingForm(false)} className={styles.cancelButton}>
                  Отмена
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    );
  }

  if (page.page_type === 'gallery') {
    return (
      <div className={styles.container}>
        {page.description && (
          <div 
            className={styles.description}
            dangerouslySetInnerHTML={{ __html: page.description }}
          />
        )}
        <div className={styles.galleryGrid}>
          {page.gallery_images?.map((image) => (
            <div key={image.id} className={styles.galleryItem}>
              <div className={styles.imageWrapper}>
                <Image
                  src={normalizeImageUrl(image.image)}
                  alt={image.description || 'Изображение'}
                  width={600}
                  height={400}
                  className={styles.image}
                />
              </div>
              {image.description && (
                <p className={styles.imageDescription}>{image.description}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (page.page_type === 'home') {
    return (
      <div className={styles.container}>
        {page.description && (
          <div 
            className={styles.description}
            dangerouslySetInnerHTML={{ __html: page.description }}
          />
        )}
        {page.home_blocks?.filter(block => block.is_active).map((block) => {
          if (!block.content_page_data) return null;
          const contentPage = block.content_page_data;
          
          // Пропускаем блоки, которые ссылаются на страницы типа 'home' (чтобы избежать рекурсии)
          if (contentPage.page_type === 'home') return null;
          
          // Формируем стили для заголовка
          const titleStyles: React.CSSProperties = {
            textAlign: block.title_align || 'center',
            color: block.title_color || '#333333',
            fontWeight: block.title_bold ? 'bold' : 'normal',
            fontStyle: block.title_italic ? 'italic' : 'normal',
          };
          
          // Добавляем размер через класс
          const titleSizeClass = block.title_size ? styles[`titleSize_${block.title_size}`] : styles.titleSize_large;
          
          // Применяем дополнительные CSS стили
          if (block.title_custom_css) {
            // Парсим CSS строку и применяем к стилям
            const customStyles = block.title_custom_css.split(';').reduce((acc, rule) => {
              const [key, value] = rule.split(':').map(s => s.trim());
              if (key && value) {
                // Конвертируем kebab-case в camelCase
                const camelKey = key.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
                acc[camelKey] = value;
              }
              return acc;
            }, {} as Record<string, string>);
            Object.assign(titleStyles, customStyles);
          }
          
          // Определяем, какой тег использовать для заголовка
          const TitleTag = block.title_tag || 'h2';
          const displayTitle = block.title || contentPage.title;
          
          return (
            <div key={block.id} className={styles.homeBlock}>
              {block.show_title && displayTitle && (
                <TitleTag 
                  className={`${styles.blockTitle} ${titleSizeClass}`}
                  style={titleStyles}
                >
                  {displayTitle}
                </TitleTag>
              )}
              {/* Рендерим контент страницы напрямую, избегая рекурсии */}
              {contentPage.page_type === 'catalog' && (
                <div className={styles.catalogGrid}>
                  {contentPage.catalog_items?.map((item) => (
                    <div key={item.id} className={styles.catalogItem}>
                      {item.image && (
                        <div className={styles.imageWrapper}>
                          <Image
                            src={normalizeImageUrl(item.image)}
                            alt={item.title}
                            width={400}
                            height={300}
                            className={styles.image}
                          />
                        </div>
                      )}
                      <h3 className={styles.itemTitle}>{item.title}</h3>
                      {item.description && (
                        <div 
                          className={styles.itemDescription}
                          dangerouslySetInnerHTML={{ __html: item.description }}
                        />
                      )}
                      {item.button_type !== 'none' && (
                        <button
                          type="button"
                          className={styles.button}
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            console.log('Home block catalog button clicked:', item);
                            handleButtonClick(item);
                          }}
                        >
                          {item.button_text || 'Записаться'}
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
              {contentPage.page_type === 'gallery' && (
                <div className={styles.galleryGrid}>
                  {contentPage.gallery_images?.map((image) => (
                    <div key={image.id} className={styles.galleryItem}>
                      <div className={styles.imageWrapper}>
                        <Image
                          src={normalizeImageUrl(image.image)}
                          alt={image.description || 'Изображение'}
                          width={600}
                          height={400}
                          className={styles.image}
                        />
                      </div>
                      {image.description && (
                        <div 
                          className={styles.imageDescription}
                          dangerouslySetInnerHTML={{ __html: image.description }}
                        />
                      )}
                    </div>
                  ))}
                </div>
              )}
              {contentPage.page_type === 'text' && (
                <div className={styles.textContent}>
                  {contentPage.description && (
                    <div dangerouslySetInnerHTML={{ __html: contentPage.description }} />
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  return null;
}

