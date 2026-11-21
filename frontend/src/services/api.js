const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
  }

  const response = await fetch(url, config);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data.detail || data.message || `API Error ${response.status}`;
    throw new Error(errorMsg);
  }

  return data;
}

export const api = {
  // Dashboard
  getDashboard: () => request('/dashboard/'),

  // AI Providers
  getAIProviders: () => request('/providers/'),
  createAIProvider: (data) => request('/providers/', { method: 'POST', body: data }),
  updateAIProvider: (id, data) => request(`/providers/${id}`, { method: 'PUT', body: data }),
  testAIProvider: (id) => request(`/providers/${id}/test`, { method: 'POST' }),
  setDefaultAIProvider: (id) => request(`/providers/${id}/set-default`, { method: 'POST' }),
  setFallbackAIProvider: (id) => request(`/providers/${id}/set-fallback`, { method: 'POST' }),
  deleteAIProvider: (id) => request(`/providers/${id}`, { method: 'DELETE' }),

  // Image Providers
  getImageProviders: () => request('/providers/image/list'),
  updateImageProvider: (id, data) => request(`/providers/image/${id}`, { method: 'PUT', body: data }),
  testImageProvider: (id) => request(`/providers/image/${id}/test`, { method: 'POST' }),
  setDefaultImageProvider: (id) => request(`/providers/image/${id}/set-default`, { method: 'POST' }),

  // Facebook
  getFacebookStatus: () => request('/facebook/status'),
  saveFacebookConfig: (data) => request('/facebook/save-config', { method: 'POST', body: data }),
  fetchManagedPages: (userToken) => request('/facebook/fetch-pages', { method: 'POST', body: { user_access_token: userToken } }),
  testFacebookPublish: (data) => request('/facebook/test-publish', { method: 'POST', body: data }),
  disconnectFacebook: () => request('/facebook/disconnect', { method: 'POST' }),

  // Templates
  getTemplates: () => request('/templates/'),
  createTemplate: (data) => request('/templates/', { method: 'POST', body: data }),
  updateTemplate: (id, data) => request(`/templates/${id}`, { method: 'PUT', body: data }),
  setDefaultTemplate: (id) => request(`/templates/${id}/set-default`, { method: 'POST' }),
  deleteTemplate: (id) => request(`/templates/${id}`, { method: 'DELETE' }),

  // Topics
  getCategories: () => request('/topics/categories'),
  getTopics: (category) => request(`/topics/${category && category !== 'All' ? `?category=${encodeURIComponent(category)}` : ''}`),
  createTopic: (data) => request('/topics/', { method: 'POST', body: data }),
  updateTopic: (id, data) => request(`/topics/${id}`, { method: 'PUT', body: data }),
  deleteTopic: (id) => request(`/topics/${id}`, { method: 'DELETE' }),

  // Schedules
  getSchedules: () => request('/schedules/'),
  updateSchedules: (slots) => request('/schedules/slots', { method: 'PUT', body: slots }),
  toggleAutomation: (enabled) => request('/schedules/toggle-automation', { method: 'POST', body: { enabled } }),
  updateSettings: (data) => request('/schedules/settings', { method: 'POST', body: data }),

  // Posts
  getPosts: (status = 'all') => request(`/posts/?status=${status}`),
  getPost: (id) => request(`/posts/${id}`),
  generatePost: (data) => request('/posts/generate', { method: 'POST', body: data }),
  publishPost: (id) => request(`/posts/${id}/publish`, { method: 'POST' }),
  updatePost: (id, data) => request(`/posts/${id}`, { method: 'PUT', body: data }),
  deletePost: (id) => request(`/posts/${id}`, { method: 'DELETE' }),
  retryPost: (id) => request(`/posts/${id}/retry`, { method: 'POST' }),
};
