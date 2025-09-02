import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import type { User, AuthTokens, OfflineData } from '@/types';

class StorageService {
  // Secure storage for sensitive data
  private async setSecureItem(key: string, value: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(key, value);
    } catch (error) {
      console.warn(`Failed to store secure item ${key}:`, error);
    }
  }

  private async getSecureItem(key: string): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync(key);
    } catch (error) {
      console.warn(`Failed to get secure item ${key}:`, error);
      return null;
    }
  }

  private async deleteSecureItem(key: string): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(key);
    } catch (error) {
      console.warn(`Failed to delete secure item ${key}:`, error);
    }
  }

  // Authentication tokens
  async storeTokens(tokens: AuthTokens, userId?: string): Promise<void> {
    try {
      const promises = [
        this.setSecureItem('access_token', tokens.access_token),
        this.setSecureItem('refresh_token', tokens.refresh_token),
        AsyncStorage.setItem('token_expiry', (Date.now() + tokens.expires_in * 1000).toString()),
      ];
      
      if (userId) {
        promises.push(AsyncStorage.setItem('user_id', userId));
      }
      
      await Promise.all(promises);
    } catch (error) {
      console.error('Failed to store tokens:', error);
      throw error;
    }
  }

  async getTokens(): Promise<AuthTokens | null> {
    try {
      const [accessToken, refreshToken, expiryString, userId] = await Promise.all([
        this.getSecureItem('access_token'),
        this.getSecureItem('refresh_token'),
        AsyncStorage.getItem('token_expiry'),
        AsyncStorage.getItem('user_id'),
      ]);

      if (!accessToken || !refreshToken || !expiryString || !userId) {
        return null;
      }

      const expiry = parseInt(expiryString, 10);
      const expiresIn = Math.max(0, Math.floor((expiry - Date.now()) / 1000));

      return {
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'bearer',
        expires_in: expiresIn,
      };
    } catch (error) {
      console.error('Failed to get tokens:', error);
      return null;
    }
  }

  async clearTokens(): Promise<void> {
    try {
      await Promise.all([
        this.deleteSecureItem('access_token'),
        this.deleteSecureItem('refresh_token'),
        AsyncStorage.removeItem('token_expiry'),
        AsyncStorage.removeItem('user_id'),
      ]);
    } catch (error) {
      console.error('Failed to clear tokens:', error);
    }
  }

  async isTokenExpired(): Promise<boolean> {
    try {
      const expiryString = await AsyncStorage.getItem('token_expiry');
      if (!expiryString) return true;

      const expiry = parseInt(expiryString, 10);
      return Date.now() >= expiry - 60000; // Consider expired 1 minute early
    } catch {
      return true;
    }
  }

  // User data
  async storeUser(user: User): Promise<void> {
    try {
      await AsyncStorage.setItem('user', JSON.stringify(user));
    } catch (error) {
      console.error('Failed to store user:', error);
      throw error;
    }
  }

  async getUser(): Promise<User | null> {
    try {
      const userString = await AsyncStorage.getItem('user');
      return userString ? JSON.parse(userString) : null;
    } catch (error) {
      console.error('Failed to get user:', error);
      return null;
    }
  }

  async clearUser(): Promise<void> {
    try {
      await AsyncStorage.removeItem('user');
    } catch (error) {
      console.error('Failed to clear user:', error);
    }
  }

  // App preferences
  async setLanguage(language: string): Promise<void> {
    try {
      await AsyncStorage.setItem('preferred_language', language);
    } catch (error) {
      console.error('Failed to set language:', error);
    }
  }

  async getLanguage(): Promise<string> {
    try {
      return (await AsyncStorage.getItem('preferred_language')) || 'en';
    } catch (error) {
      console.error('Failed to get language:', error);
      return 'en';
    }
  }

  async setTheme(theme: 'light' | 'dark'): Promise<void> {
    try {
      await AsyncStorage.setItem('theme', theme);
    } catch (error) {
      console.error('Failed to set theme:', error);
    }
  }

  async getTheme(): Promise<'light' | 'dark'> {
    try {
      return (await AsyncStorage.getItem('theme')) as 'light' | 'dark' || 'light';
    } catch (error) {
      console.error('Failed to get theme:', error);
      return 'light';
    }
  }

  // Offline data
  async storeOfflineData(data: OfflineData): Promise<void> {
    try {
      await AsyncStorage.setItem('offline_data', JSON.stringify(data));
    } catch (error) {
      console.error('Failed to store offline data:', error);
    }
  }

  async getOfflineData(): Promise<OfflineData | null> {
    try {
      const dataString = await AsyncStorage.getItem('offline_data');
      return dataString ? JSON.parse(dataString) : null;
    } catch (error) {
      console.error('Failed to get offline data:', error);
      return null;
    }
  }

  async clearOfflineData(): Promise<void> {
    try {
      await AsyncStorage.removeItem('offline_data');
    } catch (error) {
      console.error('Failed to clear offline data:', error);
    }
  }

  // Journey history
  async addToHistory(journey: any): Promise<void> {
    try {
      const historyString = await AsyncStorage.getItem('journey_history');
      const history = historyString ? JSON.parse(historyString) : [];
      
      history.unshift({ ...journey, timestamp: new Date().toISOString() });
      
      // Keep only last 100 journeys
      const trimmedHistory = history.slice(0, 100);
      
      await AsyncStorage.setItem('journey_history', JSON.stringify(trimmedHistory));
    } catch (error) {
      console.error('Failed to add to history:', error);
    }
  }

  async getHistory(): Promise<any[]> {
    try {
      const historyString = await AsyncStorage.getItem('journey_history');
      return historyString ? JSON.parse(historyString) : [];
    } catch (error) {
      console.error('Failed to get history:', error);
      return [];
    }
  }

  async clearHistory(): Promise<void> {
    try {
      await AsyncStorage.removeItem('journey_history');
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  }

  // Favorites
  async addToFavorites(journey: any): Promise<void> {
    try {
      const favoritesString = await AsyncStorage.getItem('favorites');
      const favorites = favoritesString ? JSON.parse(favoritesString) : [];
      
      // Check if already exists
      const exists = favorites.some((fav: any) => 
        fav.origin === journey.origin && fav.destination === journey.destination
      );
      
      if (!exists) {
        favorites.unshift({ ...journey, favorited_at: new Date().toISOString() });
        
        // Keep only 50 favorites
        const trimmedFavorites = favorites.slice(0, 50);
        
        await AsyncStorage.setItem('favorites', JSON.stringify(trimmedFavorites));
      }
    } catch (error) {
      console.error('Failed to add to favorites:', error);
    }
  }

  async getFavorites(): Promise<any[]> {
    try {
      const favoritesString = await AsyncStorage.getItem('favorites');
      return favoritesString ? JSON.parse(favoritesString) : [];
    } catch (error) {
      console.error('Failed to get favorites:', error);
      return [];
    }
  }

  async removeFromFavorites(journey: any): Promise<void> {
    try {
      const favoritesString = await AsyncStorage.getItem('favorites');
      const favorites = favoritesString ? JSON.parse(favoritesString) : [];
      
      const filtered = favorites.filter((fav: any) => 
        !(fav.origin === journey.origin && fav.destination === journey.destination)
      );
      
      await AsyncStorage.setItem('favorites', JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to remove from favorites:', error);
    }
  }

  // Push notification token
  async storePushToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem('push_token', token);
    } catch (error) {
      console.error('Failed to store push token:', error);
    }
  }

  async getPushToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('push_token');
    } catch (error) {
      console.error('Failed to get push token:', error);
      return null;
    }
  }

  // Biometric authentication
  async setBiometricEnabled(enabled: boolean): Promise<void> {
    try {
      await AsyncStorage.setItem('biometric_enabled', enabled.toString());
    } catch (error) {
      console.error('Failed to set biometric enabled:', error);
    }
  }

  async getBiometricEnabled(): Promise<boolean> {
    try {
      const enabled = await AsyncStorage.getItem('biometric_enabled');
      return enabled === 'true';
    } catch (error) {
      console.error('Failed to get biometric enabled:', error);
      return false;
    }
  }

  async storeBiometricCredentials(email: string, encryptedPassword: string): Promise<void> {
    try {
      await Promise.all([
        this.setSecureItem('biometric_email', email),
        this.setSecureItem('biometric_password', encryptedPassword),
      ]);
    } catch (error) {
      console.error('Failed to store biometric credentials:', error);
      throw error;
    }
  }

  async getBiometricCredentials(): Promise<{ email: string; password: string } | null> {
    try {
      const [email, password] = await Promise.all([
        this.getSecureItem('biometric_email'),
        this.getSecureItem('biometric_password'),
      ]);

      if (email && password) {
        return { email, password };
      }
      return null;
    } catch (error) {
      console.error('Failed to get biometric credentials:', error);
      return null;
    }
  }

  async hasBiometricCredentials(): Promise<boolean> {
    try {
      const credentials = await this.getBiometricCredentials();
      return !!credentials;
    } catch (error) {
      return false;
    }
  }

  async clearBiometricCredentials(): Promise<void> {
    try {
      await Promise.all([
        this.deleteSecureItem('biometric_email'),
        this.deleteSecureItem('biometric_password'),
        AsyncStorage.removeItem('biometric_enabled'),
      ]);
    } catch (error) {
      console.error('Failed to clear biometric credentials:', error);
    }
  }

  async setBiometricPromptShown(shown: boolean): Promise<void> {
    try {
      await AsyncStorage.setItem('biometric_prompt_shown', shown.toString());
    } catch (error) {
      console.error('Failed to set biometric prompt shown:', error);
    }
  }

  async hasBiometricPromptShown(): Promise<boolean> {
    try {
      const shown = await AsyncStorage.getItem('biometric_prompt_shown');
      return shown === 'true';
    } catch (error) {
      return false;
    }
  }

  // Sync state management
  async setSyncState(state: string): Promise<void> {
    try {
      await AsyncStorage.setItem('sync_state', state);
    } catch (error) {
      console.error('Failed to set sync state:', error);
    }
  }

  async getSyncState(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('sync_state');
    } catch (error) {
      console.error('Failed to get sync state:', error);
      return null;
    }
  }

  // Clear all data (for logout)
  async clearAll(): Promise<void> {
    try {
      await Promise.all([
        this.clearTokens(),
        this.clearUser(),
        this.clearOfflineData(),
        AsyncStorage.multiRemove([
          'journey_history',
          'favorites',
          'push_token',
          'preferred_language',
          'theme'
        ]),
      ]);
    } catch (error) {
      console.error('Failed to clear all data:', error);
    }
  }
}

export const storageService = new StorageService();