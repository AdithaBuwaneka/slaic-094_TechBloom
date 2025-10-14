// =============================================================================
// API CONFIGURATION - Transit Companion Mobile App
// =============================================================================

import { Platform } from 'react-native';

// Backend Configuration
export const API_CONFIG = {
  // Base URLs for different environments
  BASE_URL: __DEV__ 
    ? Platform.OS === 'web'
      ? 'http://localhost:8000'  // Web development
      : 'http://10.0.2.2:8000'  // Expo Go - use actual computer IP
    : 'https://your-production-domain.com',  // Production
  
  // API Version
  API_VERSION: '/api/v1',
  
  // Timeout settings
  REQUEST_TIMEOUT: 30000, // 30 seconds
  
  // Retry configuration
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
  
  // Cache settings
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  
  // WebSocket URL
  WS_URL: __DEV__ 
    ? Platform.OS === 'web'
      ? 'ws://localhost:8000/api/v1/ws/realtime'
      : 'ws://10.0.2.2:8000/api/v1/ws/realtime'  // Use same IP as BASE_URL
    : 'wss://your-production-domain.com/api/v1/ws/realtime',
};

// API Endpoints
export const ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    VERIFY_TOKEN: '/auth/verify-token',
    PROFILE: '/auth/profile',
    CHANGE_PASSWORD: '/auth/change-password',
    SETUP_PREFERENCES: '/auth/setup-preferences',
    ONBOARDING_STATUS: '/auth/onboarding-status',
  },
  
  // Travel Planning (Multi-Agent System)
  TRAVEL: {
    PLAN_ROUTE: '/travel/plan-route',
    SELECT_ROUTE: '/travel/select-route',
    USER_PREFERENCES: '/travel/user-preferences',
    REPORT_DISRUPTION: '/travel/report-disruption',
    ACTIVE_DISRUPTIONS: '/travel/active-disruptions',
    TEST_SEARCH: '/travel/test-search',
    TEST_LLM: '/travel/test-llm-summarizer',
    SEARCH_ROUTE_INFO: '/travel/search-route-info',
    ROUTE_HISTORY: '/travel/route-history',
    SAVE_ROUTE: '/travel/save-route',
    DELETE_ROUTE: '/travel/delete-route',
  },
  
  // Mobile App Specific
  MOBILE: {
    REGISTER_DEVICE: '/mobile/register-device',
    UNREGISTER_DEVICE: '/mobile/unregister-device',
    SEND_TEST_NOTIFICATION: '/mobile/send-test-notification',
    NOTIFICATIONS: '/mobile/notifications',
    UPDATE_LOCATION: '/mobile/update-location',
    APP_CONFIG: '/mobile/app-config',
    OFFLINE_DATA: '/mobile/offline-data',
    HEALTH: '/mobile/health',
    USER_DEVICES: '/mobile/user-devices',
  },
  
  // RAG Chatbot
  CHATBOT: {
    ASK: '/chatbot/ask',
    HEALTH: '/chatbot/health',
  },
  
  // Sri Lankan Transit Data
  SRI_LANKA: {
    RAILWAYS_REALTIME: '/sri-lanka/railways/realtime',
    BUS_TIMETABLES: '/sri-lanka/bus/timetables',
    BUS_ROUTE_MAPS: '/sri-lanka/bus/route-maps',
    BUS_FARES: '/sri-lanka/bus/fares',
    GTFS: '/sri-lanka/gtfs',
  },
  
  // Community Features
  COMMUNITY: {
    TRAFFIC: '/community/traffic',
    DELAYS: '/community/delays', 
    FARES: '/community/fares',
    ACCESSIBILITY: '/community/accessibility',
    SAFETY: '/community/safety',
    REPORTS: '/community/reports',
    STATS: '/community/stats',
    HEALTH: '/community/health',
  },
  
  // Weather Integration
  WEATHER: {
    CURRENT: '/weather/current',
    FORECAST: '/weather/forecast',
    TRAVEL_ADVICE: '/weather/travel-advice',
  },
  
  // Admin (if needed)
  ADMIN: {
    DASHBOARD: '/admin/dashboard',
    USERS: '/admin/users',
    ANALYTICS: '/admin/analytics',
    SYSTEM_HEALTH: '/admin/system-health',
  },
  
  // System
  SYSTEM: {
    HEALTH: '/health',
    DB_CONNECTION: '/db-connection',
  },
  
  // WebSocket
  WEBSOCKET: {
    REALTIME: '/ws/realtime',
    STATS: '/ws/realtime/stats',
  },
};

// Request Headers
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'User-Agent': 'TransitCompanion-Mobile/1.0.0',
};

// Error Codes
export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
};

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
};

// Cache Keys
export const CACHE_KEYS = {
  USER_PROFILE: 'user_profile',
  ROUTE_HISTORY: 'route_history',
  USER_PREFERENCES: 'user_preferences',
  OFFLINE_DATA: 'offline_data',
  SRI_LANKA_DATA: 'sri_lanka_data',
  FREQUENT_LOCATIONS: 'frequent_locations',
  APP_CONFIG: 'app_config',
};

// Storage Keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  DEVICE_TOKEN: 'device_token',
  LANGUAGE_PREFERENCE: 'language_preference',
  ONBOARDING_COMPLETED: 'onboarding_completed',
  TERMS_ACCEPTED: 'terms_accepted',
  PRIVACY_ACCEPTED: 'privacy_accepted',
};