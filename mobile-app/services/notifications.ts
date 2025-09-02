import { Platform } from 'react-native';
import { storageService } from './storage';
import { apiService } from './api';
import { Notifications, Device, isExpoGo } from './notificationsDynamic';

// Configure notifications behavior only if not in Expo Go
if (!isExpoGo && Notifications) {
  try {
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
      }),
    });
  } catch (error) {
    console.warn('Failed to configure notification handler:', error);
  }
}

class NotificationService {
  private expoPushToken: string | null = null;

  private get isAvailable(): boolean {
    return !isExpoGo && !!Notifications && !!Device;
  }

  async initialize(): Promise<boolean> {
    try {
      // Skip initialization in Expo Go or if Notifications not available
      if (!this.isAvailable) {
        console.log('Push notifications not fully supported in Expo Go - using development build recommended');
        return false;
      }

      // Check if device supports push notifications
      if (!Device.isDevice) {
        console.log('Must use physical device for Push Notifications');
        return false;
      }

      // Get permission for notifications
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      
      if (finalStatus !== 'granted') {
        console.log('Failed to get push token for push notification!');
        return false;
      }

      // Get the push token
      const token = await Notifications.getExpoPushTokenAsync({
        projectId: process.env.EXPO_PROJECT_ID,
      });
      
      this.expoPushToken = token.data;
      console.log('Push token:', this.expoPushToken);

      // Store token locally and register with backend
      await this.registerToken(this.expoPushToken);

      // Configure notification channels (Android)
      if (Platform.OS === 'android') {
        await this.createNotificationChannels();
      }

      return true;
    } catch (error) {
      console.error('Failed to initialize notifications:', error);
      return false;
    }
  }

  private async createNotificationChannels(): Promise<void> {
    // Journey updates channel
    await Notifications.setNotificationChannelAsync('journey-updates', {
      name: 'Journey Updates',
      description: 'Updates about your planned journeys',
      importance: Notifications.AndroidImportance.DEFAULT,
      sound: 'default',
    });

    // Disruption alerts channel
    await Notifications.setNotificationChannelAsync('disruptions', {
      name: 'Traffic Disruptions',
      description: 'Alerts about traffic and service disruptions',
      importance: Notifications.AndroidImportance.HIGH,
      sound: 'default',
      vibrationPattern: [0, 250, 250, 250],
    });

    // Promotions channel
    await Notifications.setNotificationChannelAsync('promotions', {
      name: 'Promotions',
      description: 'Special offers and promotions',
      importance: Notifications.AndroidImportance.LOW,
      sound: 'default',
    });
  }

  async registerToken(token: string): Promise<void> {
    try {
      // Store locally
      await storageService.storePushToken(token);

      // Register with backend
      await apiService.registerPushToken(token);
      
      console.log('Push token registered successfully');
    } catch (error) {
      console.error('Failed to register push token:', error);
    }
  }

