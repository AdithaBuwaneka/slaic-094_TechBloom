// =============================================================================
// MOBILE SERVICE - Device Management & Push Notifications
// =============================================================================

import { apiClient } from './client';
import { ENDPOINTS } from './config';
import { 
  DeviceRegistration, 
  PushNotification, 
  OfflineData, 
  APIResponse 
} from '../../types';
import Constants from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';

class MobileService {
  // =============================================================================
  // DEVICE REGISTRATION
  // =============================================================================

  async registerDevice(deviceData: DeviceRegistration): Promise<APIResponse<{
    device_id: string;
    status: string;
    message: string;
    is_new_device: boolean;
    push_enabled: boolean;
  }>> {
    return apiClient.post(ENDPOINTS.MOBILE.REGISTER_DEVICE, deviceData);
  }

  async unregisterDevice(): Promise<APIResponse<{ 
    status: string; 
    message: string 
  }>> {
    return apiClient.delete(ENDPOINTS.MOBILE.UNREGISTER_DEVICE);
  }

  async getUserDevices(): Promise<APIResponse<{
    devices: {
      device_id: string;
      device_token: string;
      platform: string;
      registered_at: string;
      last_active: string;
      is_active: boolean;
    }[];
    total_devices: number;
  }>> {
    return apiClient.get(ENDPOINTS.MOBILE.USER_DEVICES);
  }

  // =============================================================================
  // PUSH NOTIFICATIONS
  // =============================================================================

  async sendTestNotification(data: {
    title?: string;
    body?: string;
    type?: string;
  } = {}): Promise<APIResponse<{
    notification_id: string;
    status: string;
    message: string;
    sent_at: string;
  }>> {
    const testData = {
      title: data.title || 'Test Notification',
      body: data.body || 'This is a test notification from Transit Companion',
      type: data.type || 'test',
      ...data
    };

    return apiClient.post(ENDPOINTS.MOBILE.SEND_TEST_NOTIFICATION, testData);
  }

  async getNotificationHistory(limit: number = 50): Promise<APIResponse<{
    notifications: PushNotification[];
    total_count: number;
    unread_count: number;
  }>> {
    return apiClient.get(`${ENDPOINTS.MOBILE.NOTIFICATIONS}?limit=${limit}`);
  }

  async markNotificationAsRead(notificationId: string): Promise<APIResponse<{
    status: string;
    message: string;
  }>> {
    return apiClient.patch(`${ENDPOINTS.MOBILE.NOTIFICATIONS}/${notificationId}/read`);
  }

  async markAllNotificationsAsRead(): Promise<APIResponse<{
    status: string;
    message: string;
    marked_count: number;
  }>> {
    return apiClient.patch(`${ENDPOINTS.MOBILE.NOTIFICATIONS}/read-all`);
  }

  // =============================================================================
  // LOCATION SERVICES
  // =============================================================================

  async updateLocation(locationData: {
    latitude: number;
    longitude: number;
    accuracy?: number;
    heading?: number;
    speed?: number;
    timestamp?: string;
  }): Promise<APIResponse<{
    status: string;
    message: string;
    location_updated: boolean;
  }>> {
    const locationPayload = {
      ...locationData,
      timestamp: locationData.timestamp || new Date().toISOString()
    };

    return apiClient.post(ENDPOINTS.MOBILE.UPDATE_LOCATION, locationPayload);
  }

  // =============================================================================
  // APP CONFIGURATION
  // =============================================================================

  async getAppConfig(): Promise<APIResponse<{
    version: {
      current: string;
      minimum_required: string;
      update_available: boolean;
      update_required: boolean;
      changelog: string[];
    };
    features: {
      multi_agent_routing: boolean;
      real_time_tracking: boolean;
      community_reports: boolean;
      sri_lankan_modes: boolean;
      multilingual: boolean;
      push_notifications: boolean;
    };
    settings: {
      api_endpoints: Record<string, string>;
      map_configuration: {
        default_zoom: number;
        max_zoom: number;
        tile_server: string;
      };
      cache_settings: {
        route_cache_duration: number;
        offline_data_expiry: number;
      };
    };
    maintenance: {
      is_maintenance_mode: boolean;
      maintenance_message?: string;
      estimated_completion?: string;
    };
  }>> {
    return apiClient.get(ENDPOINTS.MOBILE.APP_CONFIG);
  }

  // =============================================================================
  // OFFLINE DATA MANAGEMENT
  // =============================================================================

  async getOfflineData(): Promise<APIResponse<{
    sri_lanka_transit: {
      bus_routes: any[];
      railway_lines: any[];
      stations: any[];
      fare_data: any[];
      last_updated: string;
    };
    user_data: {
      preferences: any;
      frequent_locations: any[];
      route_history: any[];
      cached_routes: any[];
    };
    app_data: {
      transit_modes: any[];
      fare_calculation_rules: any[];
      multilingual_content: any;
    };
    metadata: {
      version: string;
      generated_at: string;
      expires_at: string;
      size_mb: number;
    };
  }>> {
    return apiClient.get(ENDPOINTS.MOBILE.OFFLINE_DATA);
  }

