import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { storageService } from '@/services/storage';
import { apiService } from '@/services/api';
import { locationService } from '@/services/location';
import { notificationService } from '@/services/notifications';
import { richNotificationService } from '@/services/richNotifications';
import { offlineSyncService } from '@/services/offlineSync';
import { biometricService } from '@/services/biometric';
import type { AppState, User, AuthTokens, Location, OfflineData } from '@/types';
import i18n from '@/i18n';

interface AppContextType extends AppState {
  // Auth actions
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
  
  // Location actions
  getCurrentLocation: () => Promise<void>;
  startLocationTracking: () => Promise<void>;
  stopLocationTracking: () => void;
  
  // Settings actions
  changeLanguage: (language: string) => Promise<void>;
  changeTheme: (theme: 'light' | 'dark') => Promise<void>;
  
  // Offline actions
  syncOfflineData: () => Promise<void>;
  
  // Utility actions
  setLoading: (loading: boolean) => void;
  showError: (error: string) => void;
  clearError: () => void;
}

type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_AUTHENTICATED'; payload: boolean }
  | { type: 'SET_CURRENT_LOCATION'; payload: Location | null }
  | { type: 'SET_LANGUAGE'; payload: string }
  | { type: 'SET_THEME'; payload: 'light' | 'dark' }
  | { type: 'SET_OFFLINE_DATA'; payload: OfflineData | null }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'UPDATE_USER'; payload: Partial<User> };

const initialState: AppState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  currentLocation: null,
  language: 'en',
  theme: 'light',
  offlineData: null,
  notifications: [],
  error: null,
};

