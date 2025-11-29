import axios from 'axios';

// В продакшене должен быть установлен NEXT_PUBLIC_API_URL
// На сервере (SSR) всегда используем переменную окружения
// На клиенте используем относительный путь через API routes
const getApiBaseUrl = () => {
  // На сервере (SSR) всегда используем переменную окружения
  // Это предотвратит запросы к localhost
  if (typeof window === 'undefined') {
    // На сервере обязательно нужна переменная окружения
    return process.env.NEXT_PUBLIC_API_URL || '';
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
  getBranches: () => api.get('/content/branches/'),
  getServices: () => api.get('/content/services/'),
  getServiceBySlug: (slug: string) => api.get(`/content/services/by-slug/${slug}/`),
  getSpecialists: () => api.get('/content/specialists/'),
  getSpecialistsByBranch: (branchId: number) => api.get(`/content/specialists/by_branch/?branch_id=${branchId}`),
  getReviews: () => api.get('/content/reviews/'),
  getPromotions: () => api.get('/content/promotions/'),
  getPromotionBySlug: (slug: string) => api.get(`/content/promotions/by-slug/${slug}/`),
  getArticles: () => api.get('/content/articles/'),
  getArticleBySlug: (slug: string) => api.get(`/content/articles/by-slug/${slug}/`),
  getContacts: () => api.get('/content/contacts/'),
  getMenu: () => api.get('/content/menu/'),
  getHeaderSettings: () => api.get('/content/settings/header/'),
  getHeroSettings: () => api.get('/content/settings/hero/'),
  getFooterSettings: () => api.get('/content/settings/footer/'),
  getPrivacyPolicy: () => api.get('/content/privacy-policy/'),
  getBookingForm: (id: number) => api.get(`/booking/forms/${id}/`),
  submitBooking: (data: any) => api.post('/booking/submissions/', data),
  submitBookingWithQuiz: (data: any) => api.post('/booking/submissions/submit_with_quiz/', data),
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

