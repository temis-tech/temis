'use client';

import { useState } from 'react';
import BookingForm from './BookingForm';

interface BookingFormWrapperProps {
  formId: number;
  serviceId: number;
  serviceTitle: string;
  sourcePage?: string;
  buttonText?: string;
}

export default function BookingFormWrapper({ formId, serviceId, serviceTitle, sourcePage, buttonText = 'Записаться' }: BookingFormWrapperProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          padding: '1rem 2rem',
          fontSize: '1.1rem',
          fontWeight: 600,
          backgroundColor: '#FF820E',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          transition: 'background-color 0.2s ease'
        }}
        onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#e6730d'}
        onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#FF820E'}
      >
        {buttonText}
      </button>
    );
  }

  return (
    <BookingForm
      formId={formId}
      serviceId={serviceId}
      serviceTitle={serviceTitle}
      sourcePage={sourcePage}
      onClose={() => setIsOpen(false)}
    />
  );
}
