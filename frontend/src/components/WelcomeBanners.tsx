'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { contentApi } from '@/lib/api';
import { WelcomeBanner, WelcomeBannerCard } from '@/types';
import { normalizeImageUrl } from '@/lib/utils';
import BookingForm from './BookingForm';
import { setBookingFormCallback, initGlobalBookingForm } from '@/lib/bookingForm';
import styles from './WelcomeBanners.module.css';

const WIDTH_MAP: Record<WelcomeBanner['content_width'], number> = {
  narrow: 600,
  medium: 800,
  wide: 1000,
  full: 1200,
};

export default function WelcomeBanners() {
  const [banners, setBanners] = useState<WelcomeBanner[]>([]);
  const [loading, setLoading] = useState(true);
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [selectedFormId, setSelectedFormId] = useState<number | null>(null);
  const [selectedServiceId, setSelectedServiceId] = useState<number | null>(null);
  const [selectedServiceTitle, setSelectedServiceTitle] = useState('');
  const [openModalBanner, setOpenModalBanner] = useState<WelcomeBanner | null>(null);
  const [closedBanners, setClosedBanners] = useState<Set<number>>(new Set());
  const [hasOpenedModal, setHasOpenedModal] = useState(false);
  const router = useRouter();

  useEffect(() => {
    contentApi
      .getWelcomeBanners()
      .then((response) => {
        // API возвращает объект с полем results (DRF pagination)
        const bannersData = response.data?.results || response.data || [];
        setBanners(bannersData);
      })
      .catch((error) => {
        console.error('Ошибка загрузки приветственных баннеров:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleBooking = (formId?: number, title?: string) => {
    if (!formId) return;
    setSelectedFormId(formId);
    setSelectedServiceTitle(title || '');
    setShowBookingForm(true);
  };

  // Регистрируем глобальную функцию для вызова формы из HTML
  useEffect(() => {
    setBookingFormCallback(handleBooking);
    initGlobalBookingForm();
  }, []);

  const handleCardClick = (card: WelcomeBannerCard) => {
    switch (card.button_type) {
      case 'booking':
        handleBooking(card.button_booking_form_id, card.title);
        break;
      case 'quiz':
        if (card.button_quiz_slug) {
          router.push(`/quizzes/${card.button_quiz_slug}`);
        }
        break;
      case 'link':
        if (card.button_url) {
          const isExternal = card.button_url.startsWith('http');
          if (isExternal) {
            window.open(card.button_url, '_blank', 'noopener,noreferrer');
          } else {
            router.push(card.button_url);
          }
        }
        break;
      default:
        break;
    }
  };

  const contentWidthStyle = (banner: WelcomeBanner) => {
    const maxWidth = WIDTH_MAP[banner.content_width] || WIDTH_MAP.full;
    return { maxWidth };
  };

  const visibleBanners = useMemo(() => {
    return banners.filter((banner) => {
      return banner.cards && banner.cards.length > 0;
    });
  }, [banners]);

  // Разделяем баннеры на секции и модальные
  const sectionBanners = visibleBanners.filter(b => b.display_type === 'section');
  const modalBanners = visibleBanners.filter(b => 
    b.display_type === 'modal' && !closedBanners.has(b.id)
  );

  // Автоматически открываем первый модальный баннер при загрузке (только один раз)
  useEffect(() => {
    if (!loading && !hasOpenedModal && modalBanners.length > 0 && !openModalBanner) {
      const firstModalBanner = modalBanners.find(b => !closedBanners.has(b.id));
      if (firstModalBanner) {
        setOpenModalBanner(firstModalBanner);
        setHasOpenedModal(true);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading]);

  // Блокируем скролл когда модальное окно открыто
  useEffect(() => {
    if (openModalBanner) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [openModalBanner]);

  const handleCloseModal = () => {
    if (openModalBanner) {
      const bannerId = openModalBanner.id;
      setClosedBanners(prev => new Set([...prev, bannerId]));
      setOpenModalBanner(null);
    }
  };

  if (loading || visibleBanners.length === 0) {
    return null;
  }

  const renderBannerContent = (banner: WelcomeBanner) => (
    <div
      className={styles.banner}
      style={{
        backgroundColor: banner.background_color,
        color: banner.text_color,
      }}
    >
      <div className={styles.bannerInner} style={contentWidthStyle(banner)}>
        {(banner.title || banner.subtitle) && (
          <div className={styles.bannerHeader}>
            {banner.title && <h2 className={styles.bannerTitle}>{banner.title}</h2>}
            {banner.subtitle && (
              <div
                className={styles.bannerSubtitle}
                dangerouslySetInnerHTML={{ __html: banner.subtitle }}
              />
            )}
          </div>
        )}

        <div
          className={styles.cards}
          style={{
            gridTemplateColumns: `repeat(${banner.cards.length}, minmax(200px, 1fr))`,
          }}
        >
          {banner.cards
            .filter((card) => {
              const isActive = card.is_active !== false && card.is_active !== undefined;
              return isActive;
            })
            .sort((a, b) => (a.order || 0) - (b.order || 0))
            .map((card) => (
              <article key={card.id} className={styles.card}>
                {card.image && (
                  <div className={styles.cardImageWrapper}>
                    <img
                      src={normalizeImageUrl(card.image)}
                      alt={card.title}
                      className={styles.cardImage}
                    />
                  </div>
                )}
                <div className={styles.cardContent}>
                  <h3 className={styles.cardTitle}>{card.title}</h3>
                  {card.description && (
                    <div
                      className={styles.cardDescription}
                      dangerouslySetInnerHTML={{ __html: card.description }}
                    />
                  )}
                  {card.button_type !== 'none' && (
                    <button
                      type="button"
                      className={styles.cardButton}
                      onClick={() => handleCardClick(card)}
                    >
                      {card.button_text || 'Подробнее'}
                    </button>
                  )}
                </div>
              </article>
            ))}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Секционные баннеры */}
      {sectionBanners.length > 0 && (
        <section className={styles.wrapper}>
          {sectionBanners.map((banner) => (
            <div key={banner.id}>
              {renderBannerContent(banner)}
            </div>
          ))}
        </section>
      )}

      {/* Модальные баннеры */}
      {openModalBanner && (
        <div
          className={styles.modalOverlay}
          style={{
            backdropFilter: openModalBanner.blur_background > 0 
              ? `blur(${openModalBanner.blur_background * 0.1}px)` 
              : 'none',
            WebkitBackdropFilter: openModalBanner.blur_background > 0 
              ? `blur(${openModalBanner.blur_background * 0.1}px)` 
              : 'none',
            backgroundColor: openModalBanner.blur_background > 0 
              ? `rgba(0, 0, 0, ${openModalBanner.blur_background * 0.003})` 
              : 'rgba(0, 0, 0, 0.5)',
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              handleCloseModal();
            }
          }}
        >
          <div className={styles.modalContent}>
            <button
              className={styles.modalClose}
              onClick={handleCloseModal}
              aria-label="Закрыть"
            >
              ×
            </button>
            {renderBannerContent(openModalBanner)}
          </div>
        </div>
      )}

      {/* Остальные модальные баннеры (если есть несколько) */}
      {modalBanners.length > 1 && modalBanners.slice(1).map((banner) => (
        <div key={banner.id} style={{ display: 'none' }}>
          {/* Резерв для будущего - можно добавить очередь модальных окон */}
        </div>
      ))}

      {/* Форма записи */}
      {showBookingForm && selectedFormId && (
        <BookingForm
          formId={selectedFormId}
          serviceId={0}
          serviceTitle={selectedServiceTitle}
          onClose={() => {
            setShowBookingForm(false);
            setSelectedFormId(null);
            setSelectedServiceId(null);
            setSelectedServiceTitle('');
          }}
        />
      )}
    </>
  );
}

