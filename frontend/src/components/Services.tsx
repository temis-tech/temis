'use client';

import { Service } from '@/types';
import styles from './Services.module.css';
import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';
import { normalizeImageUrl } from '@/lib/utils';
import BookingForm from './BookingForm';

interface ServicesProps {
  services: Service[];
}

export default function Services({ services }: ServicesProps) {
  const [bookingState, setBookingState] = useState<{ formId: number; serviceId: number; serviceTitle: string } | null>(null);

  return (
    <>
      <section className={styles.services} id="services">
        <div className={styles.container}>
          <h2 className={styles.title}>Программы занятий в центре логопедии</h2>
          <p className={styles.description}>
            Комплексно развиваем речь ребенка: учимся четко говорить, правильно строить фразы, 
            расширяем словарный запас и готовимся к школе.
          </p>
          <div className={styles.grid}>
            {services.map((service) => (
              <div key={service.id} className={styles.card}>
                <Link href={`/services/${service.slug}`} className={styles.cardLink}>
                  {service.image && (
                    <div className={styles.imageWrapper}>
                      <Image
                        src={normalizeImageUrl(service.image)}
                        alt={service.title}
                        width={400}
                        height={300}
                        className={styles.image}
                      />
                    </div>
                  )}
                  <h3 className={styles.cardTitle}>{service.title}</h3>
                  <p className={styles.cardDescription}>
                    {service.short_description || service.description.substring(0, 150)}...
                  </p>
                  <div className={styles.price}>
                    <span className={styles.priceMain}>{service.price} ₽</span>
                    {service.price_with_abonement && (
                      <span className={styles.priceAbonement}>
                        {service.price_with_abonement} ₽ по абонементу
                      </span>
                    )}
                    <span className={styles.duration}>/занятие {service.duration}</span>
                  </div>
                </Link>
                {service.show_booking_button && service.booking_form_id && (
                  <button
                    className={styles.bookingButton}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setBookingState({
                        formId: service.booking_form_id!,
                        serviceId: service.id,
                        serviceTitle: service.title
                      });
                    }}
                  >
                    Записаться
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {bookingState && (
        <BookingForm
          formId={bookingState.formId}
          serviceId={bookingState.serviceId}
          serviceTitle={bookingState.serviceTitle}
          onClose={() => setBookingState(null)}
        />
      )}
    </>
  );
}

