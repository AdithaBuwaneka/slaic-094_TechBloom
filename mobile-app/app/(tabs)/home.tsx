import { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { navigateToMap } from '@/utils/navigation';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';

export default function HomeScreen() {
  const router = useRouter();
  const { user, currentLocation, theme } = useApp();
  
  const [refreshing, setRefreshing] = useState(false);
  const [weather] = useState({ temp: 28, condition: 'Sunny' });
  const [disruptions] = useState([
    { id: 1, route: 'Colombo - Kandy', severity: 'medium', message: 'Light traffic on A1 highway' },
    { id: 2, route: 'Galle Road', severity: 'high', message: 'Road construction near Bambalapitiya' }
  ]);

  const isDark = theme === 'dark';

  const onRefresh = async () => {
    setRefreshing(true);
    // Simulate API call
    setTimeout(() => setRefreshing(false), 2000);
  };

  const QuickAction = ({ icon, title, subtitle, onPress, color = '#2563eb' }: any) => (
    <TouchableOpacity 
      onPress={() => {
        console.log(`🎯 QuickAction pressed: ${title}`);
        if (onPress) {
          onPress();
        } else {
          console.warn('⚠️ No onPress handler provided');
        }
      }}
      className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-4 shadow-sm border ${isDark ? 'border-gray-700' : 'border-gray-100'}`}
    >
      <View className={`w-12 h-12 rounded-full items-center justify-center mb-3`} style={{ backgroundColor: `${color}20` }}>
        <Ionicons name={icon} size={24} color={color} />
      </View>
      <Text className={`font-semibold text-base mb-1 ${isDark ? 'text-white' : 'text-gray-900'}`}>
        {title}
      </Text>
      <Text className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
        {subtitle}
      </Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView className={`flex-1 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <ScrollView
        className="flex-1"
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View className="px-6 pt-4 pb-6">
          <View className="flex-row items-center justify-between mb-6">
            <View>
              <Text className={`text-lg ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                {new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 17 ? 'Good afternoon' : 'Good evening'}
              </Text>
              <Text className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {user?.full_name?.split(' ')[0] || 'Traveler'}
              </Text>
            </View>
            <View className="flex-row items-center space-x-3">
              <TouchableOpacity className={`w-10 h-10 rounded-full items-center justify-center ${isDark ? 'bg-gray-800' : 'bg-white'}`}>
                <Ionicons name="notifications-outline" size={20} color={isDark ? '#9ca3af' : '#6b7280'} />
              </TouchableOpacity>
              <TouchableOpacity className={`w-10 h-10 rounded-full items-center justify-center ${isDark ? 'bg-gray-800' : 'bg-white'}`}>
                <Text className="text-lg">🌍</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Location & Weather Card */}
          <View className={`${isDark ? 'bg-blue-900' : 'bg-blue-50'} rounded-2xl p-4 mb-6`}>
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <View className="flex-row items-center mb-2">
                  <Ionicons name="location" size={16} color="#2563eb" />
                  <Text className={`text-sm font-medium ml-1 ${isDark ? 'text-blue-100' : 'text-blue-800'}`}>
                    {currentLocation?.address || 'Getting location...'}
                  </Text>
                </View>
                <Text className={`text-xs ${isDark ? 'text-blue-200' : 'text-blue-600'}`}>
                  {weather.temp}°C • {weather.condition}
                </Text>
              </View>
              <TouchableOpacity
                onPress={() => router.push('/journey')}
                className="bg-blue-600 px-4 py-2 rounded-full"
              >
                <Text className="text-white font-medium text-sm">Plan Journey</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Quick Actions Grid */}
        <View className="px-6 mb-6">
          <Text className={`text-lg font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Quick Actions
          </Text>
          <View className="flex-row flex-wrap justify-between">
            <View className="w-[48%] mb-4">
              <QuickAction
                icon="navigate"
                title="Plan Journey"
                subtitle="AI-powered routes"
                color="#2563eb"
                onPress={() => router.push('/journey')}
              />
            </View>
            <View className="w-[48%] mb-4">
              <QuickAction
                icon="time"
                title="Recent Trips"
                subtitle="View history"
                color="#059669"
                onPress={() => router.push('/history')}
              />
            </View>
            <View className="w-[48%] mb-4">
              <QuickAction
                icon="heart"
                title="Favorites"
                subtitle="Saved routes"
                color="#dc2626"
                onPress={() => router.push('/favorites')}
              />
            </View>
            <View className="w-[48%] mb-4">
              <QuickAction
                icon="map"
                title="Live Map"
                subtitle="Real-time transit"
                color="#7c3aed"
                onPress={async () => {
                  console.log('🗺️ Live Map button pressed - Starting navigation');
                  
                  const success = await navigateToMap();
                  if (!success) {
                    Alert.alert(
                      'Navigation', 
                      'Please use the Map tab at the bottom to access the live map.',
                      [{ text: 'OK' }]
                    );
                  }
                }}
              />
            </View>
          </View>
        </View>

        {/* Travel Disruptions */}
        {disruptions.length > 0 && (
          <View className="px-6 mb-6">
            <View className="flex-row items-center justify-between mb-4">
              <Text className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Travel Alerts
              </Text>
              <TouchableOpacity>
                <Text className="text-blue-600 font-medium">View All</Text>
              </TouchableOpacity>
            </View>
            {disruptions.map((item) => (
              <View 
                key={item.id}
                className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-xl p-4 mb-3 border-l-4 ${
                  item.severity === 'high' ? 'border-red-500' : 'border-yellow-500'
                }`}
              >
                <View className="flex-row items-start justify-between">
                  <View className="flex-1">
                    <Text className={`font-semibold text-sm mb-1 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                      {item.route}
                    </Text>
                    <Text className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                      {item.message}
                    </Text>
                  </View>
                  <View className={`px-2 py-1 rounded-full ${
                    item.severity === 'high' ? 'bg-red-100' : 'bg-yellow-100'
                  }`}>
                    <Text className={`text-xs font-medium ${
                      item.severity === 'high' ? 'text-red-800' : 'text-yellow-800'
                    }`}>
                      {item.severity === 'high' ? 'High' : 'Medium'}
                    </Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Recent Activity */}
        <View className="px-6 mb-8">
          <Text className={`text-lg font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Recent Activity
          </Text>
          <View className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-4`}>
            <Text className={`text-center ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              Start planning your first journey to see activity here
            </Text>
            <TouchableOpacity 
              onPress={() => router.push('/(tabs)/journey')}
              className="bg-blue-600 rounded-xl py-3 mt-4"
            >
              <Text className="text-white font-semibold text-center">
                Plan Your First Journey
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}