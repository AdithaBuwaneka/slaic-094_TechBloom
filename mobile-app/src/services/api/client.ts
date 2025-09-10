// =============================================================================
// API CLIENT - Transit Companion Mobile App
// =============================================================================

import { API_CONFIG, DEFAULT_HEADERS, ERROR_CODES, HTTP_STATUS } from './config';
import { APIResponse, APIError } from '../../types';
import * as SecureStore from 'expo-secure-store';

class APIClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;
  private requestInterceptors: ((config: RequestConfig) => RequestConfig)[] = [];
  private responseInterceptors: ((response: any) => any)[] = [];

  constructor() {
    this.baseURL = API_CONFIG.BASE_URL + API_CONFIG.API_VERSION;
    this.defaultHeaders = { ...DEFAULT_HEADERS };
  }

  // =============================================================================
  // INTERCEPTORS
  // =============================================================================

  addRequestInterceptor(interceptor: (config: RequestConfig) => RequestConfig) {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor: (response: any) => any) {
    this.responseInterceptors.push(interceptor);
  }

  // =============================================================================
  // TOKEN MANAGEMENT
  // =============================================================================

  async setAuthToken(token: string) {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  async clearAuthToken() {
    delete this.defaultHeaders['Authorization'];
  }

  async getStoredToken(): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync('access_token');
    } catch (error) {
      console.error('Error getting stored token:', error);
      return null;
    }
  }

  async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = await SecureStore.getItemAsync('refresh_token');
      if (!refreshToken) return false;

      const response = await this.post<{access_token: string; refresh_token?: string}>('/auth/refresh', { refresh_token: refreshToken });
      if (response.success && response.data) {
        await SecureStore.setItemAsync('access_token', response.data.access_token);
        if (response.data.refresh_token) {
          await SecureStore.setItemAsync('refresh_token', response.data.refresh_token);
        }
        this.setAuthToken(response.data.access_token);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  }

  // =============================================================================
  // REQUEST CONFIGURATION
  // =============================================================================

  private async prepareRequest(endpoint: string, options: RequestOptions = {}): Promise<RequestConfig> {
    let config: RequestConfig = {
      url: `${this.baseURL}${endpoint}`,
      method: options.method || 'GET',
      headers: {
        ...this.defaultHeaders,
        ...options.headers,
      },
      timeout: options.timeout || API_CONFIG.REQUEST_TIMEOUT,
    };

    if (options.body) {
      config.body = JSON.stringify(options.body);
    }

    // Apply request interceptors
    for (const interceptor of this.requestInterceptors) {
      config = interceptor(config);
    }

    return config;
  }

  // =============================================================================
  // CORE HTTP METHODS
  // =============================================================================

  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<APIResponse<T>> {
    let attempt = 0;
    const maxAttempts = options.retries || API_CONFIG.MAX_RETRY_ATTEMPTS;

    while (attempt < maxAttempts) {
      try {
        const config = await this.prepareRequest(endpoint, options);
        
        const response = await fetch(config.url, {
          method: config.method,
          headers: config.headers,
          body: config.body,
          signal: AbortSignal.timeout(config.timeout),
        });

        const responseData = await this.handleResponse<T>(response);
        
        // Apply response interceptors
        let finalResponse = responseData;
        for (const interceptor of this.responseInterceptors) {
          finalResponse = interceptor(finalResponse);
        }

        return finalResponse;

      } catch (error) {
        attempt++;
        
        if (attempt >= maxAttempts) {
          return this.handleError(error);
        }

        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, API_CONFIG.RETRY_DELAY * attempt));
      }
    }

    // This should never be reached, but TypeScript requires it
    return this.handleError(new Error('Max retry attempts exceeded'));
  }

  async get<T>(endpoint: string, options: RequestOptions = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, body?: any, options: RequestOptions = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body });
  }

  async put<T>(endpoint: string, body?: any, options: RequestOptions = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body });
  }

  async patch<T>(endpoint: string, body?: any, options: RequestOptions = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body });
  }

  async delete<T>(endpoint: string, options: RequestOptions = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  // =============================================================================
  // RESPONSE HANDLING
  // =============================================================================

  private async handleResponse<T>(response: Response): Promise<APIResponse<T>> {
    const timestamp = new Date().toISOString();

    try {
      const responseText = await response.text();
      let data: any = null;

      if (responseText) {
        try {
          data = JSON.parse(responseText);
        } catch (parseError) {
          // If JSON parsing fails, treat as text response
          data = { message: responseText };
        }
      }

      if (response.ok) {
        return {
          data,
          success: true,
          timestamp,
        };
      }

      // Handle HTTP errors
      const error: APIError = {
        error_code: this.getErrorCode(response.status),
        message: data?.message || data?.detail || response.statusText,
        details: data?.details || data,
        timestamp,
      };

      // Handle token expiration
      if (response.status === HTTP_STATUS.UNAUTHORIZED) {
        const tokenRefreshed = await this.refreshToken();
        if (tokenRefreshed) {
          // Token was refreshed, the calling code should retry the request
          throw new Error('TOKEN_REFRESHED');
        } else {
          // Token refresh failed, user needs to login again
          this.clearAuthToken();
        }
      }

      return {
        error,
        success: false,
        timestamp,
      };

    } catch (error) {
      if (error instanceof Error && error.message === 'TOKEN_REFRESHED') {
        throw error; // Re-throw to allow retry
      }

      return this.handleError(error);
    }
  }

  private handleError(error: any): APIResponse<any> {
    const timestamp = new Date().toISOString();
    
    let errorCode = ERROR_CODES.UNKNOWN_ERROR;
    let message = 'An unexpected error occurred';

    if (error instanceof TypeError && error.message.includes('fetch')) {
      errorCode = ERROR_CODES.NETWORK_ERROR;
      message = 'Network connection failed. Please check your internet connection.';
    } else if (error.name === 'AbortError' || error.name === 'TimeoutError') {
      errorCode = ERROR_CODES.TIMEOUT_ERROR;
      message = 'Request timed out. Please try again.';
    } else if (error instanceof Error) {
      message = error.message;
    }

    return {
      error: {
        error_code: errorCode,
        message,
        details: { originalError: error },
        timestamp,
      },
      success: false,
      timestamp,
    };
  }

  private getErrorCode(status: number): string {
    switch (status) {
      case HTTP_STATUS.BAD_REQUEST:
        return ERROR_CODES.VALIDATION_ERROR;
      case HTTP_STATUS.UNAUTHORIZED:
        return ERROR_CODES.UNAUTHORIZED;
      case HTTP_STATUS.FORBIDDEN:
        return ERROR_CODES.FORBIDDEN;
      case HTTP_STATUS.NOT_FOUND:
        return ERROR_CODES.NOT_FOUND;
      case HTTP_STATUS.TOO_MANY_REQUESTS:
        return ERROR_CODES.RATE_LIMIT_EXCEEDED;
      case HTTP_STATUS.INTERNAL_SERVER_ERROR:
      case HTTP_STATUS.BAD_GATEWAY:
      case HTTP_STATUS.SERVICE_UNAVAILABLE:
        return ERROR_CODES.SERVER_ERROR;
      default:
        return ERROR_CODES.UNKNOWN_ERROR;
    }
  }

  // =============================================================================
  // MULTIPART/FORM-DATA SUPPORT
  // =============================================================================

  async uploadFile<T>(endpoint: string, file: any, additionalData?: Record<string, any>): Promise<APIResponse<T>> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      if (additionalData) {
        Object.keys(additionalData).forEach(key => {
          formData.append(key, additionalData[key]);
        });
      }

      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          ...this.defaultHeaders,
          'Content-Type': 'multipart/form-data',
        },
        body: formData,
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  getFullURL(endpoint: string): string {
    return `${this.baseURL}${endpoint}`;
  }

  setBaseURL(url: string) {
    this.baseURL = url;
  }

  setDefaultHeader(key: string, value: string) {
    this.defaultHeaders[key] = value;
  }

  removeDefaultHeader(key: string) {
    delete this.defaultHeaders[key];
  }
}

// =============================================================================
// INTERFACES
// =============================================================================

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
}

interface RequestConfig {
  url: string;
  method: string;
  headers: Record<string, string>;
  body?: string;
  timeout: number;
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

export const apiClient = new APIClient();

// Set up automatic token injection
apiClient.addRequestInterceptor((config) => {
  // Make this synchronous for now, token will be set via setAuthToken when available
  return config;
});

// Set up automatic error handling
apiClient.addResponseInterceptor((response) => {
  if (!response.success && response.error?.error_code === ERROR_CODES.UNAUTHORIZED) {
    // Handle global logout if needed
    console.log('User session expired, redirecting to login...');
  }
  return response;
});

export default apiClient;