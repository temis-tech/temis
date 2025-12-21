/**
 * Константы для приложения
 */

// Пути API
export const API_PREFIX = '/api';
export const MEDIA_PATH = '/media';

// Получить API URL из переменных окружения
export function getApiUrl(): string {
  if (typeof window !== 'undefined') {
    // На клиенте используем переменную окружения
    return process.env.NEXT_PUBLIC_API_URL || 'https://api.dev.logoped-spb.pro/api';
  }
  // На сервере используем внутренний URL
  return process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'https://api.dev.logoped-spb.pro/api';
}

// Получить API домен из текущего окружения
export function getApiHost(): string {
  if (typeof window === 'undefined') {
    // На сервере используем дефолтный домен
    return 'api.dev.logoped-spb.pro';
  }

  const hostname = window.location.hostname;
  
  // Определяем домен API на основе текущего домена
  if (hostname.includes('dev.logoped-spb.pro')) {
    return 'api.dev.logoped-spb.pro';
  } else if (hostname.includes('logoped-spb.pro') && !hostname.includes('dev.')) {
    return 'api.logoped-spb.pro';
  } else if (hostname.includes('temis.estenomada.es')) {
    return 'api.temis.estenomada.es';
  }
  
  // Дефолтный домен
  return 'api.dev.logoped-spb.pro';
}

// Получить базовый URL для медиа файлов
export function getMediaBaseUrl(): string {
  const apiHost = getApiHost();
  return `https://${apiHost}${MEDIA_PATH}`;
}

// Маппинг доменов для определения правильного API домена
export const DOMAIN_MAPPING: Record<string, string> = {
  'dev.logoped-spb.pro': 'api.dev.logoped-spb.pro',
  'logoped-spb.pro': 'api.logoped-spb.pro',
  'temis.estenomada.es': 'api.temis.estenomada.es',
};

