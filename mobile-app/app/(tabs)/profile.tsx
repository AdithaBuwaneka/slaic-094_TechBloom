import { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  Image,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useApp } from '@/context/AppContext';

export default function ProfileScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { user, theme, language, logout, changeTheme, changeLanguage } = useApp();
  
  const [notifications, setNotifications] = useState({
    disruptions: true,
    updates: true,
    promotions: false,
  });

  const isDark = theme === 'dark';

  const handleLogout = () => {
    console.log('🚪 Logout button pressed');
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel', onPress: () => console.log('❌ Logout cancelled') },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            console.log('✅ Logout confirmed, calling logout function...');
            try {
              await logout();
              console.log('✅ Logout completed successfully');
              // Force navigation to auth screen
              router.replace('/(auth)/welcome');
            } catch (error) {
              console.error('❌ Logout failed:', error);
              Alert.alert('Error', 'Failed to logout. Please try again.');
            }
          },
        },
      ]
    );
  };

  const SettingItem = ({ 
    icon, 
    title, 
    subtitle, 
    onPress, 
    rightElement, 
    isDestructive = false 
  }: any) => (
    <TouchableOpacity
      onPress={onPress}
      className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-4 mb-3 flex-row items-center border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}
    >
      <View className={`w-10 h-10 rounded-full items-center justify-center mr-4 ${
        isDestructive 
          ? 'bg-red-100' 
          : isDark ? 'bg-gray-700' : 'bg-gray-100'
      }`}>
        <Ionicons 
          name={icon} 
          size={20} 
          color={isDestructive ? '#ef4444' : '#6b7280'} 
        />
      </View>
      <View className="flex-1">
        <Text className={`font-semibold ${
          isDestructive 
            ? 'text-red-600' 
            : isDark ? 'text-white' : 'text-gray-900'
        }`}>
          {title}
        </Text>
        {subtitle && (
          <Text className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            {subtitle}
          </Text>
        )}
      </View>
      {rightElement || (
        <Ionicons 
          name="chevron-forward" 
          size={20} 
          color="#6b7280" 
        />
      )}
    </TouchableOpacity>
  );

  const SectionHeader = ({ title }: { title: string }) => (
    <Text className={`text-lg font-semibold mb-3 mt-6 ${isDark ? 'text-white' : 'text-gray-900'}`}>
      {title}
    </Text>
  );

  return (
    <SafeAreaView className={`flex-1 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        {/* Profile Header */}
        <View className="px-6 py-4">
          <View className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-3xl p-6 items-center border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
            <View className="w-24 h-24 rounded-full bg-blue-600 items-center justify-center mb-4">
              {user?.profile_picture ? (
                <Image 
                  source={{ uri: user.profile_picture }} 
                  className="w-full h-full rounded-full" 
                />
              ) : (
                <Text className="text-white text-2xl font-bold">
                  {user?.full_name?.charAt(0) || 'U'}
                </Text>
              )}
            </View>
            <Text className={`text-xl font-bold mb-1 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              {user?.full_name || 'User'}
            </Text>
            <Text className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              {user?.email}
            </Text>
            {user?.phone && (
              <Text className={`text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                {user.phone}
              </Text>
            )}
            
            <TouchableOpacity className="bg-blue-600 rounded-xl py-2 px-6 mt-4">
              <Text className="text-white font-semibold">Edit Profile</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View className="px-6">
          {/* Account Settings */}
          <SectionHeader title={t('profile.personalInfo')} />
          
          <SettingItem
            icon="person-outline"
            title="Personal Information"
            subtitle="Name, email, phone number"
            onPress={() => {}}
          />
          
          <SettingItem
            icon="key-outline"
            title="Change Password"
            subtitle="Update your password"
            onPress={() => {}}
          />

          {/* Preferences */}
          <SectionHeader title={t('profile.travelPreferences')} />
          
          <SettingItem
            icon="globe-outline"
            title={t('profile.language')}
            subtitle={language === 'en' ? 'English' : language === 'si' ? 'සිංහල' : 'தமிழ்'}
            onPress={() => {
              Alert.alert(
                'Select Language',
                'Choose your preferred language',
                [
                  { text: 'English', onPress: () => changeLanguage('en') },
                  { text: 'සිංහල', onPress: () => changeLanguage('si') },
                  { text: 'தமிழ்', onPress: () => changeLanguage('ta') },
                  { text: 'Cancel', style: 'cancel' },
                ]
              );
            }}
          />
          
          <SettingItem
            icon="contrast-outline"
            title={t('profile.theme')}
            subtitle={isDark ? t('profile.darkTheme') : t('profile.lightTheme')}
            rightElement={
              <Switch
                value={isDark}
                onValueChange={(value) => changeTheme(value ? 'dark' : 'light')}
                trackColor={{ false: '#e5e7eb', true: '#3b82f6' }}
                thumbColor={isDark ? '#ffffff' : '#f3f4f6'}
              />
            }
          />
          
          <SettingItem
            icon="bus-outline"
            title={t('profile.preferredTransport')}
            subtitle="Bus, Train, Three Wheeler"
            onPress={() => {}}
          />
          
          <SettingItem
            icon="accessibility-outline"
            title={t('profile.accessibility')}
            subtitle="Accessibility preferences"
            onPress={() => {}}
          />

          {/* Notifications */}
          <SectionHeader title={t('profile.notifications')} />
          
          <SettingItem
            icon="alert-circle-outline"
            title={t('notifications.disruptions')}
            subtitle="Get alerts about service disruptions"
            rightElement={
              <Switch
                value={notifications.disruptions}
                onValueChange={(value) => 
                  setNotifications(prev => ({ ...prev, disruptions: value }))
                }
                trackColor={{ false: '#e5e7eb', true: '#3b82f6' }}
                thumbColor={notifications.disruptions ? '#ffffff' : '#f3f4f6'}
              />
            }
          />
          
          <SettingItem
            icon="refresh-outline"
            title={t('notifications.journeyUpdates')}
            subtitle="Updates about your planned journeys"
            rightElement={
              <Switch
                value={notifications.updates}
                onValueChange={(value) => 
                  setNotifications(prev => ({ ...prev, updates: value }))
                }
                trackColor={{ false: '#e5e7eb', true: '#3b82f6' }}
                thumbColor={notifications.updates ? '#ffffff' : '#f3f4f6'}
              />
            }
          />
          
          <SettingItem
            icon="gift-outline"
            title={t('notifications.promotions')}
            subtitle="Special offers and promotions"
            rightElement={
              <Switch
                value={notifications.promotions}
                onValueChange={(value) => 
                  setNotifications(prev => ({ ...prev, promotions: value }))
                }
                trackColor={{ false: '#e5e7eb', true: '#3b82f6' }}
                thumbColor={notifications.promotions ? '#ffffff' : '#f3f4f6'}
              />
            }
          />

          {/* App Settings */}
          <SectionHeader title={t('settings.appSettings')} />
          
          <SettingItem
            icon="cloud-offline-outline"
            title={t('settings.offlineMode')}
            subtitle="Download maps and routes for offline use"
            onPress={() => {}}
          />
          
          <SettingItem
            icon="cellular-outline"
            title={t('settings.dataUsage')}
            subtitle="Manage data consumption"
            onPress={() => {}}
          />
          
          <SettingItem
            icon="trash-outline"
            title={t('settings.clearCache')}
            subtitle="Free up storage space"
            onPress={() => {
              Alert.alert(
                'Clear Cache',
                'This will remove cached data to free up space',
                [
                  { text: 'Cancel', style: 'cancel' },
                  { text: 'Clear', onPress: () => {} },
                ]
              );
            }}
          />

          {/* Support */}
          <SectionHeader title="Support" />
          
          <SettingItem
            icon="help-circle-outline"
            title={t('settings.support')}
            subtitle="Get help and contact support"
            onPress={() => {}}
          />
          
          <SettingItem
            icon="chatbubble-outline"
            title={t('settings.feedback')}
            subtitle="Send feedback and suggestions"
            onPress={() => {}}
          />
          
          <SettingItem
            icon="star-outline"
            title={t('settings.rateApp')}
            subtitle="Rate Smart Transit Companion"
            onPress={() => {}}
          />
          
          <SettingItem
            icon="share-outline"
            title={t('settings.shareApp')}
            subtitle="Share with friends and family"
            onPress={() => {}}
          />

          {/* Legal */}
          <SectionHeader title="Legal" />
          
          <SettingItem
            icon="document-text-outline"
            title={t('settings.privacy')}
            subtitle="Privacy policy and data usage"
            onPress={() => {}}
          />
          
          <SettingItem
            icon="shield-outline"
            title={t('settings.terms')}
            subtitle="Terms of service"
            onPress={() => {}}
          />

          {/* About */}
          <SectionHeader title={t('profile.about')} />
          
          <SettingItem
            icon="information-circle-outline"
            title="App Version"
            subtitle="1.0.0 (SLAIC 2025)"
            onPress={() => {}}
          />

          {/* Logout */}
          <SettingItem
            icon="log-out-outline"
            title={t('auth.logout')}
            subtitle="Sign out of your account"
            onPress={handleLogout}
            isDestructive
          />

          <View className="pb-8" />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}