import { api } from './api';

// Simple token management
export const getToken = () => localStorage.getItem('token');

export const setToken = (token: string) => {
  localStorage.setItem('token', token);
  // Update axios instance auth header
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

export const removeToken = () => {
  localStorage.removeItem('token');
  // Remove auth header from axios instance
  delete api.defaults.headers.common['Authorization'];
};

export const isAuthenticated = () => !!getToken();

// Add auth header to axios instance
export const setupAuthHeader = (token: string) => {
  localStorage.setItem('token', token);
};

// Remove auth header
export const removeAuthHeader = () => {
  localStorage.removeItem('token');
};

// Mock login for development
export const mockLogin = async () => {
  try {
    // Generate a mock JWT-like token for development
    const mockJWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkRldiBVc2VyIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
    
    // Set token in localStorage and update api headers
    setToken(mockJWT);
    
    // Verify the token is set in the api instance
    if (!api.defaults.headers.common['Authorization']) {
      api.defaults.headers.common['Authorization'] = `Bearer ${mockJWT}`;
    }
    
    return mockJWT;
  } catch (error) {
    console.error('Failed to set up mock authentication:', error);
    throw error;
  }
}; 