// Mock notification service for Expo Go compatibility

class MockNotificationService {
  private expoPushToken: string | null = null;

  async initialize(): Promise<boolean> {
    console.log('[Mock] Push notifications not available in Expo Go');
    return false;
  }

  async registerToken(token: string): Promise<void> {
    console.log('[Mock] Would register push token:', token);
  }

  async scheduleJourneyReminder(
    title: string, 
    body: string, 
    triggerDate: Date,
    data?: any
  ): Promise<string> {
    console.log(`[Mock] Would schedule reminder: ${title} - ${body} at ${triggerDate.toISOString()}`);
    return 'mock-reminder-id';
  }

  async showDisruptionAlert(
    route: string,
    severity: 'low' | 'medium' | 'high',
    message: string,
    data?: any
  ): Promise<void> {
    console.log(`[Mock] Would show disruption alert: ${route} (${severity}) - ${message}`);
  }

  async showJourneyUpdate(
    title: string,
    body: string,
    data?: any
  ): Promise<void> {
    console.log(`[Mock] Would show journey update: ${title} - ${body}`);
  }

  async cancelScheduledNotification(identifier: string): Promise<void> {
    console.log('[Mock] Would cancel notification:', identifier);
  }

  async cancelAllScheduledNotifications(): Promise<void> {
    console.log('[Mock] Would cancel all notifications');
  }

  async getBadgeCount(): Promise<number> {
    return 0;
  }

  async setBadgeCount(count: number): Promise<void> {
    console.log('[Mock] Would set badge count to:', count);
  }

  async clearBadge(): Promise<void> {
    console.log('[Mock] Would clear badge');
  }

  addNotificationReceivedListener(listener: Function) {
    console.log('[Mock] Would add received listener');
    return { remove: () => console.log('[Mock] Would remove received listener') };
  }

  addNotificationResponseReceivedListener(listener: Function) {
    console.log('[Mock] Would add response listener');
    return { remove: () => console.log('[Mock] Would remove response listener') };
  }

  async notifyRouteChange(
    origin: string, 
    destination: string, 
    newDuration: string,
    reason: string
  ): Promise<void> {
    console.log(`[Mock] Route change: ${origin} → ${destination}: ${newDuration} (${reason})`);
  }

  async notifyPriceChange(
    route: string, 
    oldPrice: number, 
    newPrice: number
  ): Promise<void> {
    console.log(`[Mock] Price change: ${route} LKR ${oldPrice} → LKR ${newPrice}`);
  }

  async notifyWeatherImpact(
    area: string,
    condition: string,
    impact: string
  ): Promise<void> {
    console.log(`[Mock] Weather impact: ${area} - ${condition} may cause ${impact}`);
  }

  getExpoPushToken(): string | null {
    return this.expoPushToken;
  }
}

export const mockNotificationService = new MockNotificationService();