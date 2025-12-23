/**
 * Глобальная функция для открытия формы записи из HTML кода
 * Использование в HTML редакторе:
 * 
 * Ссылка:
 * <a href="#" onclick="window.openBookingForm(1); return false;">Записаться</a>
 * 
 * Кнопка:
 * <button onclick="window.openBookingForm(1)">Записаться</button>
 * 
 * С формой и услугой:
 * <a href="#" onclick="window.openBookingForm(1, 'Название услуги', 5); return false;">Записаться</a>
 * 
 * Через URL параметры:
 * ?booking_form=1&service_id=5&service_title=Название
 */

declare global {
  interface Window {
    openBookingForm: (formId: number, serviceTitle?: string, serviceId?: number) => void;
  }
}

let bookingFormCallback: ((formId: number, serviceTitle?: string, serviceId?: number) => void) | null = null;

export function setBookingFormCallback(callback: (formId: number, serviceTitle?: string, serviceId?: number) => void) {
  bookingFormCallback = callback;
}

export function initGlobalBookingForm() {
  // Глобальная функция для вызова из HTML
  window.openBookingForm = (formId: number, serviceTitle?: string, serviceId?: number) => {
    if (bookingFormCallback) {
      bookingFormCallback(formId, serviceTitle || '', serviceId || null);
    } else {
      console.warn('BookingForm callback not set. Form will not open.');
    }
  };

  // Проверяем URL параметры при загрузке страницы
  if (typeof window !== 'undefined') {
    const urlParams = new URLSearchParams(window.location.search);
    const formIdParam = urlParams.get('booking_form');
    const serviceIdParam = urlParams.get('service_id');
    const serviceTitleParam = urlParams.get('service_title');

    if (formIdParam) {
      const formId = parseInt(formIdParam, 10);
      if (!isNaN(formId)) {
        // Небольшая задержка, чтобы компоненты успели загрузиться
        setTimeout(() => {
          const serviceId = serviceIdParam ? parseInt(serviceIdParam, 10) : undefined;
          const serviceTitle = serviceTitleParam ? decodeURIComponent(serviceTitleParam) : undefined;
          window.openBookingForm(formId, serviceTitle, serviceId);
        }, 500);
      }
    }
  }
}

