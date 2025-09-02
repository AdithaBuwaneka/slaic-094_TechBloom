import { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';
import { storageService } from '@/services/storage';

export default function HistoryScreen() {
  const router = useRouter();
  const { t } = useTranslation();
  const { theme } = useApp();
  
  const [history, setHistory] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const isDark = theme === 'dark';

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const historyData = await storageService.getHistory();
      setHistory(historyData);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadHistory();
    setRefreshing(false);
  };

  const clearHistory = () => {
    Alert.alert(
      'Clear History',
      'Are you sure you want to clear all journey history?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            await storageService.clearHistory();
            setHistory([]);
          },
        },
      ]
    );
  };

  const repeatJourney = (item: any) => {
    // Navigate to journey screen with pre-filled data
    router.push({
      pathname: '/journey',
      params: {
        origin: item.origin,
        destination: item.destination,
        transportMode: item.transport_mode,
      },
    });
  };

  const addToFavorites = async (item: any) => {
    try {
      await storageService.addToFavorites(item);
      Alert.alert(t('common.success'), t('journey.addedToFavorites'));
    } catch {
      Alert.alert(t('common.error'), 'Failed to add to favorites');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return t('history.today');
    } else if (diffDays === 1) {
      return t('history.yesterday');
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getTransportIcon = (mode: string) => {
    switch (mode) {
      case 'bus': return 'bus';
      case 'train': return 'train';
      case 'tuk': return 'car';
      case 'walk': return 'walk';
      default: return 'navigate';
    }
  };

  const HistoryItem = ({ item, index }: { item: any, index: number }) => (
    <View className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-4 mb-3 border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
      <View className="flex-row items-start justify-between mb-3">
        <View className="flex-1">
          <View className="flex-row items-center mb-2">
            <View className={`w-8 h-8 rounded-full items-center justify-center mr-3 ${isDark ? 'bg-blue-900' : 'bg-blue-100'}`}>
              <Ionicons 
                name={getTransportIcon(item.transport_mode) as any} 
                size={16} 
                color="#2563eb" 
              />
            </View>
            <View className="flex-1">
              <Text className={`font-semibold text-sm ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {item.origin}
              </Text>
              <View className="flex-row items-center my-1">
                <View className="w-1 h-1 bg-gray-400 rounded-full mr-1" />
                <View className="w-1 h-1 bg-gray-400 rounded-full mr-1" />
                <View className="w-1 h-1 bg-gray-400 rounded-full" />
              </View>
              <Text className={`font-semibold text-sm ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {item.destination}
              </Text>
            </View>
          </View>
          <Text className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            {formatDate(item.timestamp)}
          </Text>
        </View>
        
        <View className="flex-row space-x-2">
          <TouchableOpacity
            onPress={() => addToFavorites(item)}
            className={`w-8 h-8 rounded-full items-center justify-center ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}
          >
            <Ionicons name="heart-outline" size={16} color="#6b7280" />
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => repeatJourney(item)}
            className="bg-blue-600 px-3 py-1 rounded-full"
          >
            <Text className="text-white text-xs font-medium">
              {t('history.repeatJourney')}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Journey Details */}
      {item.result?.route_options?.[0] && (
        <View className={`${isDark ? 'bg-gray-700' : 'bg-gray-50'} rounded-xl p-3 mt-2`}>
          <View className="flex-row items-center space-x-4">
            <View className="flex-row items-center">
              <Ionicons name="time" size={14} color="#6b7280" />
              <Text className={`text-xs ml-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                {item.result.route_options[0].total_duration}
              </Text>
            </View>
            <View className="flex-row items-center">
              <Ionicons name="location" size={14} color="#6b7280" />
              <Text className={`text-xs ml-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                {item.result.route_options[0].total_distance}
              </Text>
            </View>
            {item.result.fare_optimization?.total_cost && (
              <View className="flex-row items-center">
                <Ionicons name="card" size={14} color="#6b7280" />
                <Text className={`text-xs ml-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  LKR {item.result.fare_optimization.total_cost}
                </Text>
              </View>
            )}
          </View>
        </View>
      )}
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView className={`flex-1 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <View className="flex-1 justify-center items-center">
          <Text className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            {t('common.loading')}
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className={`flex-1 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <View className="flex-row items-center justify-between px-6 py-4">
        <View>
          <Text className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
            {t('history.journeyHistory')}
          </Text>
          <Text className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            {history.length} journeys
          </Text>
        </View>
        {history.length > 0 && (
          <TouchableOpacity
            onPress={clearHistory}
            className={`px-4 py-2 rounded-xl ${isDark ? 'bg-red-900/20' : 'bg-red-50'}`}
          >
            <Text className="text-red-600 font-medium text-sm">
              {t('history.clearHistory')}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      {history.length === 0 ? (
        /* Empty State */
        <View className="flex-1 justify-center items-center px-6">
          <View className={`w-24 h-24 rounded-full items-center justify-center mb-6 ${isDark ? 'bg-gray-800' : 'bg-gray-100'}`}>
            <Ionicons name="time-outline" size={48} color="#6b7280" />
          </View>
          <Text className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            {t('history.noHistory')}
          </Text>
          <Text className={`text-center mb-8 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Your journey history will appear here once you start planning trips
          </Text>
          <TouchableOpacity
            onPress={() => router.push('/journey')}
            className="bg-blue-600 rounded-xl py-3 px-6"
          >
            <Text className="text-white font-semibold">
              Plan Your First Journey
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        /* History List */
        <ScrollView
          className="flex-1 px-6"
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          {history.map((item, index) => (
            <HistoryItem key={index} item={item} index={index} />
          ))}
          <View className="pb-6" />
        </ScrollView>
      )}
    </SafeAreaView>
  );
}