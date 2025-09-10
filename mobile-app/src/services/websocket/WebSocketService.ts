// =============================================================================
// WEBSOCKET SERVICE - Real-time Updates and Live Data
// =============================================================================

import { API_CONFIG } from '../api/config';
import { Platform } from 'react-native';

export interface WebSocketMessage {
  type: 'route_update' | 'disruption_alert' | 'traffic_update' | 'fare_change' | 'agent_progress' | 'community_report';
  data: any;
  timestamp: string;
  user_id?: string;
  route_id?: string;
}

export interface WebSocketSubscription {
  id: string;
  type: string;
  callback: (message: WebSocketMessage) => void;
  filters?: Record<string, any>;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private subscriptions: Map<string, WebSocketSubscription> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 5000; // 5 seconds
  private heartbeatInterval: any = null;
  private isConnecting = false;
  private userId: string | null = null;

  // =============================================================================
  // CONNECTION MANAGEMENT
  // =============================================================================

  async connect(userId?: string, token?: string): Promise<boolean> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return true;
    }

    if (this.isConnecting) {
      console.log('WebSocket connection already in progress');
      return false;
    }

    try {
      this.isConnecting = true;
      this.userId = userId || null;
      
      // Get token from secure storage if not provided
      if (!token && userId) {
        const { getStoredToken } = await import('../api/client');
        const apiClient = (await import('../api/client')).apiClient;
        token = await apiClient.getStoredToken();
      }
      
      if (!token) {
        throw new Error('Authentication token required for WebSocket connection');
      }
      
      const wsUrl = `${API_CONFIG.WS_URL}?token=${encodeURIComponent(token)}`;
      console.log('Connecting to WebSocket:', wsUrl);

      // Use native WebSocket (React Native has built-in WebSocket support)
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();

      // Wait for connection
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, 10000);

        this.ws!.onopen = () => {
          clearTimeout(timeout);
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          console.log('WebSocket connected successfully');
          resolve(true);
        };

        this.ws!.onerror = (error) => {
          clearTimeout(timeout);
          this.isConnecting = false;
          console.error('WebSocket connection error:', error);
          reject(error);
        };
      });
    } catch (error) {
      this.isConnecting = false;
      console.error('Error connecting to WebSocket:', error);
      return false;
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onmessage = this.handleMessage.bind(this);
    this.ws.onclose = this.handleClose.bind(this);
    this.ws.onerror = this.handleError.bind(this);
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      console.log('WebSocket message received:', message.type);
      
      // Dispatch message to relevant subscriptions
      this.subscriptions.forEach((subscription) => {
        if (this.messageMatchesSubscription(message, subscription)) {
          subscription.callback(message);
        }
      });
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket connection closed:', event.code, event.reason);
    this.stopHeartbeat();
    
    if (event.code !== 1000) { // Not a normal closure
      this.attemptReconnect();
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error);
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(async () => {
      try {
        await this.connect(this.userId || undefined);
      } catch (error) {
        console.error('Reconnection failed:', error);
      }
    }, this.reconnectInterval * this.reconnectAttempts);
  }

  disconnect(): void {
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.subscriptions.clear();
    this.reconnectAttempts = 0;
  }

  // =============================================================================
  // HEARTBEAT MECHANISM
  // =============================================================================

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.sendMessage({ type: 'ping', data: {} });
      }
    }, 30000); // 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  // =============================================================================
  // SUBSCRIPTION MANAGEMENT
  // =============================================================================

  subscribe(
    type: string,
    callback: (message: WebSocketMessage) => void,
    filters?: Record<string, any>
  ): string {
    const subscriptionId = `${type}_${Date.now()}_${Math.random()}`;
    
    const subscription: WebSocketSubscription = {
      id: subscriptionId,
      type,
      callback,
      filters
    };

    this.subscriptions.set(subscriptionId, subscription);
    
    // Send subscription message to server
    this.sendMessage({
      type: 'subscribe',
      data: {
        subscription_type: type,
        filters: filters || {}
      }
    });

    console.log(`Subscribed to ${type} with ID: ${subscriptionId}`);
    return subscriptionId;
  }

  unsubscribe(subscriptionId: string): boolean {
    const subscription = this.subscriptions.get(subscriptionId);
    if (!subscription) {
      return false;
    }

    // Send unsubscribe message to server
    this.sendMessage({
      type: 'unsubscribe',
      data: {
        subscription_id: subscriptionId,
        subscription_type: subscription.type
      }
    });

    this.subscriptions.delete(subscriptionId);
    console.log(`Unsubscribed from ${subscriptionId}`);
    return true;
  }

  private messageMatchesSubscription(
    message: WebSocketMessage,
    subscription: WebSocketSubscription
  ): boolean {
    // Check if message type matches subscription
    if (message.type !== subscription.type) {
      return false;
    }

    // Check filters if they exist
    if (subscription.filters) {
      for (const [key, value] of Object.entries(subscription.filters)) {
        if (message.data[key] !== value) {
          return false;
        }
      }
    }

    return true;
  }

  // =============================================================================
  // SPECIALIZED SUBSCRIPTIONS
  // =============================================================================

  subscribeToRouteUpdates(
    routeId: string,
    callback: (update: any) => void
  ): string {
    return this.subscribe('route_update', (message) => {
      callback(message.data);
    }, { route_id: routeId });
  }

  subscribeToDisruptions(
    callback: (disruption: any) => void,
    area?: string
  ): string {
    return this.subscribe('disruption_alert', (message) => {
      callback(message.data);
    }, area ? { area } : undefined);
  }

  subscribeToTrafficUpdates(
    location: string,
    callback: (traffic: any) => void
  ): string {
    return this.subscribe('traffic_update', (message) => {
      callback(message.data);
    }, { location });
  }

  subscribeToFareChanges(
    callback: (fareChange: any) => void,
    transportType?: string
  ): string {
    return this.subscribe('fare_change', (message) => {
      callback(message.data);
    }, transportType ? { transport_type: transportType } : undefined);
  }

  subscribeToAgentProgress(
    requestId: string,
    callback: (progress: any) => void
  ): string {
    return this.subscribe('agent_progress', (message) => {
      callback(message.data);
    }, { request_id: requestId });
  }

  subscribeToCommunityReports(
    callback: (report: any) => void,
    area?: string
  ): string {
    return this.subscribe('community_report', (message) => {
      callback(message.data);
    }, area ? { area } : undefined);
  }

  // =============================================================================
  // MESSAGE SENDING
  // =============================================================================

  private sendMessage(message: any): boolean {
    if (this.isConnected()) {
      try {
        this.ws!.send(JSON.stringify({
          ...message,
          timestamp: new Date().toISOString(),
          user_id: this.userId
        }));
        return true;
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
        return false;
      }
    }
    
    console.warn('WebSocket not connected, cannot send message');
    return false;
  }

  sendRouteTrackingStart(routeId: string): boolean {
    return this.sendMessage({
      type: 'start_tracking',
      data: { route_id: routeId }
    });
  }

  sendRouteTrackingStop(routeId: string): boolean {
    return this.sendMessage({
      type: 'stop_tracking',
      data: { route_id: routeId }
    });
  }

  sendLocationUpdate(latitude: number, longitude: number): boolean {
    return this.sendMessage({
      type: 'location_update',
      data: { latitude, longitude }
    });
  }

  // =============================================================================
  // CONNECTION STATUS
  // =============================================================================

  isConnected(): boolean {
    if (!this.ws) return false;
    const OPEN = Platform.OS === 'web' ? WebSocket.OPEN : 1;
    return this.ws.readyState === OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    
    const states = Platform.OS === 'web' 
      ? { CONNECTING: WebSocket.CONNECTING, OPEN: WebSocket.OPEN, CLOSING: WebSocket.CLOSING, CLOSED: WebSocket.CLOSED }
      : { CONNECTING: 0, OPEN: 1, CLOSING: 2, CLOSED: 3 };
    
    switch (this.ws.readyState) {
      case states.CONNECTING:
        return 'connecting';
      case states.OPEN:
        return 'connected';
      case states.CLOSING:
        return 'closing';
      case states.CLOSED:
        return 'closed';
      default:
        return 'unknown';
    }
  }

  getSubscriptionCount(): number {
    return this.subscriptions.size;
  }

  getActiveSubscriptions(): string[] {
    return Array.from(this.subscriptions.values()).map(sub => `${sub.type}:${sub.id}`);
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  async waitForConnection(timeout: number = 5000): Promise<boolean> {
    if (this.isConnected()) {
      return true;
    }

    return new Promise((resolve) => {
      const startTime = Date.now();
      const checkInterval = setInterval(() => {
        if (this.isConnected()) {
          clearInterval(checkInterval);
          resolve(true);
        } else if (Date.now() - startTime > timeout) {
          clearInterval(checkInterval);
          resolve(false);
        }
      }, 100);
    });
  }

  getStats(): {
    connected: boolean;
    subscriptions: number;
    reconnectAttempts: number;
    connectionState: string;
  } {
    return {
      connected: this.isConnected(),
      subscriptions: this.getSubscriptionCount(),
      reconnectAttempts: this.reconnectAttempts,
      connectionState: this.getConnectionState()
    };
  }
}

export const webSocketService = new WebSocketService();
export default webSocketService;