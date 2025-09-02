import NetInfo from '@react-native-community/netinfo';
import { storageService } from './storage';
import { apiService } from './api';
import { notificationService } from './notifications';
import { APP_CONFIG } from '@/constants/Config';

interface SyncQueue {
  id: string;
  type: 'journey' | 'favorite' | 'profile' | 'location' | 'feedback';
  action: 'create' | 'update' | 'delete';
  data: any;
  timestamp: number;
  retries: number;
}

interface OfflineSyncState {
  isOnline: boolean;
  isSyncing: boolean;
  lastSyncTime: number;
  pendingSync: number;
  syncQueue: SyncQueue[];
}

class OfflineSyncService {
  private syncState: OfflineSyncState = {
    isOnline: false,
    isSyncing: false,
    lastSyncTime: 0,
    pendingSync: 0,
    syncQueue: [],
  };

  private listeners: ((state: OfflineSyncState) => void)[] = [];
  private syncInterval: NodeJS.Timeout | null = null;

  async initialize(): Promise<void> {
    try {
      // Load sync state from storage
      const savedState = await this.loadSyncState();
      if (savedState) {
        this.syncState = { ...this.syncState, ...savedState };
      }

      // Set up network monitoring
      NetInfo.addEventListener((state) => {
        const wasOnline = this.syncState.isOnline;
        this.syncState.isOnline = state.isConnected || false;
        
        // If we just came back online, trigger sync
        if (!wasOnline && this.syncState.isOnline && this.syncState.syncQueue.length > 0) {
          console.log('Network restored, starting sync...');
          this.syncPendingData();
        }
        
        this.notifyListeners();
      });

      // Check initial network state
      const netState = await NetInfo.fetch();
      this.syncState.isOnline = netState.isConnected || false;

      // Start periodic sync when online
      this.startPeriodicSync();

      console.log('Offline sync service initialized');
    } catch (error) {
      console.error('Failed to initialize offline sync service:', error);
    }
  }

  private async loadSyncState(): Promise<Partial<OfflineSyncState> | null> {
    try {
      const stateString = await storageService.getSyncState();
      return stateString ? JSON.parse(stateString) : null;
    } catch (error) {
      console.error('Failed to load sync state:', error);
      return null;
    }
  }

  private async saveSyncState(): Promise<void> {
    try {
      await storageService.setSyncState(JSON.stringify({
        lastSyncTime: this.syncState.lastSyncTime,
        syncQueue: this.syncState.syncQueue,
      }));
    } catch (error) {
      console.error('Failed to save sync state:', error);
    }
  }