  async scheduleJourneyReminder(
    title: string, 
    body: string, 
    triggerDate: Date,
    data?: any
  ): Promise<string> {
    try {
      if (!this.isAvailable) {
        console.log(`[Expo Go] Would schedule: ${title} - ${body}`);
        return 'expo-go-mock-id';
      }

      const identifier = await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data: {
            type: 'journey_reminder',
            ...data,
          },
          sound: 'default',
          priority: Notifications.AndroidNotificationPriority.DEFAULT,
        },
        trigger: {
          date: triggerDate,
        },
      });

      console.log('Scheduled journey reminder:', identifier);
      return identifier;
    } catch (error) {
      console.error('Failed to schedule journey reminder:', error);
      throw error;
    }
  }

  async showDisruptionAlert(
    route: string,
    severity: 'low' | 'medium' | 'high',
    message: string,
    data?: any
  ): Promise<void> {
    try {
      if (isExpoGo) {
        console.log(`[Expo Go] Would show alert: ${route} - ${message}`);
        return;
      }

      await Notifications.scheduleNotificationAsync({
        content: {
          title: `${severity === 'high' ? '🚨' : '⚠️'} ${route} Disruption`,
          body: message,
          data: {
            type: 'disruption',
            route,
            severity,
            ...data,
          },
          sound: 'default',
          priority: severity === 'high' 
            ? Notifications.AndroidNotificationPriority.HIGH 
            : Notifications.AndroidNotificationPriority.DEFAULT,
        },
        trigger: null, // Show immediately
      });

      console.log('Disruption alert shown');
    } catch (error) {
      console.error('Failed to show disruption alert:', error);
    }
  }

  async showJourneyUpdate(
    title: string,
    body: string,
    data?: any
  ): Promise<void> {
    try {
      if (isExpoGo) {
        console.log(`[Expo Go] Would show update: ${title} - ${body}`);
        return;
      }

      await Notifications.scheduleNotificationAsync({
        content: {
          title: `🚌 ${title}`,
          body,
          data: {
            type: 'journey_update',
            ...data,
          },
          sound: 'default',
          priority: Notifications.AndroidNotificationPriority.DEFAULT,
        },
        trigger: null, // Show immediately
      });

      console.log('Journey update shown');
    } catch (error) {
      console.error('Failed to show journey update:', error);
    }
  }

  async cancelScheduledNotification(identifier: string): Promise<void> {
    try {
      await Notifications.cancelScheduledNotificationAsync(identifier);
      console.log('Cancelled scheduled notification:', identifier);
    } catch (error) {
      console.error('Failed to cancel scheduled notification:', error);
    }
  }

  async cancelAllScheduledNotifications(): Promise<void> {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      console.log('Cancelled all scheduled notifications');
    } catch (error) {
      console.error('Failed to cancel all scheduled notifications:', error);
    }
  }

  async getBadgeCount(): Promise<number> {
    try {
      return await Notifications.getBadgeCountAsync();
    } catch (error) {
      console.error('Failed to get badge count:', error);
      return 0;
    }
  }

  async setBadgeCount(count: number): Promise<void> {
    try {
      await Notifications.setBadgeCountAsync(count);
    } catch (error) {
      console.error('Failed to set badge count:', error);
    }
  }

  async clearBadge(): Promise<void> {
    await this.setBadgeCount(0);
  }

  // Notification listeners
  addNotificationReceivedListener(
    listener: (notification: Notifications.Notification) => void
  ) {
    return Notifications.addNotificationReceivedListener(listener);
  }

  addNotificationResponseReceivedListener(
    listener: (response: Notifications.NotificationResponse) => void
  ) {
    return Notifications.addNotificationResponseReceivedListener(listener);
  }

  // Helper methods for common notifications
  async notifyRouteChange(
    origin: string, 
    destination: string, 
    newDuration: string,
    reason: string
  ): Promise<void> {
    await this.showJourneyUpdate(
      'Route Update',
      `${origin} → ${destination}: New duration ${newDuration}. ${reason}`,
      { origin, destination, newDuration, reason }
    );
  }

  async notifyPriceChange(
    route: string, 
    oldPrice: number, 
    newPrice: number
  ): Promise<void> {
    const change = newPrice > oldPrice ? 'increased' : 'decreased';
    const emoji = newPrice > oldPrice ? '📈' : '📉';
    
    await this.showJourneyUpdate(
      'Fare Update',
      `${emoji} ${route} fare ${change} from LKR ${oldPrice} to LKR ${newPrice}`,
      { route, oldPrice, newPrice, change }
    );
  }

  async notifyWeatherImpact(
    area: string,
    condition: string,
    impact: string
  ): Promise<void> {
    await this.showDisruptionAlert(
      area,
      'medium',
      `${condition} weather may cause ${impact}`,
      { weather: condition, impact }
    );
  }

  getExpoPushToken(): string | null {
    return this.expoPushToken;
  }
}

export const notificationService = new NotificationService();