  async syncOfflineData(): Promise<APIResponse<{
    sync_status: string;
    items_updated: number;
    last_sync: string;
    next_sync?: string;
    conflicts_resolved: number;
  }>> {
    return apiClient.post(`${ENDPOINTS.MOBILE.OFFLINE_DATA}/sync`);
  }

  // =============================================================================
  // HEALTH & DIAGNOSTICS
  // =============================================================================

  async getHealthStatus(): Promise<APIResponse<{
    mobile_service: {
      status: 'healthy' | 'degraded' | 'down';
      response_time_ms: number;
      last_check: string;
    };
    push_service: {
      status: 'healthy' | 'degraded' | 'down';
      delivered_last_hour: number;
      failed_last_hour: number;
    };
    location_service: {
      status: 'healthy' | 'degraded' | 'down';
      updates_received_last_hour: number;
    };
    offline_sync: {
      status: 'healthy' | 'degraded' | 'down';
      last_successful_sync: string;
      pending_uploads: number;
    };
  }>> {
    return apiClient.get(ENDPOINTS.MOBILE.HEALTH);
  }

  // =============================================================================
  // ANALYTICS & TELEMETRY
  // =============================================================================

  async reportAppUsage(usageData: {
    screen_name: string;
    action: string;
    duration_seconds?: number;
    metadata?: Record<string, any>;
  }): Promise<void> {
    try {
      // Fire-and-forget analytics
      apiClient.post('/mobile/analytics/usage', {
        ...usageData,
        timestamp: new Date().toISOString(),
        app_version: Constants.expoConfig?.version || '1.0.0',
        platform: 'mobile'
      });
    } catch (error) {
      // Don't throw errors for analytics failures
      console.log('Analytics reporting failed:', error);
    }
  }

  async reportPerformanceMetrics(metrics: {
    screen_name: string;
    load_time_ms: number;
    memory_usage_mb?: number;
    network_requests?: number;
    errors?: string[];
  }): Promise<void> {
    try {
      // Fire-and-forget performance metrics
      apiClient.post('/mobile/analytics/performance', {
        ...metrics,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.log('Performance metrics reporting failed:', error);
    }
  }

  // =============================================================================
  // ERROR REPORTING
  // =============================================================================

  async reportError(errorData: {
    error_type: 'crash' | 'api_error' | 'ui_error' | 'network_error';
    error_message: string;
    stack_trace?: string;
    user_id?: string;
    screen_name?: string;
    additional_context?: Record<string, any>;
  }): Promise<APIResponse<{
    error_id: string;
    status: string;
    message: string;
  }>> {
    const errorPayload = {
      ...errorData,
      timestamp: new Date().toISOString(),
      app_version: '1.0.0', // TODO: Get from app config
      platform: 'mobile'
    };

    return apiClient.post('/mobile/errors/report', errorPayload);
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  async checkForUpdates(): Promise<APIResponse<{
    update_available: boolean;
    current_version: string;
    latest_version: string;
    is_critical_update: boolean;
    download_url?: string;
    changelog: string[];
    update_size_mb?: number;
  }>> {
    return apiClient.get('/mobile/updates/check');
  }

  async getFeatureFlags(): Promise<APIResponse<{
    flags: Record<string, boolean>;
    experiments: Record<string, any>;
    rollout_percentage: Record<string, number>;
  }>> {
    return apiClient.get('/mobile/feature-flags');
  }

  // =============================================================================
  // LOCAL STORAGE HELPERS
  // =============================================================================

  async cacheOfflineData(data: OfflineData): Promise<void> {
    try {
      // TODO: Implement with AsyncStorage
      // const cacheKey = CACHE_KEYS.OFFLINE_DATA;
      // await AsyncStorage.setItem(cacheKey, JSON.stringify(data));
      console.log('Offline data cached successfully');
    } catch (error) {
      console.error('Error caching offline data:', error);
    }
  }

  async getCachedOfflineData(): Promise<OfflineData | null> {
    try {
      // TODO: Implement with AsyncStorage
      // const cacheKey = CACHE_KEYS.OFFLINE_DATA;
      // const cachedData = await AsyncStorage.getItem(cacheKey);
      // 
      // if (cachedData) {
      //   const data: OfflineData = JSON.parse(cachedData);
      //   // Check if data is still valid
      //   if (new Date(data.expires_at) > new Date()) {
      //     return data;
      //   }
      // }
      
      return null;
    } catch (error) {
      console.error('Error getting cached offline data:', error);
      return null;
    }
  }

  async clearCache(): Promise<void> {
    try {
      // TODO: Implement cache clearing
      // const keys = await AsyncStorage.getAllKeys();
      // const cacheKeys = keys.filter(key => 
      //   key.startsWith('cache_') || 
      //   key.startsWith('offline_') ||
      //   key.startsWith('route_')
      // );
      // await AsyncStorage.multiRemove(cacheKeys);
      
      console.log('Cache cleared successfully');
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }
}

export const mobileService = new MobileService();
export default mobileService;