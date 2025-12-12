'use client';

import { useState, useEffect } from 'react';
import { contentApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { normalizeImageUrl } from '@/lib/utils';
import BookingForm from './BookingForm';
import styles from './Hero.module.css';

interface HeroSettings {
  title: string;
  subtitle: string;
  button_text: string;
  button_url?: string;
  button_type?: 'link' | 'quiz' | 'booking';
  button_quiz_slug?: string | null;
  button_booking_form_id?: number | null;
  background_image?: string | null;
  background_color?: string;
  image_position?: string;
  image_vertical_align?: string;
  image_size?: string;
  image_scale?: number;
  show_overlay?: boolean;
  overlay_opacity?: number;
  text_align?: string;
  content_width?: 'narrow' | 'medium' | 'wide' | 'full' | 'custom';
  content_width_custom?: number | null;
  is_active?: boolean;
}

export default function Hero() {
  const [heroSettings, setHeroSettings] = useState<HeroSettings | null>(null);
  const [showBookingForm, setShowBookingForm] = useState(false);
  const router = useRouter();

  useEffect(() => {
    contentApi.getHeroSettings()
      .then(res => setHeroSettings(res.data))
      .catch(() => setHeroSettings(null));
  }, []);

  if (!heroSettings || !heroSettings.is_active) {
    return null;
  }

  const backgroundColor = heroSettings.background_color || '#FF820E';
  const imagePosition = heroSettings.image_position || 'right';
  const imageVerticalAlign = heroSettings.image_vertical_align || 'center';
  const imageSize = heroSettings.image_size || 'cover';
  const imageScale = heroSettings.image_scale ? parseFloat(heroSettings.image_scale.toString()) : 100;
  const showOverlay = heroSettings.show_overlay !== false; // по умолчанию true
  const overlayOpacity = heroSettings.overlay_opacity ? parseFloat(heroSettings.overlay_opacity.toString()) : 0.3;
  const textAlign = (heroSettings.text_align || 'left') as 'left' | 'center' | 'right';
  
  // Определяем ширину контента
  const getContentWidth = () => {
    const widthType = heroSettings.content_width || 'narrow';
    if (widthType === 'custom' && heroSettings.content_width_custom) {
      return `${heroSettings.content_width_custom}px`;
    }
    const widthMap: Record<string, string> = {
      'narrow': '600px',
      'medium': '800px',
      'wide': '1000px',
      'full': '1200px',
    };
    return widthMap[widthType] || '600px';
  };
  
  const containerStyle = {
    textAlign: textAlign,
    maxWidth: getContentWidth(),
  };
  
  // Комбинируем горизонтальное и вертикальное выравнивание для backgroundPosition
  const backgroundPosition = `${imagePosition} ${imageVerticalAlign}`;
  
  // Определяем transform-origin на основе позиции
  const getTransformOrigin = () => {
    const horizontal = imagePosition === 'left' ? 'left' : imagePosition === 'right' ? 'right' : 'center';
    const vertical = imageVerticalAlign === 'top' ? 'top' : imageVerticalAlign === 'bottom' ? 'bottom' : 'center';
    return `${horizontal} ${vertical}`;
  };
  
  // Масштабирование применяется через transform: scale() к элементу с background-image
  // На мобильных позиционирование будет переопределено через CSS
  const backgroundImageStyle = heroSettings.background_image ? {
    backgroundImage: `url(${normalizeImageUrl(heroSettings.background_image)})`,
    backgroundPosition: backgroundPosition,
    backgroundSize: imageSize,
    transform: imageScale !== 100 ? `scale(${imageScale / 100})` : 'none',
    transformOrigin: getTransformOrigin(),
  } : {};

  const handleButtonClick = (e: React.MouseEvent) => {
    e.preventDefault();
    const buttonType = heroSettings.button_type || 'link';

    if (buttonType === 'quiz' && heroSettings.button_quiz_slug) {
      // Переход на анкету
      router.push(`/quizzes/${heroSettings.button_quiz_slug}`);
    } else if (buttonType === 'booking' && heroSettings.button_booking_form_id) {
      // Открытие формы записи
      setShowBookingForm(true);
    } else {
      // Обычная ссылка
      if (heroSettings.button_url) {
        if (heroSettings.button_url.startsWith('#')) {
          // Якорная ссылка
          const element = document.querySelector(heroSettings.button_url);
          if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
          }
        } else {
          // Внешняя ссылка
          window.location.href = heroSettings.button_url;
        }
      }
    }
  };
  
  return (
    <>
      <section 
        className={styles.hero}
        style={{ backgroundColor }}
      >
        {/* На десктопе показываем как background */}
        {heroSettings.background_image && (
          <>
            <div 
              className={styles.backgroundImage}
              style={backgroundImageStyle}
              data-image-position={imagePosition}
            />
            {showOverlay && (
              <div 
                className={styles.overlay}
                style={{ opacity: overlayOpacity }}
              />
            )}
          </>
        )}
        <div className={styles.container} style={containerStyle}>
          <h1 
            className={styles.title}
            dangerouslySetInnerHTML={{ __html: heroSettings.title }}
          />
          <div 
            className={styles.subtitle}
            dangerouslySetInnerHTML={{ __html: heroSettings.subtitle }}
          />
          <button 
            onClick={handleButtonClick}
            className={styles.button}
            type="button"
          >
            {heroSettings.button_text}
          </button>
          
          {/* На мобильных показываем изображение под текстом и кнопкой */}
          {heroSettings.background_image && (
            <div className={styles.mobileImage}>
              <img 
                src={normalizeImageUrl(heroSettings.background_image)}
                alt=""
                className={styles.mobileImageImg}
              />
            </div>
          )}
        </div>
      </section>
      
      {showBookingForm && heroSettings.button_booking_form_id && (
        <BookingForm
          formId={heroSettings.button_booking_form_id}
          serviceId={0} // Для Hero нет конкретной услуги
          serviceTitle=""
          onClose={() => setShowBookingForm(false)}
        />
      )}
    </>
  );
}

