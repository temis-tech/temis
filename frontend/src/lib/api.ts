import axios from 'axios';

// В продакшене должен быть установлен NEXT_PUBLIC_API_URL
// На сервере (SSR) используем внутренний URL для прямых запросов к Django
// На клиенте используем прямой URL к api.temis.ooo
const getApiBaseUrl = () => {
  // На сервере (SSR) используем внутренний URL для прямых запросов к Django
  if (typeof window === 'undefined') {
    return process.env.INTERNAL_API_URL 
      || process.env.NEXT_PUBLIC_API_URL 
      || 'http://127.0.0.1:8001/api';
  }
  
  // На клиенте используем прямой URL к api.temis.ooo
  return process.env.NEXT_PUBLIC_API_URL || 'https://api.temis.ooo/api';
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
  // Филиалы
  getBranches: () => api.get('/content/branches/'),
  // Настройки сайта
  getMenu: () => api.get('/content/menu/'),
  getSiteSettings: () => api.get('/content/settings/site/'),
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
  getHomePage: () => api.get('/content/pages/home/'),
  // Элементы каталога
  getCatalogItemBySlug: (slug: string) => api.get(`/content/catalog-items/by-slug/${slug}/`),
  // Услуги
  getServiceBySlug: (slug: string) => api.get(`/content/services/by-slug/${slug}/`),
  getServices: (branchId?: number) => {
    const url = branchId 
      ? `/content/services/by-branch/${branchId}/`
      : '/content/services/';
    return api.get(url);
  },
  getBranchById: (id: number) => api.get(`/content/branches/${id}/`),
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

