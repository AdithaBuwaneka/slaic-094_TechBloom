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
  APIResponse 
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
      // TODO: Implement with SecureStore
      // const refreshToken = await SecureStore.getItemAsync('refresh_token');
      
      // if (!refreshToken) {
      //   throw new Error('No refresh token available');
      // }

      // const response = await apiClient.post<AuthResponse>(ENDPOINTS.AUTH.REFRESH, {
      //   refresh_token: refreshToken
      // });

      // if (response.success && response.data) {
      //   await this.storeTokens(response.data);
      //   await apiClient.setAuthToken(response.data.access_token);
      // }

      // return response;
      
      // Placeholder implementation
      throw new Error('Refresh token not implemented');
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

  async updateProfile(profileData: Partial<User>): Promise<APIResponse<{ message: string; user: User }>> {
    return apiClient.put<{ message: string; user: User }>(ENDPOINTS.AUTH.PROFILE, profileData);
  }

  async changePassword(passwordData: {
    current_password: string;
    new_password: string;
  }): Promise<APIResponse<{ message: string }>> {
    return apiClient.post<{ message: string }>(ENDPOINTS.AUTH.CHANGE_PASSWORD, passwordData);
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
      await SecureStore.setItemAsync('access_token', authResponse.access_token);
      await SecureStore.setItemAsync('refresh_token', authResponse.refresh_token);
      await SecureStore.setItemAsync('user_data', JSON.stringify(authResponse.user));
      
      console.log('Tokens stored successfully');
    } catch (error) {
      console.error('Error storing tokens:', error);
      throw error;
    }
  }

  private async clearTokens(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync('access_token');
      await SecureStore.deleteItemAsync('refresh_token');
      await SecureStore.deleteItemAsync('user_data');
      
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
        console.log('Token refresh failed during auto-login');
      }

      // If all fails, clear tokens
      await this.clearTokens();
      return null;
    } catch (error) {
      console.error('Auto-login error:', error);
      await this.clearTokens();
      return null;
    }
  }
}

export const authService = new AuthService();
export default authService;