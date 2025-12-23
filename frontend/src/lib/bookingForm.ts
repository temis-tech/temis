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

let bookingFormCallbacks: Array<((formId: number, serviceTitle?: string, serviceId?: number) => void)> = [];
let urlParamsProcessed = false; // Флаг для предотвращения повторной обработки URL параметров

export function setBookingFormCallback(callback: (formId: number, serviceTitle?: string, serviceId?: number) => void) {
  // Добавляем callback в список, чтобы поддерживать несколько компонентов
  if (!bookingFormCallbacks.includes(callback)) {
    bookingFormCallbacks.push(callback);
  }
}

export function initGlobalBookingForm() {
  // Глобальная функция для вызова из HTML
  if (typeof window !== 'undefined' && !window.openBookingForm) {
    window.openBookingForm = (formId: number, serviceTitle?: string, serviceId?: number) => {
      console.log('🔍 window.openBookingForm вызвана:', { formId, serviceTitle, serviceId, callbacksCount: bookingFormCallbacks.length });
      
      // Вызываем callbacks по порядку, но останавливаемся после первого успешного вызова
      // Это предотвращает двойное открытие формы
      // ContentPage обычно регистрируется первым и является универсальным обработчиком
      let called = false;
      for (let i = 0; i < bookingFormCallbacks.length; i++) {
        const callback = bookingFormCallbacks[i];
        try {
          console.log(`🔍 Вызываем callback ${i + 1}/${bookingFormCallbacks.length}`);
          callback(formId, serviceTitle || '', serviceId ?? undefined);
          called = true;
          console.log(`✅ Callback ${i + 1} успешно вызван, останавливаемся`);
          break; // Останавливаемся после первого успешного вызова, чтобы форма не открывалась несколько раз
        } catch (e) {
          console.error(`❌ Ошибка в callback ${i + 1}:`, e);
          // Продолжаем пробовать другие callbacks при ошибке
        }
      }
      if (!called) {
        console.warn('⚠️ BookingForm callback not set. Form will not open. Form ID:', formId, 'Available callbacks:', bookingFormCallbacks.length);
      }
    };
  }

  // Проверяем URL параметры при загрузке страницы (только один раз)
  if (typeof window !== 'undefined' && !urlParamsProcessed) {
    urlParamsProcessed = true;
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
          if (window.openBookingForm) {
            window.openBookingForm(formId, serviceTitle, serviceId);
          }
        }, 500);
      }
    }
  }
}

