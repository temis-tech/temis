'use client';

import { useState } from 'react';
import BookingForm from './BookingForm';

interface BookingFormWrapperProps {
  formId: number;
  serviceId: number;
  serviceTitle: string;
}

export default function BookingFormWrapper({ formId, serviceId, serviceTitle }: BookingFormWrapperProps) {
  const [isOpen, setIsOpen] = useState(true);

  if (!isOpen) {
    return null;
  }

  return (
    <BookingForm
      formId={formId}
      serviceId={serviceId}
      serviceTitle={serviceTitle}
      onClose={() => setIsOpen(false)}
    />
  );
}
