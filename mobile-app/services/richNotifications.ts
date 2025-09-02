import * as FileSystem from 'expo-file-system';
import { Image } from 'react-native';
import { notificationService } from './notifications';
import { Notifications, isExpoGo } from './notificationsDynamic';

interface RichNotificationContent {
  title: string;
  body: string;
  imageUrl?: string;
  actions?: NotificationAction[];
  data?: Record<string, any>;
  sound?: string;
  priority?: 'low' | 'normal' | 'high';
}

interface NotificationAction {
  identifier: string;
  title: string;
  options?: {
    foreground?: boolean;
    destructive?: boolean;
    authenticationRequired?: boolean;
  };
}

class RichNotificationService {
  private cachedImages: Map<string, string> = new Map();

  private get isAvailable(): boolean {
    return !isExpoGo && !!Notifications;
  }

  async initialize(): Promise<void> {
    try {
      if (!this.isAvailable) {
        console.log('Rich notifications not fully supported in Expo Go - development build recommended');
        return;
      }

      // Register notification categories with actions
      await this.registerNotificationCategories();
      console.log('Rich notification service initialized');
    } catch (error) {
      console.error('Failed to initialize rich notification service:', error);
    }
  }

  private async registerNotificationCategories(): Promise<void> {
    // Journey Planning Category
    await Notifications.setNotificationCategoryAsync('journey_planning', [
      {
        identifier: 'view_route',
        title: 'View Route',
        options: { foreground: true },
      },
      {
        identifier: 'start_navigation',
        title: 'Start Navigation', 
        options: { foreground: true },
      },
    ]);

    // Disruption Alert Category
    await Notifications.setNotificationCategoryAsync('disruption_alert', [
      {
        identifier: 'find_alternative',
        title: 'Find Alternative',
        options: { foreground: true },
      },
      {
        identifier: 'dismiss',
        title: 'Dismiss',
        options: { foreground: false },
      },
    ]);

    // Fare Update Category
    await Notifications.setNotificationCategoryAsync('fare_update', [
      {
        identifier: 'view_details',
        title: 'View Details',
        options: { foreground: true },
      },
      {
        identifier: 'save_route',
        title: 'Save Route',
        options: { foreground: false },
      },
    ]);

    // Reminder Category
    await Notifications.setNotificationCategoryAsync('reminder', [
      {
        identifier: 'snooze',
        title: 'Snooze 10min',
        options: { foreground: false },
      },
      {
        identifier: 'plan_journey',
        title: 'Plan Journey',
        options: { foreground: true },
      },
    ]);
  }

  async showRichNotification(content: RichNotificationContent): Promise<string> {
    try {
      if (isExpoGo) {
        console.log(`[Expo Go] Would show rich notification: ${content.title} - ${content.body}`);
        return 'expo-go-rich-mock-id';
      }

      let attachmentUri: string | undefined;
      
      // Download and cache image if provided
      if (content.imageUrl) {
        attachmentUri = await this.downloadAndCacheImage(content.imageUrl);
      }

      const notificationContent: Notifications.NotificationContentInput = {
        title: content.title,
        body: content.body,
        data: content.data || {},
        sound: content.sound || 'default',
        priority: this.mapPriority(content.priority || 'normal'),
      };

      // Add attachment if image was successfully cached
      if (attachmentUri) {
        notificationContent.attachments = [{
          url: attachmentUri,
          options: {
            thumbnailHidden: false,
            thumbnailClippingRect: { x: 0, y: 0, width: 1, height: 1 },
          },
        }];
      }

      // Add category for actions
      if (content.actions && content.actions.length > 0) {
        notificationContent.categoryIdentifier = this.getCategoryForActions(content.actions);
      }

      const identifier = await Notifications.scheduleNotificationAsync({
        content: notificationContent,
        trigger: null, // Show immediately
      });

      console.log('Rich notification shown:', identifier);
      return identifier;
    } catch (error) {
      console.error('Failed to show rich notification:', error);
      throw error;
    }
  }

