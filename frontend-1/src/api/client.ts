import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth endpoints
export const authAPI = {
  register: (data: { company_name: string; industry: string; email: string; password: string }) =>
    api.post('/auth/register/', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login/', data),
  logout: () => api.post('/auth/logout/'),
  refreshToken: (refresh: string) =>
    api.post('/auth/token/refresh/', { refresh }),
};

// Assessment endpoints
export const assessmentAPI = {
  getQuestions: () => api.get('/questions/'),
  submitAnswers: (answers: { question_id: number; value: number }[]) =>
    api.post('/submit/', { answers }),
  getResult: (id: number) => api.get(`/result/${id}/`),
  downloadPdf: (id: number) => api.get(`/result/${id}/pdf/`, { responseType: 'blob' }),
};

// Company endpoints
export const companyAPI = {
  getProfile: () => api.get('/company/profile/'),
  getHistory: () => api.get('/company/history/'),
};

export default api;