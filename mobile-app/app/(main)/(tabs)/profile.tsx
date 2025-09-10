import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Switch, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import ThemeToggle, { ThemePreview } from '../../components/ThemeToggle';
import { useTheme, ThemeMode } from '../../../src/contexts/ThemeContext';
import { useAuth } from '../../../src/contexts/AppContext';
import { authService } from '../../../src/services/api/authService';
import { useLanguage } from '../../../src/contexts/LanguageContext';

export default function Profile() {
  const { theme, mode, setTheme, isDark } = useTheme();
  const { user: authUser, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  
  // Use real user data from authentication context
  const user = {
    name: authUser?.name || 'User',
    email: authUser?.email || 'user@example.com',
    phone: authUser?.profile?.phone || 'Not provided',
    preferredLanguage: authUser?.profile?.preferred_language || 'en',
    memberSince: authUser?.created_at ? new Date(authUser.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) : 'Recently'
  };

  const [preferences, setPreferences] = useState({
    notifications: {
      delays: true,
      offers: true,
      reminders: true,
      community: false
    },
    privacy: {
      shareLocation: true,
      shareReports: true,
      analytics: true
    }
  });

  const [stats, setStats] = useState({
    totalTrips: authUser?.profile?.stats?.totalTrips || 0,
    distanceTraveled: authUser?.profile?.stats?.distanceTraveled || 0,
    moneySaved: authUser?.profile?.stats?.moneySaved || 0,
    carbonReduced: authUser?.profile?.stats?.carbonReduced || 0,
    communityReports: authUser?.profile?.stats?.communityReports || 0,
    helpfulVotes: authUser?.profile?.stats?.helpfulVotes || 0
  });

  const languageOptions = [
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'si', label: 'සිංහල', flag: '🇱🇰' },
    { code: 'ta', label: 'தமிழ்', flag: '🇱🇰' }
  ];

  const toggleNotification = (type: keyof typeof preferences.notifications) => {
    setPreferences(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [type]: !prev.notifications[type]
      }
    }));
  };

  const togglePrivacy = (type: keyof typeof preferences.privacy) => {
    setPreferences(prev => ({
      ...prev,
      privacy: {
        ...prev.privacy,
        [type]: !prev.privacy[type]
      }
    }));
  };

  const handleLanguageChange = async (languageCode: string) => {
    try {
      const selectedLang = languageOptions.find(l => l.code === languageCode);
      if (!selectedLang) return;
      
      // Update language in context (immediate effect)
      await setLanguage(languageCode as any);
      
      // Also update user profile via API
      try {
        await authService.updateProfile({ 
          preferred_language: languageCode 
        });
      } catch (error) {
        console.error('Failed to update profile, but language changed locally:', error);
      }
      
      Alert.alert(
        t('common.success'), 
        `App language changed to ${selectedLang.label}`,
        [{ text: t('common.ok') }]
      );
    } catch (error) {
      console.error('Language update error:', error);
      Alert.alert(t('common.error'), 'Failed to update language preference. Please try again.');
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Logout', 
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/(auth)/login');
          }
        }
      ]
    );
  };

  return (
    <SafeAreaView className="flex-1" style={{ backgroundColor: theme.background }}>
      <ScrollView className="flex-1">
        {/* Header */}
        <View className="p-6" style={{ backgroundColor: theme.primary }}>
          <View className="flex-row items-center">
            <View className="w-16 h-16 bg-blue-500 rounded-full items-center justify-center mr-4">
              <Text className="text-white text-2xl font-bold">
                {user.name.split(' ').map(n => n[0]).join('')}
              </Text>
            </View>
            <View className="flex-1">
              <Text className="text-white text-xl font-bold">{user.name}</Text>
              <Text className="text-blue-100 text-sm">{user.email}</Text>
              <Text className="text-blue-200 text-xs">Member since {user.memberSince}</Text>
            </View>
            <TouchableOpacity className="p-2">
              <Ionicons name="pencil" size={20} color="white" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Stats Cards */}
        <View className="px-4 mt-4 mb-6">
          <View className="rounded-lg shadow-sm p-4" style={{ backgroundColor: theme.surface }}>
            <Text className="text-lg font-semibold mb-4" style={{ color: theme.text }}>{t('profile.impact')}</Text>
            <View className="flex-row flex-wrap">
              <View className="w-1/2 p-2">
                <View className="bg-blue-50 p-3 rounded-lg items-center">
                  <Text className="text-2xl font-bold text-blue-600">{stats.totalTrips}</Text>
                  <Text className="text-xs text-gray-600 text-center">Total Trips</Text>
                </View>
              </View>
              <View className="w-1/2 p-2">
                <View className="bg-green-50 p-3 rounded-lg items-center">
                  <Text className="text-2xl font-bold text-green-600">{stats.distanceTraveled}</Text>
                  <Text className="text-xs text-gray-600 text-center">km Traveled</Text>
                </View>
              </View>
              <View className="w-1/2 p-2">
                <View className="bg-purple-50 p-3 rounded-lg items-center">
                  <Text className="text-2xl font-bold text-purple-600">Rs. {stats.moneySaved}</Text>
                  <Text className="text-xs text-gray-600 text-center">Money Saved</Text>
                </View>
              </View>
              <View className="w-1/2 p-2">
                <View className="bg-orange-50 p-3 rounded-lg items-center">
                  <Text className="text-2xl font-bold text-orange-600">{stats.carbonReduced}</Text>
                  <Text className="text-xs text-gray-600 text-center">kg CO₂ Reduced</Text>
                </View>
              </View>
            </View>
          </View>
        </View>

        {/* Theme Settings */}
        <View
          className="mx-4 rounded-lg shadow-sm p-4 mb-4"
          style={{ backgroundColor: theme.surface }}
        >
          <Text
            className="text-lg font-semibold mb-3"
            style={{ color: theme.text }}
          >
            {t('profile.appearance')}
          </Text>
          
          <View>
            <Text className="text-sm font-medium mb-3" style={{ color: theme.textSecondary }}>
              Choose your preferred theme
            </Text>
            <View className="flex-row space-x-4">
              <TouchableOpacity
                className="flex-1 p-4 rounded-lg border-2"
                style={{
                  backgroundColor: mode === 'light' ? '#EBF8FF' : theme.surface,
                  borderColor: mode === 'light' ? theme.primary : theme.border
                }}
                onPress={() => setTheme('light')}
              >
                <View className="items-center">
                  <View className="w-12 h-12 bg-white border rounded-lg mb-2 items-center justify-center">
                    <Ionicons name="sunny" size={24} color="#F59E0B" />
                  </View>
                  <Text
                    className="font-medium"
                    style={{
                      color: mode === 'light' ? theme.primary : theme.text
                    }}
                  >
                    Light
                  </Text>
                </View>
              </TouchableOpacity>
              
              <TouchableOpacity
                className="flex-1 p-4 rounded-lg border-2"
                style={{
                  backgroundColor: mode === 'dark' ? '#1E293B' : theme.surface,
                  borderColor: mode === 'dark' ? theme.primary : theme.border
                }}
                onPress={() => setTheme('dark')}
              >
                <View className="items-center">
                  <View className="w-12 h-12 bg-gray-800 border rounded-lg mb-2 items-center justify-center">
                    <Ionicons name="moon" size={24} color="#8B5CF6" />
                  </View>
                  <Text
                    className="font-medium"
                    style={{
                      color: mode === 'dark' ? theme.primary : theme.text
                    }}
                  >
                    Dark
                  </Text>
                </View>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Language Settings */}
        <View
          className="mx-4 rounded-lg shadow-sm p-4 mb-4"
          style={{ backgroundColor: theme.surface }}
        >
          <Text
            className="text-lg font-semibold mb-3"
            style={{ color: theme.text }}
          >
            {t('profile.language')}
          </Text>
          <View className="space-y-3">
            {languageOptions.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                className="flex-row items-center p-3 rounded-lg"
                style={{
                  backgroundColor: language === lang.code 
                    ? (isDark ? theme.primary + '20' : '#EBF8FF')
                    : (isDark ? theme.card : '#F9FAFB'),
                  borderWidth: language === lang.code ? 1 : 0,
                  borderColor: theme.primary
                }}
                onPress={() => handleLanguageChange(lang.code)}
              >
                <Text className="text-2xl mr-3">{lang.flag}</Text>
                <Text
                  className="flex-1 font-medium"
                  style={{
                    color: language === lang.code 
                      ? theme.primary 
                      : theme.text
                  }}
                >
                  {lang.label}
                </Text>
                {language === lang.code && (
                  <Ionicons name="checkmark-circle" size={20} color={theme.primary} />
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Notification Settings */}
        <View
          className="mx-4 rounded-lg shadow-sm p-4 mb-4"
          style={{ backgroundColor: theme.surface }}
        >
          <Text
            className="text-lg font-semibold mb-3"
            style={{ color: theme.text }}
          >
            Notifications
          </Text>
          <View className="space-y-3">
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-base" style={{ color: theme.text }}>Delay alerts</Text>
                <Text className="text-sm" style={{ color: theme.textSecondary }}>Get notified about transport delays</Text>
              </View>
              <Switch
                value={preferences.notifications.delays}
                onValueChange={() => toggleNotification('delays')}
              />
            </View>
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-base" style={{ color: theme.text }}>Fare offers</Text>
                <Text className="text-sm" style={{ color: theme.textSecondary }}>Receive deals and discounts</Text>
              </View>
              <Switch
                value={preferences.notifications.offers}
                onValueChange={() => toggleNotification('offers')}
              />
            </View>
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-base" style={{ color: theme.text }}>Journey reminders</Text>
                <Text className="text-sm" style={{ color: theme.textSecondary }}>Reminders for planned trips</Text>
              </View>
              <Switch
                value={preferences.notifications.reminders}
                onValueChange={() => toggleNotification('reminders')}
              />
            </View>
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-base" style={{ color: theme.text }}>Community updates</Text>
                <Text className="text-sm" style={{ color: theme.textSecondary }}>New reports and responses</Text>
              </View>
              <Switch
                value={preferences.notifications.community}
                onValueChange={() => toggleNotification('community')}
              />
            </View>
          </View>
        </View>

        {/* Privacy Settings */}
        <View
          className="mx-4 rounded-lg shadow-sm p-4 mb-4"
          style={{ backgroundColor: theme.surface }}
        >
          <Text
            className="text-lg font-semibold mb-3"
            style={{ color: theme.text }}
          >
            Privacy & Data
          </Text>
          <View className="space-y-3">
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-base" style={{ color: theme.text }}>Share location</Text>
                <Text className="text-sm" style={{ color: theme.textSecondary }}>Help improve route suggestions</Text>
              </View>
              <Switch
                value={preferences.privacy.shareLocation}
                onValueChange={() => togglePrivacy('shareLocation')}
              />
            </View>
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-base" style={{ color: theme.text }}>Share community reports</Text>
                <Text className="text-sm" style={{ color: theme.textSecondary }}>Make your reports visible to others</Text>
              </View>
              <Switch
                value={preferences.privacy.shareReports}
                onValueChange={() => togglePrivacy('shareReports')}
              />
            </View>
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-base" style={{ color: theme.text }}>Analytics</Text>
                <Text className="text-sm" style={{ color: theme.textSecondary }}>Help improve the app with usage data</Text>
              </View>
              <Switch
                value={preferences.privacy.analytics}
                onValueChange={() => togglePrivacy('analytics')}
              />
            </View>
          </View>
        </View>

        {/* Menu Options */}
        <View
          className="mx-4 rounded-lg shadow-sm p-4 mb-4"
          style={{ backgroundColor: theme.surface }}
        >
          <View className="space-y-1">
            <TouchableOpacity className="flex-row items-center p-3 rounded-lg">
              <Ionicons name="help-circle-outline" size={24} color="#6b7280" />
              <Text className="flex-1 text-base ml-3" style={{ color: theme.text }}>Help & Support</Text>
              <Ionicons name="chevron-forward" size={20} color="#6b7280" />
            </TouchableOpacity>
            
            <TouchableOpacity className="flex-row items-center p-3 rounded-lg">
              <Ionicons name="document-text-outline" size={24} color="#6b7280" />
              <Text className="flex-1 text-base ml-3" style={{ color: theme.text }}>Terms & Privacy</Text>
              <Ionicons name="chevron-forward" size={20} color="#6b7280" />
            </TouchableOpacity>
            
            <TouchableOpacity className="flex-row items-center p-3 rounded-lg">
              <Ionicons name="star-outline" size={24} color="#6b7280" />
              <Text className="flex-1 text-base ml-3" style={{ color: theme.text }}>Rate the App</Text>
              <Ionicons name="chevron-forward" size={20} color="#6b7280" />
            </TouchableOpacity>
            
            <TouchableOpacity className="flex-row items-center p-3 rounded-lg">
              <Ionicons name="information-circle-outline" size={24} color="#6b7280" />
              <Text className="flex-1 text-base ml-3" style={{ color: theme.text }}>About</Text>
              <Ionicons name="chevron-forward" size={20} color="#6b7280" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Community Stats */}
        <View
          className="mx-4 rounded-lg shadow-sm p-4 mb-4"
          style={{ backgroundColor: theme.surface }}
        >
          <Text
            className="text-lg font-semibold mb-3"
            style={{ color: theme.text }}
          >
            Community Contribution
          </Text>
          <View className="flex-row justify-between">
            <View className="items-center">
              <Text className="text-xl font-bold text-orange-600">{stats.communityReports}</Text>
              <Text className="text-xs" style={{ color: theme.textSecondary }}>Reports</Text>
            </View>
            <View className="items-center">
              <Text className="text-xl font-bold text-blue-600">{stats.helpfulVotes}</Text>
              <Text className="text-xs" style={{ color: theme.textSecondary }}>Helpful Votes</Text>
            </View>
            <View className="items-center">
              <Text className="text-xl font-bold text-green-600">4.8</Text>
              <Text className="text-xs" style={{ color: theme.textSecondary }}>Rating</Text>
            </View>
          </View>
        </View>

        {/* Logout Button */}
        <View className="px-4 mb-8">
          <TouchableOpacity
            className="bg-red-50 border border-red-200 rounded-lg p-4"
            onPress={handleLogout}
          >
            <View className="flex-row items-center justify-center">
              <Ionicons name="log-out-outline" size={20} color="#dc2626" />
              <Text className="text-red-600 font-medium ml-2">Logout</Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* App Version */}
        <View className="px-4 pb-4">
          <Text className="text-center text-xs text-gray-500">
            Transit Companion v1.0.0{'\n'}
            Powered by 10 AI Agents • SLAIC 2025
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}