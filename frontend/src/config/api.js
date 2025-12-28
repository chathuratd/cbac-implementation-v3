// API configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_VERSION = '/api/v1';

export const API_ENDPOINTS = {
  getUserProfile: (userId) => `${API_BASE_URL}${API_VERSION}/get-user-profile/${userId}`,
  listCoreBehaviors: (userId) => `${API_BASE_URL}${API_VERSION}/list-core-behaviors/${userId}`,
  analyzeFromStorage: (userId) => `${API_BASE_URL}${API_VERSION}/analyze-behaviors-from-storage?user_id=${userId}`,
  getLLMContext: (userId, params) => {
    const queryParams = new URLSearchParams(params).toString();
    return `${API_BASE_URL}${API_VERSION}/profile/${userId}/llm-context${queryParams ? '?' + queryParams : ''}`;
  },
  health: `${API_BASE_URL}${API_VERSION}/health`,
};

export default API_BASE_URL;