const AppContext = createContext<AppContextType | undefined>(undefined);

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'SET_USER':
      return { ...state, user: action.payload };
    
    case 'SET_AUTHENTICATED':
      return { ...state, isAuthenticated: action.payload };
    
    case 'SET_CURRENT_LOCATION':
      return { ...state, currentLocation: action.payload };
    
    case 'SET_LANGUAGE':
      return { ...state, language: action.payload };
    
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    
    case 'SET_OFFLINE_DATA':
      return { ...state, offlineData: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    
    case 'UPDATE_USER':
      return { 
        ...state, 
        user: state.user ? { ...state.user, ...action.payload } : null 
      };
    
    default:
      return state;
  }
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Initialize app on startup
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      // Load user preferences
      const [language, theme, offlineData] = await Promise.all([
        storageService.getLanguage(),
        storageService.getTheme(),
        storageService.getOfflineData(),
      ]);

      dispatch({ type: 'SET_LANGUAGE', payload: language });
      dispatch({ type: 'SET_THEME', payload: theme });
      dispatch({ type: 'SET_OFFLINE_DATA', payload: offlineData });

      // Set i18n language
      await i18n.changeLanguage(language);

      // Initialize push notifications
      try {
        await notificationService.initialize();
      } catch (error) {
        console.warn('Failed to initialize notification service:', error);
      }
      
      try {
        await richNotificationService.initialize();
      } catch (error) {
        console.warn('Failed to initialize rich notification service:', error);
      }

      // Initialize offline sync
      await offlineSyncService.initialize();

      // Initialize biometric service
      await biometricService.initialize();

      // Always try to get current location for map functionality
      await getCurrentLocation(false);

      // Check if user is logged in
      const tokens = await storageService.getTokens();
      if (tokens && !await storageService.isTokenExpired()) {
        const user = await storageService.getUser();
        if (user) {
          dispatch({ type: 'SET_USER', payload: user });
          dispatch({ type: 'SET_AUTHENTICATED', payload: true });
          
          // Update location for authenticated users
          await getCurrentLocation(true);
        }
      }

    } catch (error) {
      console.error('Failed to initialize app:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to initialize app' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const login = async (email: string, password: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const response = await apiService.login(email, password);
      
      // Store tokens and user data
      await Promise.all([
        storageService.storeTokens(response.tokens, response.user.id),
        storageService.storeUser(response.user),
      ]);

      dispatch({ type: 'SET_USER', payload: response.user });
      dispatch({ type: 'SET_AUTHENTICATED', payload: true });
      
      // Start location tracking (don't let errors block login completion)
      try {
        await getCurrentLocation(true);
      } catch (locationError) {
        console.warn('Location update failed after login (non-critical):', locationError);
      }

    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.message || 'Login failed' });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const register = async (userData: any) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const response = await apiService.register({
        ...userData,
        preferred_language: state.language,
      });

      // Store tokens and user data
      await Promise.all([
        storageService.storeTokens(response.tokens, response.user.id),
        storageService.storeUser(response.user),
      ]);

      dispatch({ type: 'SET_USER', payload: response.user });
      dispatch({ type: 'SET_AUTHENTICATED', payload: true });

      // Start location tracking (don't let errors block registration completion)
      try {
        await getCurrentLocation(true);
      } catch (locationError) {
        console.warn('Location update failed after registration (non-critical):', locationError);
      }

    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.message || 'Registration failed' });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const logout = async () => {
    try {
      console.log('🚪 AppContext logout started');
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Call logout API
      console.log('📡 Calling logout API...');
      await apiService.logout().catch((error) => {
        console.warn('⚠️ Logout API call failed (non-critical):', error);
      });
      
      // Clear all local data
      console.log('🗑️ Clearing local storage...');
      await storageService.clearAll();
      
      // Stop location tracking
      console.log('📍 Stopping location tracking...');
      locationService.stopLocationTracking();

      console.log('🔄 Updating app state...');
      dispatch({ type: 'SET_USER', payload: null });
      dispatch({ type: 'SET_AUTHENTICATED', payload: false });
      dispatch({ type: 'SET_CURRENT_LOCATION', payload: null });
      dispatch({ type: 'SET_OFFLINE_DATA', payload: null });
      
      console.log('✅ Logout completed successfully');

    } catch (error) {
      console.error('❌ Logout error:', error);
      throw error; // Re-throw so the UI can handle it
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
      console.log('🏁 Logout process finished');
    }
  };

  const getCurrentLocation = async (forceAuthenticated?: boolean) => {
    try {
      const location = await locationService.getCurrentLocation();
      dispatch({ type: 'SET_CURRENT_LOCATION', payload: location });
      
      // Update location on server if user is authenticated
      const isAuth = forceAuthenticated || state.isAuthenticated;
      if (isAuth && location) {
        try {
          await apiService.updateLocation({
            latitude: location.latitude,
            longitude: location.longitude,
          });
        } catch (error: any) {
          // Silently handle location update errors (non-critical)
          if (error?.message?.includes('403')) {
            console.warn('Location update permission denied (non-critical)');
          } else {
            console.warn('Location update failed (non-critical):', error?.message);
          }
        }
      }
    } catch (error) {
      console.error('Failed to get current location:', error);
    }
  };

  const startLocationTracking = async () => {
    try {
      const success = await locationService.startLocationTracking((location) => {
        dispatch({ type: 'SET_CURRENT_LOCATION', payload: location });
        
        // Update location on server
        if (state.isAuthenticated) {
          apiService.updateLocation({
            latitude: location.latitude,
            longitude: location.longitude,
          }).catch((error: any) => {
            // Silently handle location update errors (non-critical)
            if (error?.message?.includes('403')) {
              console.warn('Location update permission denied (non-critical)');
            } else {
              console.warn('Location update failed (non-critical):', error?.message);
            }
          });
        }
      });

      if (!success) {
        dispatch({ type: 'SET_ERROR', payload: 'Location permission required' });
      }
    } catch (error) {
      console.error('Failed to start location tracking:', error);
    }
  };

  const stopLocationTracking = () => {
    locationService.stopLocationTracking();
  };

  const changeLanguage = async (language: string) => {
    try {
      // Always change language locally first
      await storageService.setLanguage(language);
      await i18n.changeLanguage(language);
      dispatch({ type: 'SET_LANGUAGE', payload: language });

      // Try to update user preference on server (non-critical)
      if (state.user) {
        try {
          const updatedUser = await apiService.updateProfile({
            preferred_language: language,
          });
          dispatch({ type: 'SET_USER', payload: updatedUser });
          await storageService.storeUser(updatedUser);
        } catch (serverError: any) {
          // Server update failed - not critical, language still changed locally
          if (serverError?.message?.includes('403')) {
            console.warn('Language preference update permission denied (non-critical)');
          } else {
            console.warn('Failed to sync language preference to server (non-critical):', serverError?.message);
          }
        }
      }
    } catch (error) {
      console.error('Failed to change language locally:', error);
    }
  };

  const changeTheme = async (theme: 'light' | 'dark') => {
    try {
      await storageService.setTheme(theme);
      dispatch({ type: 'SET_THEME', payload: theme });
    } catch (error) {
      console.error('Failed to change theme:', error);
    }
  };

  const syncOfflineData = async () => {
    try {
      if (!state.offlineData || !state.isAuthenticated) return;

      // await apiService.syncOfflineData(state.offlineData); // Endpoint removed
      
      // Update last sync timestamp
      const updatedOfflineData = {
        ...state.offlineData,
        lastSync: new Date().toISOString(),
      };
      
      await storageService.storeOfflineData(updatedOfflineData);
      dispatch({ type: 'SET_OFFLINE_DATA', payload: updatedOfflineData });
    } catch (error) {
      console.error('Failed to sync offline data:', error);
    }
  };

  const setLoading = (loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const showError = (error: string) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const clearError = () => {
    dispatch({ type: 'SET_ERROR', payload: null });
  };

  const contextValue: AppContextType = {
    ...state,
    login,
    register,
    logout,
    getCurrentLocation,
    startLocationTracking,
    stopLocationTracking,
    changeLanguage,
    changeTheme,
    syncOfflineData,
    setLoading,
    showError,
    clearError,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

export { AppContext };