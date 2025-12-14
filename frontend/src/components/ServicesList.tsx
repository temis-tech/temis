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
  filterByBranchId?: number | null;
}

export default function ServicesList({ 
  services, 
  title = 'Наши услуги',
  showTitle = true,
  className = '',
  filterByBranchId
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
      return price.toLocaleString('ru-RU');
    }
    if (price.min === price.max) {
      return price.min.toLocaleString('ru-RU');
    }
    return `${price.min.toLocaleString('ru-RU')} - ${price.max.toLocaleString('ru-RU')}`;
  };

  const getServicePrice = (service: Service, branchId?: number | null) => {
    if (branchId && service.service_branches) {
      const serviceBranch = service.service_branches.find(
        (sb: any) => sb.branch_id === branchId || (sb.branch && typeof sb.branch === 'object' && sb.branch.id === branchId)
      );
      if (serviceBranch) {
        // Используем final_price если есть, иначе price, иначе базовая цена услуги
        return serviceBranch.final_price || serviceBranch.price || service.price;
      }
    }
    // Если есть диапазон цен, показываем его
    if (service.price_range) {
      return service.price_range;
    }
    return service.price;
  };

  const getServicePriceWithAbonement = (service: Service, branchId?: number | null) => {
    if (branchId && service.service_branches) {
      const serviceBranch = service.service_branches.find(
        (sb: any) => sb.branch_id === branchId || (sb.branch && typeof sb.branch === 'object' && sb.branch.id === branchId)
      );
      if (serviceBranch) {
        // Используем final_price_with_abonement если есть, иначе price_with_abonement
        return serviceBranch.final_price_with_abonement || serviceBranch.price_with_abonement || service.price_with_abonement;
      }
    }
    return service.price_with_abonement;
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

          return (
            <div key={service.id} className={styles.card}>
              {service.image && (
                <div className={styles.imageWrapper}>
                  <Image
                    src={normalizeImageUrl(service.image)}
                    alt={service.title}
                    width={400}
                    height={250}
                    className={styles.image}
                    style={{ objectFit: 'cover', borderRadius: '8px' }}
                  />
                </div>
              )}
              <div className={styles.content}>
                <h3 className={styles.name}>{service.title}</h3>
                {service.short_description && (
                  <p className={styles.description}>{service.short_description}</p>
                )}
                {service.duration && (
                  <p className={styles.duration}>⏱️ {service.duration}</p>
                )}
                <div className={styles.priceContainer}>
                  {formattedPrice && (
                    <div className={styles.price}>
                      <span className={styles.priceLabel}>Цена:</span>
                      <span className={styles.priceValue}>{formattedPrice} ₽</span>
                    </div>
                  )}
                  {formattedPriceWithAbonement && (
                    <div className={styles.priceAbonement}>
                      <span className={styles.priceLabel}>По абонементу:</span>
                      <span className={styles.priceValue}>{formattedPriceWithAbonement} ₽</span>
                    </div>
                  )}
                </div>
                {service.has_own_page && service.url && (
                  <Link href={service.url} className={styles.link}>
                    Подробнее →
                  </Link>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