  private startPeriodicSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }

    this.syncInterval = setInterval(() => {
      if (this.syncState.isOnline && this.syncState.syncQueue.length > 0) {
        this.syncPendingData();
      }
    }, APP_CONFIG.OFFLINE_SYNC_INTERVAL);
  }

  addListener(listener: (state: OfflineSyncState) => void): () => void {
    this.listeners.push(listener);
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener({ ...this.syncState }));
  }

  getSyncState(): OfflineSyncState {
    return { ...this.syncState };
  }

  // Queue operations for sync
  async queueOperation(
    type: SyncQueue['type'],
    action: SyncQueue['action'],
    data: any
  ): Promise<void> {
    const operation: SyncQueue = {
      id: `${type}_${action}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      action,
      data,
      timestamp: Date.now(),
      retries: 0,
    };

    this.syncState.syncQueue.push(operation);
    this.syncState.pendingSync = this.syncState.syncQueue.length;
    
    await this.saveSyncState();
    this.notifyListeners();

    // Try to sync immediately if online
    if (this.syncState.isOnline) {
      this.syncPendingData();
    }
  }

  // Manual sync trigger
  async syncNow(): Promise<{ success: boolean; synced: number; failed: number }> {
    if (!this.syncState.isOnline) {
      throw new Error('No internet connection');
    }

    return await this.syncPendingData();
  }

  private async syncPendingData(): Promise<{ success: boolean; synced: number; failed: number }> {
    if (this.syncState.isSyncing || this.syncState.syncQueue.length === 0) {
      return { success: true, synced: 0, failed: 0 };
    }

    this.syncState.isSyncing = true;
    this.notifyListeners();

    let syncedCount = 0;
    let failedCount = 0;
    const itemsToSync = [...this.syncState.syncQueue];

    console.log(`Starting sync of ${itemsToSync.length} items...`);

    for (let i = 0; i < itemsToSync.length; i++) {
      const item = itemsToSync[i];
      
      try {
        const success = await this.syncSingleItem(item);
        
        if (success) {
          // Remove from queue
          this.syncState.syncQueue = this.syncState.syncQueue.filter(q => q.id !== item.id);
          syncedCount++;
          console.log(`Synced: ${item.type} ${item.action}`);
        } else {
          // Increment retry count
          const queueIndex = this.syncState.syncQueue.findIndex(q => q.id === item.id);
          if (queueIndex !== -1) {
            this.syncState.syncQueue[queueIndex].retries++;
            
            // Remove if too many retries
            if (this.syncState.syncQueue[queueIndex].retries >= 5) {
              this.syncState.syncQueue.splice(queueIndex, 1);
              console.log(`Removed failed item after 5 retries: ${item.type} ${item.action}`);
            }
          }
          failedCount++;
        }
      } catch (error) {
        console.error(`Sync error for ${item.type} ${item.action}:`, error);
        failedCount++;
      }
    }

    this.syncState.isSyncing = false;
    this.syncState.lastSyncTime = Date.now();
    this.syncState.pendingSync = this.syncState.syncQueue.length;

    await this.saveSyncState();
    this.notifyListeners();

    console.log(`Sync completed: ${syncedCount} synced, ${failedCount} failed`);

    // Show notification if there were sync results
    if (syncedCount > 0) {
      await notificationService.showJourneyUpdate(
        'Data Synced',
        `${syncedCount} items synced successfully`,
        { type: 'sync_complete', count: syncedCount }
      );
    }

    return { success: failedCount === 0, synced: syncedCount, failed: failedCount };
  }

  private async syncSingleItem(item: SyncQueue): Promise<boolean> {
    try {
      switch (item.type) {
        case 'journey':
          return await this.syncJourney(item);
        case 'favorite':
          return await this.syncFavorite(item);
        case 'profile':
          return await this.syncProfile(item);
        case 'location':
          return await this.syncLocation(item);
        case 'feedback':
          return await this.syncFeedback(item);
        default:
          console.warn(`Unknown sync type: ${item.type}`);
          return false;
      }
    } catch (error) {
      console.error(`Sync item error:`, error);
      return false;
    }
  }

  private async syncJourney(item: SyncQueue): Promise<boolean> {
    try {
      if (item.action === 'create') {
        // Add journey to history on server
        await apiService.addJourneyToHistory(item.data);
        return true;
      }
      return true;
    } catch (error) {
      console.error('Journey sync error:', error);
      return false;
    }
  }

  private async syncFavorite(item: SyncQueue): Promise<boolean> {
    try {
      if (item.action === 'create') {
        await apiService.addToFavorites(item.data.journeyId);
      } else if (item.action === 'delete') {
        await apiService.removeFromFavorites(item.data.journeyId);
      }
      return true;
    } catch (error) {
      console.error('Favorite sync error:', error);
      return false;
    }
  }

  private async syncProfile(item: SyncQueue): Promise<boolean> {
    try {
      if (item.action === 'update') {
        await apiService.updateProfile(item.data);
      }
      return true;
    } catch (error) {
      console.error('Profile sync error:', error);
      return false;
    }
  }

  private async syncLocation(item: SyncQueue): Promise<boolean> {
    try {
      if (item.action === 'update') {
        await apiService.updateLocation(item.data);
      }
      return true;
    } catch (error) {
      console.error('Location sync error:', error);
      return false;
    }
  }

  private async syncFeedback(item: SyncQueue): Promise<boolean> {
    try {
      if (item.action === 'create') {
        await apiService.submitFeedback(item.data);
      }
      return true;
    } catch (error) {
      console.error('Feedback sync error:', error);
      return false;
    }
  }

  // Download data for offline use
  async downloadOfflineData(): Promise<{ success: boolean; size: number }> {
    try {
      console.log('Downloading offline data...');
      
      // Download essential data
      const [routes, locations, appConfig] = await Promise.all([
        apiService.getPopularRoutes().catch(() => []),
        apiService.getPopularLocations().catch(() => []),
        apiService.getAppConfig().catch(() => ({})),
      ]);

      const offlineData = {
        routes,
        locations,
        appConfig,
        downloadTime: Date.now(),
      };

      await storageService.storeOfflineData(offlineData);
      
      const size = JSON.stringify(offlineData).length;
      console.log(`Offline data downloaded: ${size} bytes`);

      return { success: true, size };
    } catch (error) {
      console.error('Failed to download offline data:', error);
      return { success: false, size: 0 };
    }
  }

  // Clear offline data
  async clearOfflineData(): Promise<void> {
    try {
      await storageService.clearOfflineData();
      console.log('Offline data cleared');
    } catch (error) {
      console.error('Failed to clear offline data:', error);
    }
  }

  // Get offline data size
  async getOfflineDataSize(): Promise<number> {
    try {
      const data = await storageService.getOfflineData();
      return data ? JSON.stringify(data).length : 0;
    } catch (error) {
      return 0;
    }
  }

  // Force full sync
  async forceFullSync(): Promise<void> {
    try {
      // Clear existing queue and start fresh
      this.syncState.syncQueue = [];
      this.syncState.lastSyncTime = 0;
      
      // Download fresh offline data
      await this.downloadOfflineData();
      
      // Upload any local changes
      await this.uploadLocalChanges();
      
      this.syncState.lastSyncTime = Date.now();
      await this.saveSyncState();
      this.notifyListeners();
      
      console.log('Full sync completed');
    } catch (error) {
      console.error('Full sync failed:', error);
      throw error;
    }
  }

  private async uploadLocalChanges(): Promise<void> {
    // Upload recent journeys, favorites changes, etc.
    // This is a simplified version - in production you'd track what needs uploading
    try {
      const [history, favorites] = await Promise.all([
        storageService.getHistory(),
        storageService.getFavorites(),
      ]);

      // Upload recent history items
      const recentHistory = history.filter(h => 
        Date.now() - new Date(h.timestamp).getTime() < 24 * 60 * 60 * 1000 // Last 24 hours
      );

      for (const journey of recentHistory) {
        await this.queueOperation('journey', 'create', journey);
      }

      console.log('Local changes queued for upload');
    } catch (error) {
      console.error('Failed to upload local changes:', error);
    }
  }

  destroy(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
    this.listeners = [];
  }
}

export const offlineSyncService = new OfflineSyncService();