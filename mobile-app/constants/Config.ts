export const API_CONFIG = {
  BASE_URL: __DEV__ ? 'http://10.0.2.2:8000' : 'https://api.smarttransit.lk',
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/api/v1/auth/login',
      REGISTER: '/api/v1/auth/register', 
      REFRESH: '/api/v1/auth/refresh-token',
      LOGOUT: '/api/v1/auth/logout',
      PROFILE: '/api/v1/auth/me',
      UPDATE_PROFILE: '/api/v1/auth/me',
    },
    JOURNEY: {
      PLAN_DIRECT: '/api/v1/plan-journey/direct',
      PLAN_WITH_AI: '/api/v1/plan-journey/agentic',
      HISTORY: '/api/v1/rn/user/journey-history',
      SAVE_ROUTE: '/api/v1/rn/user/save-route',
      SEARCH_ROUTES: '/api/v1/rn/routes/search',
      POPULAR_ROUTES: '/api/v1/rn/routes/popular',
    },
    DISRUPTIONS: {
      ACTIVE: '/api/v1/rn/disruptions/active-compact',
    },
    MOBILE: {
      UPDATE_LOCATION: '/api/v1/auth/update-location',
      REGISTER_DEVICE: '/api/v1/mobile/devices/register',
      APP_CONFIG: '/api/v1/mobile/app/config',
      STARTUP_DATA: '/api/v1/rn/app/startup-data',
      NOTIFICATIONS: '/api/v1/mobile/notifications/',
    }
  }
};

export const APP_CONFIG = {
  NAME: 'Smart Transit Companion',
  VERSION: '1.0.0',
  SUPPORTED_LANGUAGES: ['en', 'si', 'ta'],
  DEFAULT_LANGUAGE: 'en',
  LOCATION_TIMEOUT: 10000,
  API_TIMEOUT: 30000,
  OFFLINE_SYNC_INTERVAL: 300000, // 5 minutes
  MAX_JOURNEY_HISTORY: 100,
  MAX_FAVORITES: 50,
};

export const SRI_LANKA_CONFIG = {
  DEFAULT_CENTER: {
    latitude: 7.8731,
    longitude: 80.7718,
  },
  ZOOM_LEVELS: {
    CITY: 12,
    ROUTE: 14,
    DETAIL: 16,
  },
  POPULAR_CITIES: [
    { name: 'Colombo', coordinates: { latitude: 6.9271, longitude: 79.8612 } },
    { name: 'Kandy', coordinates: { latitude: 7.2906, longitude: 80.6337 } },
    { name: 'Galle', coordinates: { latitude: 6.0535, longitude: 80.2210 } },
    { name: 'Jaffna', coordinates: { latitude: 9.6615, longitude: 80.0255 } },
    { name: 'Negombo', coordinates: { latitude: 7.2084, longitude: 79.8358 } },
    { name: 'Anuradhapura', coordinates: { latitude: 8.3114, longitude: 80.4037 } },
  ],
  TRANSPORT_MODES: ['bus', 'train', 'tuk', 'walk'],
};