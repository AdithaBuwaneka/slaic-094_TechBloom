// =============================================================================
// AUTHENTICATION SERVICE - Transit Companion Mobile App
// =============================================================================

import { apiClient } from './client';
import { ENDPOINTS } from './config';
import { 
  AuthResponse, 
  LoginRequest, 
  RegisterRequest, 
  User, 
  TravelPreferences,
  APIResponse,
  UserProfile
} from '../../types';
import * as SecureStore from 'expo-secure-store';

class AuthService {
  // =============================================================================
  // AUTHENTICATION METHODS
  // =============================================================================

  async login(credentials: LoginRequest): Promise<APIResponse<AuthResponse>> {
    try {
      const response = await apiClient.post<AuthResponse>(ENDPOINTS.AUTH.LOGIN, credentials);
      
      if (response.success && response.data) {
        // Store tokens securely
        await this.storeTokens(response.data);
        
        // Set auth token for future requests
        await apiClient.setAuthToken(response.data.access_token);
      }
      
      return response;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async register(userData: RegisterRequest): Promise<APIResponse<AuthResponse>> {
    try {
      const response = await apiClient.post<AuthResponse>(ENDPOINTS.AUTH.REGISTER, userData);
      
      if (response.success && response.data) {
        // Store tokens securely
        await this.storeTokens(response.data);
        
        // Set auth token for future requests
        await apiClient.setAuthToken(response.data.access_token);
      }
      
      return response;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async logout(): Promise<APIResponse<{ message: string }>> {
    try {
      const response = await apiClient.post<{ message: string }>(ENDPOINTS.AUTH.LOGOUT);
      
      // Clear stored tokens regardless of API response
      await this.clearTokens();
      await apiClient.clearAuthToken();
      
      return response;
    } catch (error) {
      // Even if API call fails, clear local tokens
      await this.clearTokens();
      await apiClient.clearAuthToken();
      throw error;
    }
  }

  async refreshToken(): Promise<APIResponse<AuthResponse>> {
    try {
      const refreshToken = await SecureStore.getItemAsync('refresh_token');
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post<AuthResponse>(ENDPOINTS.AUTH.REFRESH, {
        refresh_token: refreshToken
      });

      if (response.success && response.data) {
        await this.storeTokens(response.data);
        await apiClient.setAuthToken(response.data.access_token);
        console.log('Token refreshed successfully');
      }

      return response;
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  }

  async verifyToken(): Promise<APIResponse<{ valid: boolean; user: User }>> {
    return apiClient.get<{ valid: boolean; user: User }>(ENDPOINTS.AUTH.VERIFY_TOKEN);
  }

  // =============================================================================
  // USER PROFILE METHODS
  // =============================================================================

  async getProfile(): Promise<APIResponse<User>> {
    return apiClient.get<User>(ENDPOINTS.AUTH.PROFILE);
  }

  async updateProfile(
    profileData: Partial<User> & { preferred_language?: UserProfile['preferred_language'] }
  ): Promise<APIResponse<{ message: string; user: User }>> {
    return apiClient.put<{ message: string; user: User }>(ENDPOINTS.AUTH.PROFILE, profileData);
  }

  async changePassword(passwordData: {
    current_password: string;
    new_password: string;
  }): Promise<APIResponse<{ message: string }>> {
    return apiClient.post<{ message: string }>(ENDPOINTS.AUTH.CHANGE_PASSWORD, passwordData);
  }

  async getUserStats(): Promise<APIResponse<{
    usage_stats: {
      total_trips_planned: number;
      total_distance_traveled: number;
      total_fare_saved: number;
      favorite_destinations: string[];
      most_used_mode?: string;
    };
    community_stats: {
      total_reports: number;
      helpful_votes_received: number;
      community_rating: number;
      user_rating: number;
    };
    environmental_impact: {
      carbon_saved_kg: number;
      equivalent_trees: number;
    };
  }>> {
    return apiClient.get(`${ENDPOINTS.AUTH.PROFILE}/stats`);
  }

  async updateUserPreferences(preferences: {
    notifications?: {
      delays: boolean;
      offers: boolean;
      reminders: boolean;
      community: boolean;
    };
    privacy?: {
      shareLocation: boolean;
      shareReports: boolean;
      analytics: boolean;
    };
  }): Promise<APIResponse<{ message: string; preferences: any }>> {
    return apiClient.put<{ message: string; preferences: any }>(`${ENDPOINTS.AUTH.PROFILE}/preferences`, preferences);
  }

  async getUserPreferences(): Promise<APIResponse<{
    notifications: {
      delays: boolean;
      offers: boolean;
      reminders: boolean;
      community: boolean;
    };
    privacy: {
      shareLocation: boolean;
      shareReports: boolean;
      analytics: boolean;
    };
  }>> {
    return apiClient.get(`${ENDPOINTS.AUTH.PROFILE}/preferences`);
  }

  // =============================================================================
  // ONBOARDING & PREFERENCES
  // =============================================================================

  async setupPreferences(preferences: {
    preferred_transit_modes: string[];
    max_walking_distance: number;
    budget_preference: string;
    time_vs_cost_weight: number;
    comfort_preference: number;
    accessibility_needs: string[];
    avoid_preferences: string[];
    notification_preferences: {
      email_notifications: boolean;
      push_notifications: boolean;
      sms_notifications: boolean;
    };
  }): Promise<APIResponse<{ status: string; message: string; user: User }>> {
    return apiClient.post<{ status: string; message: string; user: User }>(
      ENDPOINTS.AUTH.SETUP_PREFERENCES, 
      preferences
    );
  }

  async getOnboardingStatus(): Promise<APIResponse<{
    user_id: string;
    preferences_setup_completed: boolean;
    requires_setup: boolean;
    setup_date?: string;
    onboarding_steps: {
      registration: boolean;
      preferences_setup: boolean;
      profile_complete: boolean;
    };
  }>> {
    return apiClient.get(ENDPOINTS.AUTH.ONBOARDING_STATUS);
  }

  // =============================================================================
  // TOKEN MANAGEMENT
  // =============================================================================

  private async storeTokens(authResponse: AuthResponse): Promise<void> {
    try {
      // Ensure all values are strings
      const accessToken = String(authResponse.access_token || '');
      const refreshToken = String(authResponse.refresh_token || '');
      const userData = JSON.stringify(authResponse.user || {});
      
      await SecureStore.setItemAsync('access_token', accessToken);
      await SecureStore.setItemAsync('refresh_token', refreshToken);
      await SecureStore.setItemAsync('user_data', userData);
      
      console.log('Tokens stored successfully');
    } catch (error) {
      console.error('Error storing tokens:', error);
      console.error('AuthResponse data:', {
        hasAccessToken: !!authResponse.access_token,
        hasRefreshToken: !!authResponse.refresh_token,
        hasUser: !!authResponse.user,
        accessTokenType: typeof authResponse.access_token,
        refreshTokenType: typeof authResponse.refresh_token
      });
      throw error;
    }
  }

  private async clearTokens(): Promise<void> {
    try {
      // Clear each token individually to avoid partial failures
      try {
        await SecureStore.deleteItemAsync('access_token');
      } catch (e) {
        console.log('Failed to clear access_token:', e);
      }
      
      try {
        await SecureStore.deleteItemAsync('refresh_token');
      } catch (e) {
        console.log('Failed to clear refresh_token:', e);
      }
      
      try {
        await SecureStore.deleteItemAsync('user_data');
      } catch (e) {
        console.log('Failed to clear user_data:', e);
      }
      
      console.log('Tokens cleared successfully');
    } catch (error) {
      console.error('Error clearing tokens:', error);
    }
  }

  async getStoredUser(): Promise<User | null> {
    try {
      const userData = await SecureStore.getItemAsync('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting stored user:', error);
      return null;
    }
  }

  async isAuthenticated(): Promise<boolean> {
    try {
      const token = await SecureStore.getItemAsync('access_token');
      return !!token;
    } catch (error) {
      console.error('Error checking authentication:', error);
      return false;
    }
  }

  // =============================================================================
  // AUTO-LOGIN HELPER
  // =============================================================================

  async attemptAutoLogin(): Promise<User | null> {
    try {
      const isAuth = await this.isAuthenticated();
      if (!isAuth) return null;

      const tokenResponse = await this.verifyToken();
      if (tokenResponse.success && tokenResponse.data?.valid) {
        return tokenResponse.data.user;
      }

      // Try to refresh token if verification failed
      try {
        const refreshResponse = await this.refreshToken();
        if (refreshResponse.success && refreshResponse.data) {
          return refreshResponse.data.user;
        }
      } catch (refreshError) {
        console.log('Token refresh failed during auto-login:', refreshError);
        // Clear potentially corrupted tokens
        await this.clearTokens();
      }

      // If all fails, clear tokens
      await this.clearTokens();
      return null;
    } catch (error) {
      console.error('Auto-login error:', error);
      // Clear tokens on any error to prevent repeated failures
      await this.clearTokens();
      return null;
    }
  }

  // Add a method to clear corrupted tokens on app start
  async clearCorruptedTokens(): Promise<void> {
    try {
      // Try to read tokens to see if they're corrupted
      await SecureStore.getItemAsync('access_token');
      await SecureStore.getItemAsync('refresh_token');
      await SecureStore.getItemAsync('user_data');
    } catch (error) {
      console.log('Detected corrupted tokens, clearing...');
      await this.clearTokens();
    }
  }
}

export const authService = new AuthService();
export default authService;