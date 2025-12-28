'use client';

import { Service } from '@/types';
import { normalizeImageUrl } from '@/lib/utils';
import Image from 'next/image';
import Link from 'next/link';
import styles from './ServicesList.module.css';

interface ServicesListProps {
  services: Service[];
  title?: string;
  showTitle?: boolean;
  className?: string;
  cardStyle?: 'standard' | 'compact' | 'detailed' | 'minimal';
  cardWidth?: number;
  cardHeight?: number;
  filterByBranchId?: number | null;
  onBookingClick?: (formId: number, serviceTitle: string, serviceId: number) => void;
}

export default function ServicesList({ 
  services, 
  title = 'Наши услуги',
  showTitle = true,
  className = '',
  cardStyle = 'standard',
  cardWidth,
  cardHeight,
  filterByBranchId,
  onBookingClick
}: ServicesListProps) {
  if (!services || services.length === 0) {
    return null;
  }

  // Фильтруем услуги по филиалу, если указан filterByBranchId
  let filteredServices = services;
  if (filterByBranchId) {
    filteredServices = services.filter(service => {
      if (!service.service_branches || !Array.isArray(service.service_branches)) {
        return false;
      }
      return service.service_branches.some(
        (sb: any) => (sb.branch_id === filterByBranchId || (sb.branch && typeof sb.branch === 'object' && sb.branch.id === filterByBranchId)) && sb.is_available !== false
      );
    });
  }

  if (filteredServices.length === 0) {
    return null;
  }

  const formatPrice = (price: number | { min: number; max: number } | null | undefined) => {
    if (!price) return null;
    if (typeof price === 'number') {
      if (isNaN(price) || price === null || price === undefined) return null;
      return price.toLocaleString('ru-RU');
    }
    if (typeof price === 'object' && 'min' in price && 'max' in price) {
      const min = price.min;
      const max = price.max;
      if (min === undefined || max === undefined || isNaN(min) || isNaN(max)) return null;
      if (min === max) {
        return min.toLocaleString('ru-RU');
      }
      return `${min.toLocaleString('ru-RU')} - ${max.toLocaleString('ru-RU')}`;
    }
    return null;
  };

  const getServicePrice = (service: Service, branchId?: number | null): number | { min: number; max: number } | null => {
    if (branchId && service.service_branches && Array.isArray(service.service_branches)) {
      const serviceBranch = service.service_branches.find(
        (sb: any) => sb.branch_id === branchId || (sb.branch && typeof sb.branch === 'object' && sb.branch.id === branchId)
      );
      if (serviceBranch) {
        // Используем final_price если есть, иначе price, иначе базовая цена услуги
        const price = serviceBranch.final_price ?? serviceBranch.price ?? service.price;
        if (price !== null && price !== undefined && !isNaN(Number(price))) {
          return Number(price);
        }
      }
    }
    // Если есть диапазон цен, показываем его
    if (service.price_range) {
      if (typeof service.price_range === 'object' && 'min' in service.price_range && 'max' in service.price_range) {
        return service.price_range;
      }
      if (typeof service.price_range === 'number' && !isNaN(service.price_range)) {
        return service.price_range;
      }
    }
    // Возвращаем базовую цену, если она валидна
    if (service.price !== null && service.price !== undefined && !isNaN(Number(service.price))) {
      return Number(service.price);
    }
    return null;
  };

  const getServicePriceWithAbonement = (service: Service, branchId?: number | null): number | null => {
    if (branchId && service.service_branches && Array.isArray(service.service_branches)) {
      const serviceBranch = service.service_branches.find(
        (sb: any) => sb.branch_id === branchId || (sb.branch && typeof sb.branch === 'object' && sb.branch.id === branchId)
      );
      if (serviceBranch) {
        // Используем final_price_with_abonement если есть, иначе price_with_abonement
        const price = serviceBranch.final_price_with_abonement ?? serviceBranch.price_with_abonement ?? service.price_with_abonement;
        if (price !== null && price !== undefined && !isNaN(Number(price))) {
          return Number(price);
        }
      }
    }
    // Возвращаем базовую цену по абонементу, если она валидна
    if (service.price_with_abonement !== null && service.price_with_abonement !== undefined && !isNaN(Number(service.price_with_abonement))) {
      return Number(service.price_with_abonement);
    }
    return null;
  };

  return (
    <div className={`${styles.container} ${className}`}>
      {showTitle && title && (
        <h2 className={styles.title}>{title}</h2>
      )}
      <div className={styles.grid}>
        {filteredServices.map((service) => {
          const price = getServicePrice(service, filterByBranchId);
          const priceWithAbonement = getServicePriceWithAbonement(service, filterByBranchId);
          const formattedPrice = formatPrice(price);
          const formattedPriceWithAbonement = priceWithAbonement ? formatPrice(priceWithAbonement) : null;

          const cardClassName = `${styles.card} ${styles[`card_${cardStyle}`] || ''}`;
          
          // Применяем размеры карточки, если они указаны
          const cardStyleProps: React.CSSProperties = {};
          if (cardWidth && cardStyle !== 'minimal') {
            cardStyleProps.width = `${cardWidth}px`;
          }
          if (cardHeight) {
            cardStyleProps.height = `${cardHeight}px`;
          }
          
          return (
            <div key={service.id} className={cardClassName} style={cardStyleProps}>
              {service.image && cardStyle === 'minimal' && (
                <div className={styles.imageWrapperMinimal}>
                  <Image
                    src={normalizeImageUrl(service.image)}
                    alt={service.title}
                    width={80}
                    height={80}
                    className={styles.imageMinimal}
                    style={{ objectFit: 'contain', objectPosition: 'center', borderRadius: '8px' }}
                  />
                </div>
              )}
              {service.image && cardStyle !== 'minimal' && (
                <div className={styles.imageWrapper}>
                  <Image
                    src={normalizeImageUrl(service.image)}
                    alt={service.title}
                    width={400}
                    height={250}
                    className={styles.image}
                    style={{ objectFit: 'cover', objectPosition: 'center', borderRadius: '8px' }}
                  />
                </div>
              )}
              <div className={styles.content}>
                <h3 className={styles.name}>{service.title}</h3>
                {cardStyle === 'minimal' && service.card_short_description ? (
                  <div className={styles.description} dangerouslySetInnerHTML={{ __html: service.card_short_description }} />
                ) : service.card_short_description && cardStyle !== 'compact' && cardStyle !== 'minimal' ? (
                  <div className={styles.description} dangerouslySetInnerHTML={{ __html: service.card_short_description }} />
                ) : null}
                {(formattedPrice || formattedPriceWithAbonement) && (
                  <div className={styles.priceContainer}>
                    {formattedPrice && (
                      <div className={styles.price}>
                        <span className={styles.priceLabel}>Цена:</span>
                        <span className={styles.priceValue}>
                          {service.price_is_from ? 'От ' : ''}{formattedPrice} ₽
                        </span>
                      </div>
                    )}
                    {formattedPriceWithAbonement && cardStyle === 'detailed' && (
                      <div className={styles.priceAbonement}>
                        <span className={styles.priceLabel}>По абонементу:</span>
                        <span className={styles.priceValue}>
                          {service.price_with_abonement_is_from ? 'От ' : ''}{formattedPriceWithAbonement} ₽
                        </span>
                      </div>
                    )}
                  </div>
                )}
                {(service.show_booking_button && service.booking_form_id && onBookingClick) || (service.has_own_page && service.url) ? (
                  <div className={styles.buttonsContainer}>
                    {service.show_booking_button && service.booking_form_id && onBookingClick && (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          onBookingClick(service.booking_form_id!, service.title, service.id);
                        }}
                        className={styles.bookingButton}
                      >
                        Записаться
                      </button>
                    )}
                    {service.has_own_page && service.url && cardStyle !== 'minimal' && (
                      <Link href={service.url} className={styles.link}>
                        Подробнее
                      </Link>
                    )}
                  </div>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
