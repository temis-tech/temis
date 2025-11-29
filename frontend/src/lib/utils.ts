/**
 * Нормализует URL изображений, заменяя HTTP на HTTPS и localhost на правильный домен
 */
export function normalizeImageUrl(url: string | null | undefined): string {
  if (!url) return '';
  
  // Если URL уже относительный или начинается с /, возвращаем как есть
  if (url.startsWith('/')) {
    return url;
  }
  
  // Дефолтный домен для продакшена
  const apiHost = 'api.rainbow-say.estenomada.es';
  
  // Заменяем localhost на правильный API домен
  url = url.replace(/https?:\/\/localhost:\d+/g, `https://${apiHost}`);
  url = url.replace(/https?:\/\/127\.0\.0\.1:\d+/g, `https://${apiHost}`);
  url = url.replace(/https?:\/\/0\.0\.0\.0:\d+/g, `https://${apiHost}`);
  
  // Если URL начинается с http://, заменяем на https://
  if (url.startsWith('http://')) {
    url = url.replace('http://', 'https://');
  }
  
  return url;
}

