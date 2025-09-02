import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_CONFIG, APP_CONFIG } from '@/constants/Config';
import type { AuthTokens, User, JourneyRequest, DirectJourneyRequest, AIJourneyResponse } from '@/types';

class APIService {
  private baseURL: string;
  private timeout: number;

  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.timeout = APP_CONFIG.API_TIMEOUT;
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    const token = await AsyncStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
    return response.json();
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = await this.getAuthHeaders();

    // Add timeout using AbortController
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    const config: RequestInit = {
      ...options,
      headers: { ...headers, ...options.headers },
      signal: controller.signal,
    };

    try {
      const response = await fetch(url, config);
      clearTimeout(timeoutId);
      return this.handleResponse<T>(response);
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Request timeout - please check your internet connection');
      }
      throw error;
    }
  }

  // Authentication APIs
  async login(email: string, password: string, deviceType: string = 'android'): Promise<{ user: User; tokens: AuthTokens }> {
    console.log('🚀 Starting login request:', { email, deviceType });
    
    try {
      const response = await this.makeRequest<any>(API_CONFIG.ENDPOINTS.AUTH.LOGIN, {
        method: 'POST',
        body: JSON.stringify({ email, password, device_type: deviceType }),
      });
      
      console.log('✅ Login response received:', { 
        hasAccessToken: !!response.access_token,
        hasRefreshToken: !!response.refresh_token,
        userId: response.user_id
      });
      
      // Transform backend response to frontend format
      const tokens: AuthTokens = {
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        token_type: response.token_type || 'bearer',
        expires_in: response.expires_in
      };
      
      console.log('🔄 Getting user profile...');
      
      // Get user profile with the new token (not from storage)
      const user = await this.getProfileWithToken(response.access_token);
      
      console.log('✅ Login completed successfully:', { 
        userId: user._id,
        email: user.email,
        fullName: user.full_name
      });
      
      return { user, tokens };
    } catch (error) {
      console.error('❌ Login error:', error);
      throw error;
    }
  }

  async register(userData: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    preferred_language?: string;
    device_type?: string;
    fcm_token?: string;
  }): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await this.makeRequest<any>(API_CONFIG.ENDPOINTS.AUTH.REGISTER, {
      method: 'POST',
      body: JSON.stringify({ device_type: 'android', ...userData }),
    });
    
    // Transform backend response to frontend format
    const tokens: AuthTokens = {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      token_type: response.token_type || 'bearer',
      expires_in: response.expires_in
    };
    
    // Get user profile with the new token (not from storage)
    const user = await this.getProfileWithToken(response.access_token);
    
    return { user, tokens };
  }
  
  // Helper method to get profile with specific token
  private async getProfileWithToken(token: string): Promise<User> {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
    
    return this.makeRequest(API_CONFIG.ENDPOINTS.AUTH.PROFILE, {
      headers
    });
  }

  async refreshToken(): Promise<AuthTokens> {
    const refreshToken = await AsyncStorage.getItem('refresh_token');
    const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.AUTH.REFRESH}?refresh_token=${refreshToken}`, {
      method: 'POST',
    });
    
    return {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      token_type: response.token_type || 'bearer',
      expires_in: response.expires_in
    };
  }

  async logout(): Promise<void> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.AUTH.LOGOUT, {
      method: 'POST',
    });
  }

  async getProfile(): Promise<User> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.AUTH.PROFILE);
  }

  async updateProfile(updates: Partial<User>): Promise<User> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.AUTH.UPDATE_PROFILE, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  // Journey Planning APIs
  async planJourney(request: JourneyRequest): Promise<AIJourneyResponse> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.JOURNEY.PLAN_WITH_AI, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async planJourneyDirect(request: DirectJourneyRequest): Promise<any> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.JOURNEY.PLAN_DIRECT, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async searchRoutes(query: string): Promise<any> {
    return this.makeRequest(`${API_CONFIG.ENDPOINTS.JOURNEY.SEARCH_ROUTES}?q=${encodeURIComponent(query)}`);
  }

  async getPopularRoutes(): Promise<any> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.JOURNEY.POPULAR_ROUTES);
  }

  async getJourneyHistory(page: number = 1, limit: number = 20): Promise<any> {
    return this.makeRequest(`${API_CONFIG.ENDPOINTS.JOURNEY.HISTORY}?page=${page}&limit=${limit}`);
  }

  async saveRoute(routeData: any): Promise<void> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.JOURNEY.SAVE_ROUTE, {
      method: 'POST',
      body: JSON.stringify(routeData),
    });
  }

  // Mobile-specific APIs
  async updateLocation(location: { latitude: number; longitude: number }): Promise<void> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.MOBILE.UPDATE_LOCATION, {
      method: 'POST',
      body: JSON.stringify(location),
    });
  }

  // Legacy sync method - removed as endpoint doesn't exist

  async registerDevice(deviceData: any): Promise<void> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.MOBILE.REGISTER_DEVICE, {
      method: 'POST',
      body: JSON.stringify(deviceData),
    });
  }

  async registerPushToken(token: string): Promise<void> {
    // For now, just log the token since push token registration endpoint may not exist
    console.log('Registering push token:', token);
    // In a real implementation, this would call a backend endpoint
    // return this.makeRequest('/api/v1/auth/register-push-token', {
    //   method: 'POST',
    //   body: JSON.stringify({ push_token: token }),
    // });
  }

  async getNotifications(): Promise<any> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.MOBILE.NOTIFICATIONS);
  }

  async getStartupData(): Promise<any> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.MOBILE.STARTUP_DATA);
  }

  async getAppConfig(): Promise<any> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.MOBILE.APP_CONFIG);
  }

  // Disruption APIs
  async getActiveDisruptions(): Promise<any> {
    return this.makeRequest(API_CONFIG.ENDPOINTS.DISRUPTIONS.ACTIVE);
  }

  // Additional methods for offline sync
  async addJourneyToHistory(journey: any): Promise<void> {
    return this.makeRequest('/journey-planner/history', {
      method: 'POST',
      body: JSON.stringify(journey),
    });
  }

  // Removed - favorites functionality handled by saveRoute

  async submitFeedback(feedback: any): Promise<void> {
    return this.makeRequest('/feedback', {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  async getPopularRoutes(): Promise<any[]> {
    return this.makeRequest('/routes/popular');
  }

  async getPopularLocations(): Promise<any[]> {
    return this.makeRequest('/locations/popular');
  }
}

export const apiService = new APIService();