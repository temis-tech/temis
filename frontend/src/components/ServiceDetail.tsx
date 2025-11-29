'use client';

import { Service } from '@/types';
import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';
import { normalizeImageUrl } from '@/lib/utils';
import BookingForm from './BookingForm';
import styles from './ServiceDetail.module.css';

interface ServiceDetailProps {
  service: Service;
}

export default function ServiceDetail({ service }: ServiceDetailProps) {
  const [showBookingForm, setShowBookingForm] = useState(false);

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <Link href="/services" className={styles.backLink}>
          ← Назад к услугам
        </Link>
        
        {service.image && (
          <div className={styles.imageWrapper}>
            <Image
              src={normalizeImageUrl(service.image)}
              alt={service.title}
              width={800}
              height={500}
              className={styles.image}
            />
          </div>
        )}
        
        <h1 className={styles.title}>{service.title}</h1>
        
        <div className={styles.price}>
          <span className={styles.priceMain}>{service.price} ₽</span>
          {service.price_with_abonement && (
            <span className={styles.priceAbonement}>
              {service.price_with_abonement} ₽ по абонементу
            </span>
          )}
          <span className={styles.duration}>/занятие {service.duration}</span>
        </div>
        
        <div className={styles.description}>
          {service.description.split('\n').map((paragraph, i) => (
            <p key={i}>{paragraph}</p>
          ))}
        </div>
        
        {service.show_booking_button && service.booking_form_id && (
          <button 
            className={styles.bookingButton}
            onClick={() => setShowBookingForm(true)}
          >
            Записаться
          </button>
        )}
      </div>
      
      {showBookingForm && service.booking_form_id && (
        <BookingForm
          formId={service.booking_form_id}
          serviceId={service.id}
          serviceTitle={service.title}
          onClose={() => setShowBookingForm(false)}
        />
      )}
    </div>
  );
}

