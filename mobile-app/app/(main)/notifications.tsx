import React, { useState, useEffect, useRef } from 'react';
import { View, Text, ScrollView, TouchableOpacity, RefreshControl, ActivityIndicator, Animated } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useFocusEffect } from 'expo-router';
import { useTheme } from '../../src/contexts/ThemeContext';
import { mobileService } from '../../src/services/api/mobileService';
import { useAuth } from '../../src/contexts/AppContext';

// Try to import notifications, but don't fail if not available (Expo Go limitation)
let Notifications: any = null;
try {
  Notifications = require('expo-notifications');
} catch (error) {
  console.log('Push notifications not available (Expo Go limitation).');
}

interface Notification {
  notification_id: string;
  title: string;
  body: string;
  data?: any;
  read_by?: string[];
  sent_at: string;
  type?: string;
}

export default function NotificationsPage() {
  const { theme } = useTheme();
  const router = useRouter();
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const notificationListener = useRef<any>();
  const fadeAnim = useRef(new Animated.Value(1)).current;

  // Refresh when screen comes into focus
  useFocusEffect(
    React.useCallback(() => {
      loadNotifications();
    }, [])
  );

  useEffect(() => {
    loadNotifications();

    // Real-time notification listener (only if available)
    if (Notifications && Notifications.addNotificationReceivedListener) {
      try {
        notificationListener.current = Notifications.addNotificationReceivedListener(notification => {
          console.log('📬 New notification received on notifications page:', notification);
          // Reload notifications immediately
          loadNotifications();
        });
      } catch (error) {
        console.log('Could not set up notification listener:', error);
      }
    }

    // Polling fallback
    const pollInterval = Notifications ? 30000 : 10000; // 30s with push, 10s without
    const interval = setInterval(loadNotifications, pollInterval);

    return () => {
      if (Notifications && notificationListener.current) {
        try {
          Notifications.removeNotificationSubscription(notificationListener.current);
        } catch (error) {
          console.log('Error removing notification listener:', error);
        }
      }
      clearInterval(interval);
    };
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await mobileService.getNotificationHistory(50);

      if (response.success && response.data) {
        // Backend returns array directly, not nested in notifications property
        const notificationsList = Array.isArray(response.data) ? response.data : [];
        setNotifications(notificationsList);
        // Check if user_id is in read_by array
        const userId = user?.user_id;
        setUnreadCount(
          notificationsList.filter((n: Notification) =>
            !n.read_by || !n.read_by.includes(userId || '')
          ).length
        );
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadNotifications();
  };

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      const userId = user?.user_id;
      if (!userId) return;

      // Optimistically update UI first for instant feedback
      setNotifications(prev =>
        prev.map(n =>
          n.notification_id === notificationId
            ? { ...n, read_by: [...(n.read_by || []), userId] }
            : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));

      // Then send to backend
      await mobileService.markNotificationAsRead(notificationId);
    } catch (error) {
      console.error('Error marking notification as read:', error);
      // Revert on error
      loadNotifications();
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      const userId = user?.user_id;
      if (!userId) return;

      // Animate fade out of unread indicator
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }).start(() => {
        // Update state after animation
        setNotifications(prev =>
          prev.map(n => ({ ...n, read_by: [...(n.read_by || []), userId] }))
        );
        setUnreadCount(0);
        fadeAnim.setValue(1);
      });

      // Send to backend
      await mobileService.markAllNotificationsAsRead();
    } catch (error) {
      console.error('Error marking all as read:', error);
      fadeAnim.setValue(1);
      loadNotifications();
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getNotificationIcon = (type?: string) => {
    switch (type) {
      case 'route':
        return '🚌';
      case 'disruption':
        return '⚠️';
      case 'update':
        return '🔔';
      case 'promotion':
        return '🎉';
      default:
        return '📬';
    }
  };

  return (
    <SafeAreaView className="flex-1" style={{ backgroundColor: theme.background }}>
      {/* Header */}
      <View className="px-6 py-4 border-b" style={{ borderColor: theme.border, backgroundColor: theme.surface }}>
        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center">
            <TouchableOpacity onPress={() => router.back()} className="mr-3">
              <Ionicons name="arrow-back" size={24} color={theme.text} />
            </TouchableOpacity>
            <View>
              <Text className="text-xl font-bold" style={{ color: theme.text }}>
                Notifications
              </Text>
              {unreadCount > 0 && (
                <Text className="text-sm" style={{ color: theme.textSecondary }}>
                  {unreadCount} unread
                </Text>
              )}
            </View>
          </View>
          {unreadCount > 0 && (
            <TouchableOpacity onPress={handleMarkAllAsRead} className="px-3 py-1.5 rounded-lg" style={{ backgroundColor: theme.primary }}>
              <Text className="text-white text-sm font-medium">Mark all read</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Notifications List */}
      {loading ? (
        <View className="flex-1 items-center justify-center">
          <ActivityIndicator size="large" color={theme.primary} />
          <Text className="mt-4" style={{ color: theme.textSecondary }}>Loading notifications...</Text>
        </View>
      ) : (
        <ScrollView
          className="flex-1"
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor={theme.primary}
            />
          }
        >
          {notifications.length === 0 ? (
            <View className="flex-1 items-center justify-center py-20">
              <Text className="text-6xl mb-4">📭</Text>
              <Text className="text-lg font-semibold mb-2" style={{ color: theme.text }}>
                No notifications yet
              </Text>
              <Text className="text-sm" style={{ color: theme.textSecondary }}>
                We'll notify you when something important happens
              </Text>
            </View>
          ) : (
            <View className="p-4">
              {notifications.map((notification) => {
                const userId = user?.user_id;
                const isRead = notification.read_by && notification.read_by.includes(userId || '');

                return (
                  <TouchableOpacity
                    key={notification.notification_id}
                    className="mb-3 p-4 rounded-lg border"
                    style={{
                      backgroundColor: isRead ? theme.surface : `${theme.primary}10`,
                      borderColor: isRead ? theme.border : theme.primary,
                      borderWidth: isRead ? 1 : 2
                    }}
                    onPress={() => !isRead && handleMarkAsRead(notification.notification_id)}
                  >
                    <View className="flex-row items-start">
                      <Text className="text-2xl mr-3">
                        {getNotificationIcon(notification.data?.type || notification.type)}
                      </Text>
                      <View className="flex-1">
                        <View className="flex-row items-center justify-between mb-1">
                          <Text
                            className="text-base font-semibold flex-1"
                            style={{ color: theme.text }}
                          >
                            {notification.title}
                          </Text>
                          {!isRead && (
                            <View className="w-2 h-2 rounded-full ml-2" style={{ backgroundColor: theme.primary }} />
                          )}
                        </View>
                        <Text className="text-sm mb-2" style={{ color: theme.textSecondary }}>
                          {notification.body}
                        </Text>
                        <Text className="text-xs" style={{ color: theme.textTertiary }}>
                          {formatTime(notification.sent_at)}
                        </Text>
                      </View>
                    </View>
                  </TouchableOpacity>
                );
              })}
            </View>
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}
