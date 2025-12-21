import { getApiHost, MEDIA_PATH } from '@/config/constants';

/**
 * Нормализует URL изображений, заменяя HTTP на HTTPS и localhost на правильный домен
 */
export function normalizeImageUrl(url: string | null | undefined): string {
  if (!url) return '';
  
  // Если URL уже относительный или начинается с /, возвращаем как есть
  if (url.startsWith('/')) {
    return url;
  }
  
  // Получаем правильный API домен из конфигурации
  const apiHost = getApiHost();
  
  // Заменяем localhost на правильный API домен
  url = url.replace(/https?:\/\/localhost:\d+/g, `https://${apiHost}`);
  url = url.replace(/https?:\/\/127\.0\.0\.1:\d+/g, `https://${apiHost}`);
  url = url.replace(/https?:\/\/0\.0\.0\.0:\d+/g, `https://${apiHost}`);
  
  // Если URL уже содержит правильный API домен, возвращаем как есть
  if (url.includes(apiHost)) {
    return url;
  }
  
  // Заменяем неправильные домены на правильный
  // Заменяем старые домены на api.temis.ooo
  const mediaPathEscaped = MEDIA_PATH.replace(/\//g, '\\/');
  url = url.replace(
    new RegExp(`https?://[^/]+\\.logoped-spb\\.pro(${mediaPathEscaped}/.*)`, 'g'),
    `https://${apiHost}$1`
  );
  // Заменяем любые другие домены с /media/ на правильный API домен
  url = url.replace(
    new RegExp(`https?://[^/]+(${mediaPathEscaped}/.*)`, 'g'),
    `https://${apiHost}$1`
  );
  
  // Если URL начинается с http://, заменяем на https://
  if (url.startsWith('http://')) {
    url = url.replace('http://', 'https://');
  }
  
  return url;
}

/**
 * Нормализует номер телефона, оставляя только цифры (для MoyKlass API)
 * MoyKlass требует формат: ^[0-9]{10,15}$
 * Поддерживает форматы:
 * - +79214209008 (11 цифр с +7)
 * - 89214209008 (11 цифр с 8)
 * - 9214209008 (10 цифр без кода страны)
 */
export function normalizePhone(phone: string | null | undefined): string {
  if (!phone) return '';
  // Удаляем все нецифровые символы
  let digits = phone.replace(/\D/g, '');
  
  // Если номер начинается с 8 и имеет 11 цифр, заменяем 8 на 7
  if (digits.startsWith('8') && digits.length === 11) {
    digits = '7' + digits.substring(1);
  }
  
  // Если введено 10 цифр (без кода страны), добавляем 7 в начало
  if (digits.length === 10) {
    digits = '7' + digits;
  }
  
  // Ограничиваем до 15 цифр (максимум для MoyKlass)
  if (digits.length > 15) {
    digits = digits.substring(0, 15);
  }
  
  return digits;
}

/**
 * Валидирует номер телефона в реальном времени
 * Поддерживает форматы:
 * - +79214209008 (11 цифр с +7)
 * - 89214209008 (11 цифр с 8)
 * - 9214209008 (10 цифр без кода страны)
 * @returns {string | null} Ошибка валидации или null, если валидно
 */
export function validatePhone(phone: string | null | undefined, isTyping: boolean = false): string | null {
  if (!phone || phone.trim() === '') {
    return null; // Пустое поле не валидируем (если поле обязательное, это проверит required)
  }
  
  // Проверяем наличие недопустимых символов (буквы и другие символы, кроме цифр, +, пробелов, скобок, дефисов)
  // Разрешаем только: цифры, +, пробелы, скобки (), дефисы -
  const allowedPattern = /^[\d+\s()\-]*$/;
  if (!allowedPattern.test(phone)) {
    return 'Номер телефона может содержать только цифры и символы: +, пробелы, скобки, дефисы';
  }
  
  // Удаляем все нецифровые символы для проверки
  const digits = phone.replace(/\D/g, '');
  
  // Если нет цифр вообще, но есть другие символы - ошибка
  if (digits.length === 0 && phone.trim().length > 0) {
    return 'Номер телефона должен содержать цифры';
  }
  
  // Если пользователь еще вводит номер (меньше 10 цифр), не показываем ошибку
  // Показываем ошибку только если номер явно некорректный
  if (digits.length === 0) {
    return null; // Пустое поле
  }
  
  // Если меньше 10 цифр и пользователь еще вводит, не показываем ошибку
  if (digits.length < 10 && isTyping) {
    return null; // Пользователь еще вводит
  }
  
  // Если меньше 10 цифр и пользователь закончил ввод (не isTyping), показываем ошибку
  if (digits.length < 10) {
    return 'Недостаточно цифр. Введите номер в формате: +7 (999) 123-45-67, 8 (999) 123-45-67 или 999 123-45-67';
  }
  
  // 10 цифр - это валидно (без кода страны)
  if (digits.length === 10) {
    return null;
  }
  
  // 11 цифр - проверяем формат
  if (digits.length === 11) {
    if (digits.startsWith('7') || digits.startsWith('8')) {
      return null; // Валидно
    }
    // Если 11 цифр, но не начинается с 7 или 8 - ошибка
    return 'Номер должен начинаться с 7 или 8';
  }
  
  // Больше 15 цифр - ошибка
  if (digits.length > 15) {
    return 'Слишком много цифр. Максимум 15 цифр';
  }
  
  // Между 11 и 15 цифр - может быть международный номер, разрешаем
  if (digits.length > 11 && digits.length <= 15) {
    return null; // Разрешаем международные номера
  }
  
  return null; // По умолчанию валидно
}

/**
 * Форматирует номер телефона для отображения (маска)
 * Поддерживает форматы: +79214209008, 89214209008, 9214209008
 * Формат отображения: +7 (999) 123-45-67 или 8 (999) 123-45-67
 */
export function formatPhone(phone: string | null | undefined): string {
  if (!phone) return '';
  
  // Удаляем все нецифровые символы
  const digits = phone.replace(/\D/g, '');
  
  if (digits.length === 0) return '';
  
  // Определяем формат номера
  let normalized = digits;
  let startsWith8 = false;
  
  // Если номер начинается с 8 и имеет 11 цифр, сохраняем это
  if (normalized.startsWith('8') && normalized.length === 11) {
    startsWith8 = true;
  }
  
  // Если номер имеет 10 цифр (без кода страны), не добавляем ничего - пользователь сам решит формат
  // Форматируем в зависимости от длины
  if (normalized.length === 10) {
    // 10 цифр - форматируем как 8 (999) 123-45-67
    const area = normalized.substring(0, 3);
    const part1 = normalized.substring(3, 6);
    const part2 = normalized.substring(6, 8);
    const part3 = normalized.substring(8, 10);
    return `8 (${area}) ${part1}-${part2}-${part3}`;
  } else if (normalized.length === 11) {
    // 11 цифр - проверяем, начинается ли с 8 или 7
    if (normalized.startsWith('8')) {
      // Формат: 8 (999) 123-45-67
      const area = normalized.substring(1, 4);
      const part1 = normalized.substring(4, 7);
      const part2 = normalized.substring(7, 9);
      const part3 = normalized.substring(9, 11);
      return `8 (${area}) ${part1}-${part2}-${part3}`;
    } else if (normalized.startsWith('7')) {
      // Формат: +7 (999) 123-45-67
      const area = normalized.substring(1, 4);
      const part1 = normalized.substring(4, 7);
      const part2 = normalized.substring(7, 9);
      const part3 = normalized.substring(9, 11);
      return `+7 (${area}) ${part1}-${part2}-${part3}`;
    } else {
      // Если не начинается с 7 или 8, форматируем как 8
      const area = normalized.substring(0, 3);
      const part1 = normalized.substring(3, 6);
      const part2 = normalized.substring(6, 8);
      const part3 = normalized.substring(8, 11);
      return `8 (${area}) ${part1}-${part2}-${part3}`;
    }
  } else if (normalized.length > 11) {
    // Больше 11 цифр - форматируем первые 11, остальные добавляем
    if (normalized.startsWith('7')) {
      const area = normalized.substring(1, 4);
      const part1 = normalized.substring(4, 7);
      const part2 = normalized.substring(7, 9);
      const part3 = normalized.substring(9, 11);
      return `+7 (${area}) ${part1}-${part2}-${part3}${normalized.substring(11)}`;
    } else if (normalized.startsWith('8')) {
      const area = normalized.substring(1, 4);
      const part1 = normalized.substring(4, 7);
      const part2 = normalized.substring(7, 9);
      const part3 = normalized.substring(9, 11);
      return `8 (${area}) ${part1}-${part2}-${part3}${normalized.substring(11)}`;
    }
  }
  
  // Если меньше 10 цифр, возвращаем как есть
  return normalized;
}

/**
 * Фильтрует ввод телефона - удаляет только недопустимые символы (буквы и спецсимволы)
 * НЕ форматирует номер, только очищает от недопустимых символов
 * Разрешает: цифры, +, пробелы, скобки (), дефисы -
 */
export function filterPhoneInput(value: string): string {
  // Разрешаем только: цифры, +, пробелы, скобки (), дефисы -
  // Удаляем все недопустимые символы (буквы и другие)
  return value.replace(/[^\d+\s()\-]/g, '');
}

