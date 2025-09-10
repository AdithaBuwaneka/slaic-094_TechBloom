// =============================================================================
// NOTIFICATION SERVICE - Expo Push Notifications Integration
// =============================================================================

import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { mobileService } from '../api/mobileService';

// Configure notification handling
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

export interface NotificationData {
  type: 'route_update' | 'disruption' | 'fare_deal' | 'reminder' | 'community';
  title: string;
  body: string;
  data?: Record<string, any>;
  routeId?: string;
  userId?: string;
}

class NotificationService {
  private expoPushToken: string | null = null;
  private notificationListener: any = null;
  private responseListener: any = null;

  // =============================================================================
  // INITIALIZATION
  // =============================================================================

  async initialize(): Promise<boolean> {
    try {
      if (!Device.isDevice) {
        console.log('Notifications only work on physical devices');
        return false;
      }

      // Request permissions
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.log('Failed to get push notification permissions');
        return false;
      }

      // Get Expo push token
      this.expoPushToken = await this.getExpoPushToken();
      
      if (this.expoPushToken) {
        // Register device with backend
        await this.registerDeviceWithBackend();
        
        // Set up notification listeners
        this.setupNotificationListeners();
        
        console.log('Notifications initialized successfully');
        return true;
      }

      return false;
    } catch (error) {
      console.error('Error initializing notifications:', error);
      return false;
    }
  }

  private async getExpoPushToken(): Promise<string | null> {
    try {
      const projectId = process.env.EXPO_PROJECT_ID || 'your-expo-project-id';
      
      const token = await Notifications.getExpoPushTokenAsync({
        projectId,
      });

      console.log('Expo Push Token:', token.data);
      return token.data;
    } catch (error) {
      console.error('Error getting Expo push token:', error);
      return null;
    }
  }

  private async registerDeviceWithBackend(): Promise<void> {
    try {
      if (!this.expoPushToken) return;

      const deviceInfo = {
        device_token: this.expoPushToken,
        platform: Platform.OS as 'ios' | 'android',
        app_version: '1.0.0', // TODO: Get from app.json
        device_info: {
          model: Device.modelName || 'Unknown',
          os_version: Device.osVersion || 'Unknown',
          app_build: '1', // TODO: Get from build config
        }
      };

      const response = await mobileService.registerDevice(deviceInfo);
      
      if (response.success) {
        console.log('Device registered successfully:', response.data?.device_id);
      } else {
        console.error('Failed to register device:', response.error?.message);
      }
    } catch (error) {
      console.error('Error registering device with backend:', error);
    }
  }

  // =============================================================================
  // NOTIFICATION LISTENERS
  // =============================================================================

  private setupNotificationListeners(): void {
    // Handle notifications received while app is running
    this.notificationListener = Notifications.addNotificationReceivedListener(
      this.handleNotificationReceived
    );

    // Handle user tapping on notifications
    this.responseListener = Notifications.addNotificationResponseReceivedListener(
      this.handleNotificationResponse
    );
  }

  private handleNotificationReceived = (notification: Notifications.Notification) => {
    console.log('Notification received:', notification);
    
    const { type, routeId } = (notification.request.content.data as any) || {};
    
    // Handle different notification types
    switch (type) {
      case 'route_update':
        this.handleRouteUpdateNotification(notification, routeId);
        break;
      case 'disruption':
        this.handleDisruptionNotification(notification);
        break;
      case 'fare_deal':
        this.handleFareDealNotification(notification);
        break;
      case 'reminder':
        this.handleReminderNotification(notification);
        break;
      case 'community':
        this.handleCommunityNotification(notification);
        break;
      default:
        console.log('Unknown notification type:', type);
    }
  };

  private handleNotificationResponse = (response: Notifications.NotificationResponse) => {
    console.log('Notification tapped:', response);
    
    const { type, routeId, screen } = (response.notification.request.content.data as any) || {};
    
    // Navigate to appropriate screen based on notification type
    this.navigateToScreen(type, { routeId, screen });
  };

  // =============================================================================
  // NOTIFICATION TYPE HANDLERS
  // =============================================================================

  private handleRouteUpdateNotification(
    notification: Notifications.Notification, 
    routeId?: string
  ): void {
    console.log('Route update notification:', routeId);
    // Route data will be updated through WebSocket or manual refresh
    // Store notification for user to see in notification history
  }

  private handleDisruptionNotification(notification: Notifications.Notification): void {
    console.log('Disruption notification');
    // Disruption will trigger UI alerts and update community reports
  }

  private handleFareDealNotification(notification: Notifications.Notification): void {
    console.log('Fare deal notification');
    // Navigate to deals section when implemented
  }

  private handleReminderNotification(notification: Notifications.Notification): void {
    console.log('Reminder notification');
    // Show reminder alert for scheduled journeys
  }

  private handleCommunityNotification(notification: Notifications.Notification): void {
    console.log('Community notification');
    // Navigate to community tab to show new reports
  }

  private navigateToScreen(type: string, data: any): void {
    console.log('Navigate to screen:', type, data);
    
    // Navigation will be handled by the app's routing system
    // For now, we'll emit an event that can be caught by the app
    if (typeof window !== 'undefined' && window.dispatchEvent) {
      window.dispatchEvent(new CustomEvent('notification_tap', {
        detail: { type, data }
      }));
    }
  }

  // =============================================================================
  // PUBLIC METHODS
  // =============================================================================

  async sendTestNotification(): Promise<boolean> {
    try {
      if (!this.expoPushToken) {
        console.log('No push token available');
        return false;
      }

      const response = await mobileService.sendTestNotification({
        title: 'Test Notification',
        body: 'This is a test notification from Transit Companion',
        type: 'test'
      });

      return response.success;
    } catch (error) {
      console.error('Error sending test notification:', error);
      return false;
    }
  }

  async scheduleLocalNotification(
    title: string,
    body: string,
    trigger: Notifications.NotificationTriggerInput,
    data?: Record<string, any>
  ): Promise<string | null> {
    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data: data || {},
          sound: 'default',
        },
        trigger,
      });

      console.log('Local notification scheduled:', notificationId);
      return notificationId;
    } catch (error) {
      console.error('Error scheduling local notification:', error);
      return null;
    }
  }

  async cancelLocalNotification(notificationId: string): Promise<boolean> {
    try {
      await Notifications.cancelScheduledNotificationAsync(notificationId);
      return true;
    } catch (error) {
      console.error('Error canceling notification:', error);
      return false;
    }
  }

  async cancelAllLocalNotifications(): Promise<boolean> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      return true;
    } catch (error) {
      console.error('Error canceling all notifications:', error);
      return false;
    }
  }

  async getBadgeCount(): Promise<number> {
    try {
      return await Notifications.getBadgeCountAsync();
    } catch (error) {
      console.error('Error getting badge count:', error);
      return 0;
    }
  }

  async setBadgeCount(count: number): Promise<boolean> {
    try {
      await Notifications.setBadgeCountAsync(count);
      return true;
    } catch (error) {
      console.error('Error setting badge count:', error);
      return false;
    }
  }

  async clearBadge(): Promise<boolean> {
    return this.setBadgeCount(0);
  }

  // =============================================================================
  // NOTIFICATION CATEGORIES
  // =============================================================================

  async setupNotificationCategories(): Promise<void> {
    try {
      await Notifications.setNotificationCategoryAsync('route_update', [
        {
          identifier: 'view_route',
          buttonTitle: 'View Route',
          options: {
            opensAppToForeground: true,
          },
        },
        {
          identifier: 'dismiss',
          buttonTitle: 'Dismiss',
          options: {
            opensAppToForeground: false,
          },
        },
      ]);

      await Notifications.setNotificationCategoryAsync('disruption', [
        {
          identifier: 'view_alternatives',
          buttonTitle: 'View Alternatives',
          options: {
            opensAppToForeground: true,
          },
        },
        {
          identifier: 'dismiss',
          buttonTitle: 'OK',
          options: {
            opensAppToForeground: false,
          },
        },
      ]);

      await Notifications.setNotificationCategoryAsync('community', [
        {
          identifier: 'view_report',
          buttonTitle: 'View Report',
          options: {
            opensAppToForeground: true,
          },
        },
        {
          identifier: 'vote_helpful',
          buttonTitle: 'Helpful',
          options: {
            opensAppToForeground: false,
          },
        },
      ]);
    } catch (error) {
      console.error('Error setting up notification categories:', error);
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  getPushToken(): string | null {
    return this.expoPushToken;
  }

  isInitialized(): boolean {
    return this.expoPushToken !== null;
  }

  async getNotificationHistory(): Promise<any[]> {
    try {
      const response = await mobileService.getNotificationHistory(50);
      return response.success ? response.data?.notifications || [] : [];
    } catch (error) {
      console.error('Error getting notification history:', error);
      return [];
    }
  }

  // =============================================================================
  // CLEANUP
  // =============================================================================

  cleanup(): void {
    if (this.notificationListener) {
      Notifications.removeNotificationSubscription(this.notificationListener);
    }
    
    if (this.responseListener) {
      Notifications.removeNotificationSubscription(this.responseListener);
    }
  }
}

export const notificationService = new NotificationService();
export default notificationService;