  private async downloadAndCacheImage(imageUrl: string): Promise<string | undefined> {
    try {
      // Check if already cached
      if (this.cachedImages.has(imageUrl)) {
        return this.cachedImages.get(imageUrl);
      }

      // Create cache directory if it doesn't exist
      const cacheDir = `${FileSystem.cacheDirectory}notifications/`;
      await FileSystem.makeDirectoryAsync(cacheDir, { intermediates: true });

      // Generate cache filename
      const filename = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}.jpg`;
      const localUri = `${cacheDir}${filename}`;

      // Download image
      const downloadResult = await FileSystem.downloadAsync(imageUrl, localUri);
      
      if (downloadResult.status === 200) {
        this.cachedImages.set(imageUrl, localUri);
        return localUri;
      }
      
      return undefined;
    } catch (error) {
      console.error('Failed to download notification image:', error);
      return undefined;
    }
  }

  private mapPriority(priority: 'low' | 'normal' | 'high'): Notifications.AndroidNotificationPriority {
    switch (priority) {
      case 'low':
        return Notifications.AndroidNotificationPriority.LOW;
      case 'high':
        return Notifications.AndroidNotificationPriority.HIGH;
      default:
        return Notifications.AndroidNotificationPriority.DEFAULT;
    }
  }

  private getCategoryForActions(actions: NotificationAction[]): string {
    // Simple heuristic to determine category based on action identifiers
    const actionIds = actions.map(a => a.identifier);
    
    if (actionIds.includes('view_route') || actionIds.includes('start_navigation')) {
      return 'journey_planning';
    }
    if (actionIds.includes('find_alternative')) {
      return 'disruption_alert';
    }
    if (actionIds.includes('view_details') || actionIds.includes('save_route')) {
      return 'fare_update';
    }
    if (actionIds.includes('snooze') || actionIds.includes('plan_journey')) {
      return 'reminder';
    }
    
    return 'default';
  }

  // Specialized rich notifications for different scenarios

  async showJourneyPlanningResult(
    origin: string,
    destination: string,
    duration: string,
    imageUrl?: string,
    routeData?: any
  ): Promise<string> {
    return this.showRichNotification({
      title: '🚌 Journey Planned Successfully',
      body: `${origin} → ${destination} (${duration})`,
      imageUrl,
      priority: 'normal',
      actions: [
        { identifier: 'view_route', title: 'View Route' },
        { identifier: 'start_navigation', title: 'Start Navigation' },
      ],
      data: {
        type: 'journey_result',
        origin,
        destination,
        duration,
        routeData,
      },
    });
  }

  async showDisruptionAlert(
    route: string,
    severity: 'low' | 'medium' | 'high',
    message: string,
    alternativeRoutes?: any[],
    mapImageUrl?: string
  ): Promise<string> {
    const emoji = severity === 'high' ? '🚨' : '⚠️';
    const priority = severity === 'high' ? 'high' : 'normal';

    return this.showRichNotification({
      title: `${emoji} ${route} Disruption`,
      body: message,
      imageUrl: mapImageUrl,
      priority,
      actions: [
        { identifier: 'find_alternative', title: 'Find Alternative' },
        { identifier: 'dismiss', title: 'Dismiss' },
      ],
      data: {
        type: 'disruption',
        route,
        severity,
        message,
        alternativeRoutes,
      },
    });
  }

  async showFareUpdateNotification(
    route: string,
    oldPrice: number,
    newPrice: number,
    reason?: string
  ): Promise<string> {
    const change = newPrice > oldPrice ? 'increased' : 'decreased';
    const emoji = newPrice > oldPrice ? '📈' : '📉';
    const changePercent = Math.round(((newPrice - oldPrice) / oldPrice) * 100);

    return this.showRichNotification({
      title: `${emoji} Fare Update`,
      body: `${route} fare ${change} by ${Math.abs(changePercent)}% (LKR ${oldPrice} → LKR ${newPrice})`,
      priority: 'normal',
      actions: [
        { identifier: 'view_details', title: 'View Details' },
        { identifier: 'save_route', title: 'Save Route' },
      ],
      data: {
        type: 'fare_update',
        route,
        oldPrice,
        newPrice,
        change,
        reason,
      },
    });
  }

  async showWeatherImpactAlert(
    area: string,
    weatherCondition: string,
    impact: string,
    weatherIconUrl?: string
  ): Promise<string> {
    return this.showRichNotification({
      title: `🌧️ Weather Alert - ${area}`,
      body: `${weatherCondition} may cause ${impact}`,
      imageUrl: weatherIconUrl,
      priority: 'normal',
      actions: [
        { identifier: 'find_alternative', title: 'Plan Alternative' },
        { identifier: 'dismiss', title: 'Got It' },
      ],
      data: {
        type: 'weather_impact',
        area,
        weatherCondition,
        impact,
      },
    });
  }

  async showJourneyReminder(
    journeyName: string,
    departureTime: string,
    estimatedDuration: string,
    routeImageUrl?: string
  ): Promise<string> {
    return this.showRichNotification({
      title: '🕒 Journey Reminder',
      body: `${journeyName} departs in 15 minutes (${departureTime}, ${estimatedDuration} trip)`,
      imageUrl: routeImageUrl,
      priority: 'high',
      sound: 'default',
      actions: [
        { identifier: 'snooze', title: 'Snooze 10min' },
        { identifier: 'plan_journey', title: 'Update Route' },
      ],
      data: {
        type: 'journey_reminder',
        journeyName,
        departureTime,
        estimatedDuration,
      },
    });
  }

  async showCongestionAlert(
    route: string,
    congestionLevel: 'light' | 'moderate' | 'heavy',
    estimatedDelay: string,
    alternativeTime?: string
  ): Promise<string> {
    const emoji = congestionLevel === 'heavy' ? '🚗💨' : '🚙';
    const color = congestionLevel === 'heavy' ? 'red' : congestionLevel === 'moderate' ? 'orange' : 'yellow';

    return this.showRichNotification({
      title: `${emoji} Traffic Update`,
      body: `${route} has ${congestionLevel} congestion (+${estimatedDelay} delay)${alternativeTime ? `. Alternative route: ${alternativeTime}` : ''}`,
      priority: congestionLevel === 'heavy' ? 'high' : 'normal',
      actions: [
        { identifier: 'find_alternative', title: 'Find Alternative' },
        { identifier: 'view_route', title: 'View on Map' },
      ],
      data: {
        type: 'congestion',
        route,
        congestionLevel,
        estimatedDelay,
        alternativeTime,
      },
    });
  }

  async showPromotionNotification(
    title: string,
    description: string,
    discountPercent: number,
    validUntil: string,
    promoImageUrl?: string
  ): Promise<string> {
    return this.showRichNotification({
      title: `🎉 ${title}`,
      body: `${description} - ${discountPercent}% off! Valid until ${validUntil}`,
      imageUrl: promoImageUrl,
      priority: 'low',
      actions: [
        { identifier: 'view_details', title: 'View Offer' },
        { identifier: 'dismiss', title: 'Not Now' },
      ],
      data: {
        type: 'promotion',
        title,
        description,
        discountPercent,
        validUntil,
      },
    });
  }

  // Cleanup cached images periodically
  async cleanupCache(): Promise<void> {
    try {
      const cacheDir = `${FileSystem.cacheDirectory}notifications/`;
      const files = await FileSystem.readDirectoryAsync(cacheDir);
      
      const now = Date.now();
      const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
      
      for (const file of files) {
        const filePath = `${cacheDir}${file}`;
        const info = await FileSystem.getInfoAsync(filePath);
        
        if (info.exists && info.modificationTime) {
          const age = now - info.modificationTime;
          if (age > maxAge) {
            await FileSystem.deleteAsync(filePath);
            console.log('Deleted old cached notification image:', file);
          }
        }
      }
      
      // Clear in-memory cache
      this.cachedImages.clear();
    } catch (error) {
      console.error('Failed to cleanup notification cache:', error);
    }
  }
}

export const richNotificationService = new RichNotificationService();