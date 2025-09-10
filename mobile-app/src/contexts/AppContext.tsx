// =============================================================================
// APP CONTEXT - Global Application State Management
// =============================================================================

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { User, RouteOption, DisruptionAlert, CommunityReport } from '../types';
import { authService } from '../services/api/authService';
import { apiClient } from '../services/api/client';
import { travelService } from '../services/api/travelService';
import { notificationService } from '../services/notifications/NotificationService';
import { webSocketService } from '../services/websocket/WebSocketService';
import { initializeAPI } from '../services/api';

interface AppState {
  // Authentication
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Navigation
  currentRoute: RouteOption | null;
  routeHistory: RouteOption[];
  
  // Real-time data
  activeDisruptions: DisruptionAlert[];
  recentCommunityReports: CommunityReport[];
  
  // App settings
  isOfflineMode: boolean;
  language: 'en' | 'si' | 'ta';
  
  // Services status
  services: {
    notifications: boolean;
    websocket: boolean;
    backend: boolean;
  };
}

interface AppActions {
  // Authentication
  login: (email: string, password: string) => Promise<boolean>;
  register: (userData: any) => Promise<boolean>;
  logout: () => Promise<void>;
  
  // Route management
  setCurrentRoute: (route: RouteOption) => void;
  addToRouteHistory: (route: RouteOption) => Promise<void>;
  clearRouteHistory: () => void;
  loadRouteHistoryFromBackend: () => Promise<RouteOption[]>;
  
  // Real-time updates
  updateDisruptions: (disruptions: DisruptionAlert[]) => void;
  updateCommunityReports: (reports: CommunityReport[]) => void;
  
  // App settings
  setLanguage: (language: 'en' | 'si' | 'ta') => void;
  setOfflineMode: (enabled: boolean) => void;
  
  // Service management
  initializeServices: () => Promise<void>;
  reconnectServices: () => Promise<void>;
}

type AppContextType = AppState & AppActions;

const AppContext = createContext<AppContextType | undefined>(undefined);

interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const [state, setState] = useState<AppState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    currentRoute: null,
    routeHistory: [],
    activeDisruptions: [],
    recentCommunityReports: [],
    isOfflineMode: false,
    language: 'en',
    services: {
      notifications: false,
      websocket: false,
      backend: false,
    },
  });

  // =============================================================================
  // INITIALIZATION
  // =============================================================================

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true }));

      // Initialize API services
      await initializeAPI();
      
      // Try to restore authentication
      const user = await authService.attemptAutoLogin();
      if (user) {
        setState(prev => ({
          ...prev,
          user,
          isAuthenticated: true,
        }));
        
        // Initialize user-dependent services
        await initializeUserServices(user.user_id);
      }

      // Initialize general services
      await initializeServices();

      setState(prev => ({
        ...prev,
        isLoading: false,
        services: {
          ...prev.services,
          backend: true,
        },
      }));

    } catch (error) {
      console.error('App initialization error:', error);
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const initializeServices = async () => {
    try {
      // Initialize notifications
      const notificationsEnabled = await notificationService.initialize();
      
      setState(prev => ({
        ...prev,
        services: {
          ...prev.services,
          notifications: notificationsEnabled,
        },
      }));

      console.log('Services initialized - Notifications:', notificationsEnabled);
    } catch (error) {
      console.error('Error initializing services:', error);
    }
  };

  const initializeUserServices = async (userId: string) => {
    try {
      // Get stored auth token for WebSocket authentication
      const token = await apiClient.getStoredToken();
      
      // Connect WebSocket for real-time updates
      const websocketConnected = await webSocketService.connect(userId, token);
      
      if (websocketConnected) {
        // Subscribe to real-time updates
        setupWebSocketSubscriptions();
      }

      setState(prev => ({
        ...prev,
        services: {
          ...prev.services,
          websocket: websocketConnected,
        },
      }));

    } catch (error) {
      console.error('Error initializing user services:', error);
    }
  };

  const setupWebSocketSubscriptions = () => {
    // Subscribe to disruption alerts
    webSocketService.subscribeToDisruptions((disruption) => {
      setState(prev => ({
        ...prev,
        activeDisruptions: [disruption, ...prev.activeDisruptions].slice(0, 10),
      }));
    });

    // Subscribe to community reports
    webSocketService.subscribeToCommunityReports((report) => {
      setState(prev => ({
        ...prev,
        recentCommunityReports: [report, ...prev.recentCommunityReports].slice(0, 20),
      }));
    });

    // Subscribe to route updates if there's an active route
    if (state.currentRoute) {
      webSocketService.subscribeToRouteUpdates(
        state.currentRoute.route_id,
        (update) => {
          console.log('Route update received:', update);
          // TODO: Update current route with new information
        }
      );
    }
  };

  // =============================================================================
  // AUTHENTICATION ACTIONS
  // =============================================================================

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await authService.login({ email, password });
      
      if (response.success && response.data) {
        const user = response.data.user;
        setState(prev => ({
          ...prev,
          user,
          isAuthenticated: true,
        }));

        // Initialize user services
        await initializeUserServices(user.user_id);
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (userData: any): Promise<boolean> => {
    try {
      const response = await authService.register(userData);
      
      if (response.success && response.data) {
        const user = response.data.user;
        setState(prev => ({
          ...prev,
          user,
          isAuthenticated: true,
        }));

        // Initialize user services
        await initializeUserServices(user.user_id);
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
      
      // Disconnect WebSocket
      webSocketService.disconnect();
      
      // Reset state
      setState(prev => ({
        ...prev,
        user: null,
        isAuthenticated: false,
        currentRoute: null,
        routeHistory: [],
        activeDisruptions: [],
        recentCommunityReports: [],
        services: {
          ...prev.services,
          websocket: false,
        },
      }));
      
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // =============================================================================
  // ROUTE MANAGEMENT ACTIONS
  // =============================================================================

  const setCurrentRoute = (route: RouteOption) => {
    setState(prev => ({ ...prev, currentRoute: route }));
    
    // Subscribe to updates for the new route
    if (state.services.websocket) {
      webSocketService.subscribeToRouteUpdates(
        route.route_id,
        (update) => {
          console.log('Route update for current route:', update);
        }
      );
    }
  };

  const addToRouteHistory = async (route: RouteOption) => {
    const updatedHistory = [route, ...state.routeHistory.filter(r => r.route_id !== route.route_id)].slice(0, 10);
    
    setState(prev => ({
      ...prev,
      routeHistory: updatedHistory,
    }));

    // Save to AsyncStorage (local storage)
    try {
      await AsyncStorage.setItem('recent_routes', JSON.stringify(updatedHistory));
      console.log('Route saved to local storage');
    } catch (error) {
      console.error('Error saving route to local storage:', error);
    }

    // Save to backend database
    if (state.user?.user_id) {
      try {
        const backendResponse = await travelService.saveRouteToBackend(route, state.user.user_id);
        if (backendResponse.success) {
          console.log('Route saved to backend database successfully');
        } else {
          console.warn('Failed to save route to backend:', backendResponse.error?.message);
        }
      } catch (error) {
        console.error('Error saving route to backend:', error);
      }
    } else {
      console.warn('No user logged in, skipping backend save');
    }
  };

  const clearRouteHistory = () => {
    setState(prev => ({ ...prev, routeHistory: [] }));
  };

  const loadRouteHistoryFromBackend = async (): Promise<RouteOption[]> => {
    if (!state.user?.user_id) {
      console.warn('No user logged in, cannot fetch backend route history');
      return [];
    }

    try {
      const response = await travelService.getRouteHistoryFromBackend(state.user.user_id, 10);
      if (response.success && response.data) {
        console.log('Loaded route history from backend:', response.data.length, 'routes');
        return response.data;
      } else {
        console.warn('Failed to load route history from backend:', response.error?.message);
        return [];
      }
    } catch (error) {
      console.error('Error loading route history from backend:', error);
      return [];
    }
  };

  // =============================================================================
  // REAL-TIME UPDATE ACTIONS
  // =============================================================================

  const updateDisruptions = (disruptions: DisruptionAlert[]) => {
    setState(prev => ({ ...prev, activeDisruptions: disruptions }));
  };

  const updateCommunityReports = (reports: CommunityReport[]) => {
    setState(prev => ({ ...prev, recentCommunityReports: reports }));
  };

  // =============================================================================
  // APP SETTINGS ACTIONS
  // =============================================================================

  const setLanguage = (language: 'en' | 'si' | 'ta') => {
    setState(prev => ({ ...prev, language }));
    // TODO: Save to AsyncStorage
  };

  const setOfflineMode = (enabled: boolean) => {
    setState(prev => ({ ...prev, isOfflineMode: enabled }));
    
    if (enabled) {
      // Disconnect WebSocket to save data
      webSocketService.disconnect();
      setState(prev => ({
        ...prev,
        services: { ...prev.services, websocket: false },
      }));
    } else if (state.user) {
      // Reconnect WebSocket
      initializeUserServices(state.user.user_id);
    }
  };

  // =============================================================================
  // SERVICE MANAGEMENT ACTIONS
  // =============================================================================

  const reconnectServices = async () => {
    try {
      // Reconnect WebSocket if user is authenticated
      if (state.user && !state.isOfflineMode) {
        const connected = await webSocketService.connect(state.user.user_id);
        setState(prev => ({
          ...prev,
          services: { ...prev.services, websocket: connected },
        }));
      }

      // Test backend connection
      // const backendHealthy = await checkServicesHealth();
      // setState(prev => ({
      //   ...prev,
      //   services: { ...prev.services, backend: backendHealthy.overall },
      // }));

    } catch (error) {
      console.error('Error reconnecting services:', error);
    }
  };

  // =============================================================================
  // CONTEXT VALUE
  // =============================================================================

  const contextValue: AppContextType = {
    // State
    ...state,
    
    // Actions
    login,
    register,
    logout,
    setCurrentRoute,
    addToRouteHistory,
    clearRouteHistory,
    loadRouteHistoryFromBackend,
    updateDisruptions,
    updateCommunityReports,
    setLanguage,
    setOfflineMode,
    initializeServices,
    reconnectServices,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

// =============================================================================
// HELPER HOOKS
// =============================================================================

export function useAuth() {
  const { user, isAuthenticated, isLoading, login, register, logout } = useApp();
  return { user, isAuthenticated, isLoading, login, register, logout };
}

export function useRoutes() {
  const { 
    currentRoute, 
    routeHistory, 
    setCurrentRoute, 
    addToRouteHistory, 
    clearRouteHistory,
    loadRouteHistoryFromBackend
  } = useApp();
  
  return {
    currentRoute,
    routeHistory,
    setCurrentRoute,
    addToRouteHistory,
    clearRouteHistory,
    loadRouteHistoryFromBackend,
  };
}

export function useRealTimeData() {
  const {
    activeDisruptions,
    recentCommunityReports,
    updateDisruptions,
    updateCommunityReports,
  } = useApp();
  
  return {
    activeDisruptions,
    recentCommunityReports,
    updateDisruptions,
    updateCommunityReports,
  };
}

export function useServiceStatus() {
  const { services, reconnectServices } = useApp();
  return { services, reconnectServices };
}

export default AppProvider;