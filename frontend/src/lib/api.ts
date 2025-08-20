// Revised: frontend/src/lib/api.ts

// frontend/src/lib/api.ts

import axios from 'axios';
import { toast } from 'react-toastify';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Auth state management for request queuing
let isAuthReady = false;
let authReadyPromise: Promise<void> | null = null;
let authReadyResolve: (() => void) | null = null;

// Initialize auth ready promise
const initializeAuthPromise = () => {
  if (!authReadyPromise) {
    authReadyPromise = new Promise((resolve) => {
      authReadyResolve = resolve;
    });
  }
};

initializeAuthPromise();

// Mark auth as ready (called from AuthContext)
export const markAuthReady = () => {
  console.log('[API] Auth context marked as ready');
  isAuthReady = true;
  if (authReadyResolve) {
    authReadyResolve();
    authReadyResolve = null;
  }
};

// Reset auth ready state (called on logout)
export const resetAuthReady = () => {
  console.log('[API] Auth context reset');
  isAuthReady = false;
  initializeAuthPromise();
};

// Wait for auth to be ready for protected endpoints
const waitForAuthIfNeeded = async (config: any) => {
  // Skip auth waiting for public endpoints
  const publicEndpoints = ['/auth/login', '/auth/otp/', '/auth/admin/setup'];
  const isPublicEndpoint = publicEndpoints.some(endpoint => config.url?.includes(endpoint));
  
  if (isPublicEndpoint) {
    console.log('[API] Public endpoint, skipping auth wait:', config.url);
    return;
  }
  
  // Wait for auth context if not ready, with timeout to prevent deadlocks
  if (!isAuthReady && authReadyPromise) {
    console.log('[API] Waiting for auth context to be ready for:', config.url);
    
    // Add timeout to prevent infinite waiting
    const authTimeout = new Promise<void>((_, reject) => {
      setTimeout(() => {
        console.warn('[API] Auth wait timeout - proceeding without auth ready state');
        reject(new Error('Auth wait timeout'));
      }, 10000); // 10 second timeout
    });
    
    try {
      await Promise.race([authReadyPromise, authTimeout]);
      console.log('[API] Auth context ready, proceeding with request:', config.url);
    } catch (error) {
      console.warn('[API] Auth wait failed or timed out, proceeding anyway:', error.message);
      // Continue with request even if auth wait fails
    }
  }
};

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests - organization context derived from backend session
api.interceptors.request.use(
  async (config) => {
    // Wait for auth context if needed before proceeding
    await waitForAuthIfNeeded(config);
    
    const token = localStorage.getItem('token');
    
    // Debug logging for all requests
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
      hasToken: !!token,
      authReady: isAuthReady,
      timestamp: new Date().toISOString(),
      note: 'Organization context derived from backend session'
    });
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log the full request URL for debugging 404 issues
    const fullUrl = `${config.baseURL}${config.url}`;
    console.log(`[API] Request URL: ${fullUrl}`, {
      method: config.method?.toUpperCase(),
      hasAuth: !!token,
    });
    return config;
  },
  (error) => {
    console.error('[API] Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Handle token expiration and network errors with enhanced debugging
api.interceptors.response.use(
  (response) => {
    // Log successful responses for protected endpoints
    if (response.config.headers?.Authorization) {
      console.log(`[API] Success ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        hasData: !!response.data,
        timestamp: new Date().toISOString()
      });
    }
    return response;
  },
  (error) => {
    const method = error.config?.method?.toUpperCase();
    const url = error.config?.url;
    const status = error.response?.status;
    
    console.error(`[API] Error ${method} ${url}`, {
      status,
      error: error.response?.data,
      timestamp: new Date().toISOString()
    });
    
    if (error.response?.status === 401 || error.response?.status === 403) {
      console.log(`[API] ${error.response.status} Auth error - clearing auth data and redirecting`);
      
      // Show specific error message if available before redirect
      const errorDetail = error.response?.data?.detail;
      if (errorDetail && typeof errorDetail === 'string') {
        console.log(`[API] ${error.response.status} Error reason:`, errorDetail);
        // Show toast notification with error reason before redirect
        toast.error(`Session expired: ${errorDetail}`, {
          position: "top-right",
          autoClose: 3000,
        });
      } else {
        toast.error('Session expired. Please login again.', {
          position: "top-right",
          autoClose: 3000,
        });
      }
      
      localStorage.removeItem('token');
      localStorage.removeItem('user_role');
      localStorage.removeItem('is_super_admin');
      
      // Reset auth ready state
      resetAuthReady();
      
      // Add a small delay to allow logging and toast to complete
      setTimeout(() => {
        window.location.href = '/';
      }, 100);
    } else if (error.response?.status === 404 && url?.includes('/companies/current')) {
      // Special handling for company missing scenario - DO NOT logout
      console.log('[API] 404 on /companies/current - company setup required, not an auth error');
      
      // Add a flag to indicate this is a company setup scenario
      const enhancedError = {
        ...error,
        isCompanySetupRequired: true,
        userMessage: 'Company setup required'
      };
      
      // Don't clear auth data or redirect - let the component handle company onboarding
      return Promise.reject(enhancedError);
    }
    
    // Extract error message with proper handling for arrays and objects
    let errorMessage = 'An unexpected error occurred';
    
    const detail = error.response?.data?.detail;
    const message = error.response?.data?.message;
    
    if (typeof detail === 'string' && detail) {
      errorMessage = detail;
    } else if (typeof message === 'string' && message) {
      errorMessage = message;
    } else if (Array.isArray(detail) && detail.length > 0) {
      // Handle Pydantic validation errors (array of objects)
      const messages = detail.map(err => err.msg || `${err.loc?.join(' -> ')}: ${err.type}`).filter(Boolean);
      errorMessage = messages.length > 0 ? messages.join(', ') : 'Validation error';
    } else if (detail && typeof detail === 'object') {
      // Handle object error details
      errorMessage = detail.error || detail.message || JSON.stringify(detail);
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    console.error('[API] Processed error message:', errorMessage);
    return Promise.reject({
      ...error,
      userMessage: errorMessage,
      status: error.response?.status
    });
  }
);

export default api;