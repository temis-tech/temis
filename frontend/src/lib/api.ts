import axios from 'axios';

// В продакшене должен быть установлен NEXT_PUBLIC_API_URL
// На сервере (SSR) всегда используем переменную окружения
// На клиенте используем относительный путь через API routes
const getApiBaseUrl = () => {
  // На сервере (SSR) всегда используем переменную окружения
  // Это предотвратит запросы к localhost
  if (typeof window === 'undefined') {
    // Основной публичный адрес API, fallback на внутренний адрес (systemd backend слушает 127.0.0.1:8001)
    return process.env.NEXT_PUBLIC_API_URL 
      || process.env.INTERNAL_API_URL 
      || 'http://127.0.0.1:8001/api';
  }
  
  // На клиенте используем относительный путь через API routes
  // Это не вызовет запросы к localhost, так как запросы идут к Next.js API routes
  return '/api';
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Content API
export const contentApi = {
  // Контакты (используется в Footer)
  getContacts: () => api.get('/content/contacts/'),
  // Настройки сайта
  getMenu: () => api.get('/content/menu/'),
  getHeaderSettings: () => api.get('/content/settings/header/'),
  getHeroSettings: () => api.get('/content/settings/hero/'),
  getFooterSettings: () => api.get('/content/settings/footer/'),
  getPrivacyPolicies: () => api.get('/content/policies/'),
  getPrivacyPolicyBySlug: (slug: string) => api.get(`/content/policies/by-slug/${slug}/`),
  getWelcomeBanners: () => api.get('/content/banners/'),
  // Бронирование
  getBookingForm: (id: number) => api.get(`/booking/forms/${id}/`),
  submitBooking: (data: any) => api.post('/booking/submissions/', data),
  submitBookingWithQuiz: (data: any) => api.post('/booking/submissions/submit_with_quiz/', data),
  // Универсальные страницы контента (конструктор)
  getContentPageBySlug: (slug: string) => api.get(`/content/pages/by-slug/${slug}/`),
  // Элементы каталога
  getCatalogItemBySlug: (slug: string) => api.get(`/content/catalog-items/by-slug/${slug}/`),
  // Услуги
  getServiceBySlug: (slug: string) => api.get(`/content/services/by-slug/${slug}/`),
};

// Quizzes API
export const quizzesApi = {
  getQuizzes: () => api.get('/quizzes/quizzes/'),
  getQuizBySlug: (slug: string) => api.get(`/quizzes/quizzes/by-slug/${slug}/`),
  submitQuiz: (data: any) => {
    const { quiz, ...payload } = data;
    return api.post(`/quizzes/quizzes/${quiz}/submit/`, payload);
  },
  getSubmissions: () => api.get('/quizzes/submissions/'),
};

export default api;

