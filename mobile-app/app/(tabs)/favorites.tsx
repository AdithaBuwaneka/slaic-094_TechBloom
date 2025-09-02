import { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  TextInput,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';
import { storageService } from '@/services/storage';

export default function FavoritesScreen() {
  const router = useRouter();
  const { t } = useTranslation();
  const { theme } = useApp();
  
  const [favorites, setFavorites] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [editingLabel, setEditingLabel] = useState<string | null>(null);
  const [newLabel, setNewLabel] = useState('');
  
  const isDark = theme === 'dark';

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      const favoritesData = await storageService.getFavorites();
      setFavorites(favoritesData);
    } catch (error) {
      console.error('Failed to load favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadFavorites();
    setRefreshing(false);
  };

  const removeFavorite = (item: any) => {
    Alert.alert(
      'Remove Favorite',
      `Remove "${item.label || `${item.origin} → ${item.destination}`}" from favorites?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: async () => {
            await storageService.removeFromFavorites(item);
            setFavorites(prev => prev.filter(fav => 
              !(fav.origin === item.origin && fav.destination === item.destination)
            ));
          },
        },
      ]
    );
  };

  const startJourney = (item: any) => {
    router.push({
      pathname: '/journey',
      params: {
        origin: item.origin,
        destination: item.destination,
        transportMode: item.transport_mode || 'any',
      },
    });
  };

  const saveLabel = async (item: any) => {
    try {
      // Update the label in storage
      const updatedFavorites = favorites.map(fav => 
        (fav.origin === item.origin && fav.destination === item.destination)
          ? { ...fav, label: newLabel.trim() }
          : fav
      );
      
      // Save updated favorites
      await Promise.all(updatedFavorites.map(fav => storageService.addToFavorites(fav)));
      
      setFavorites(updatedFavorites);
      setEditingLabel(null);
      setNewLabel('');
    } catch {
      Alert.alert(t('common.error'), 'Failed to update label');
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const FavoriteItem = ({ item, index }: { item: any, index: number }) => {
    const itemKey = `${item.origin}-${item.destination}`;
    const isEditing = editingLabel === itemKey;

    return (
      <View className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-4 mb-3 border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <View className="flex-row items-start justify-between mb-3">
          <View className="flex-1">
            {/* Label */}
            {isEditing ? (
              <View className="mb-2">
                <TextInput
                  value={newLabel}
                  onChangeText={setNewLabel}
                  placeholder="Add a label (e.g., Home, Work)"
                  placeholderTextColor={isDark ? '#6b7280' : '#9ca3af'}
                  className={`${isDark ? 'bg-gray-700 text-white' : 'bg-gray-100 text-gray-900'} rounded-lg px-3 py-2 text-sm`}
                  autoFocus
                />
                <View className="flex-row space-x-2 mt-2">
                  <TouchableOpacity
                    onPress={() => saveLabel(item)}
                    className="bg-blue-600 px-3 py-1 rounded-full"
                  >
                    <Text className="text-white text-xs font-medium">Save</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    onPress={() => {
                      setEditingLabel(null);
                      setNewLabel('');
                    }}
                    className={`${isDark ? 'bg-gray-700' : 'bg-gray-200'} px-3 py-1 rounded-full`}
                  >
                    <Text className={`text-xs font-medium ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                      Cancel
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>
            ) : (
              item.label && (
                <View className="flex-row items-center mb-2">
                  <View className="bg-green-100 px-2 py-1 rounded-full mr-2">
                    <Text className="text-green-800 text-xs font-medium">{item.label}</Text>
                  </View>
                  <TouchableOpacity
                    onPress={() => {
                      setEditingLabel(itemKey);
                      setNewLabel(item.label || '');
                    }}
                  >
                    <Ionicons name="pencil" size={14} color="#6b7280" />
                  </TouchableOpacity>
                </View>
              )
            )}

            {/* Route */}
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
                  <Ionicons name="arrow-down" size={12} color="#6b7280" />
                </View>
                <Text className={`font-semibold text-sm ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  {item.destination}
                </Text>
              </View>
            </View>

            <Text className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              Added on {formatDate(item.favorited_at)}
            </Text>
          </View>
          
          <TouchableOpacity
            onPress={() => removeFavorite(item)}
            className={`w-8 h-8 rounded-full items-center justify-center ${isDark ? 'bg-gray-700' : 'bg-gray-100'}`}
          >
            <Ionicons name="trash-outline" size={16} color="#ef4444" />
          </TouchableOpacity>
        </View>

        {/* Action Buttons */}
        <View className="flex-row space-x-3">
          <TouchableOpacity
            onPress={() => startJourney(item)}
            className="bg-blue-600 rounded-xl py-2 px-4 flex-1"
          >
            <Text className="text-white font-semibold text-center text-sm">
              Start Journey
            </Text>
          </TouchableOpacity>
          
          {!item.label && !isEditing && (
            <TouchableOpacity
              onPress={() => {
                setEditingLabel(itemKey);
                setNewLabel('');
              }}
              className={`${isDark ? 'bg-gray-700' : 'bg-gray-200'} rounded-xl py-2 px-4`}
            >
              <Text className={`font-medium text-center text-sm ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                {t('favorites.addLabel')}
              </Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

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
      <View className="px-6 py-4">
        <Text className={`text-2xl font-bold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
          {t('favorites.favoriteJourneys')}
        </Text>
        <Text className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
          {favorites.length} saved routes
        </Text>
      </View>

      {favorites.length === 0 ? (
        /* Empty State */
        <View className="flex-1 justify-center items-center px-6">
          <View className={`w-24 h-24 rounded-full items-center justify-center mb-6 ${isDark ? 'bg-gray-800' : 'bg-gray-100'}`}>
            <Ionicons name="heart-outline" size={48} color="#6b7280" />
          </View>
          <Text className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            {t('favorites.noFavorites')}
          </Text>
          <Text className={`text-center mb-8 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Save your frequently used routes for quick access
          </Text>
          <TouchableOpacity
            onPress={() => router.push('/journey')}
            className="bg-blue-600 rounded-xl py-3 px-6"
          >
            <Text className="text-white font-semibold">
              Plan a Journey
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        /* Favorites List */
        <ScrollView
          className="flex-1 px-6"
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          {/* Quick Access Cards */}
          <View className="mb-6">
            <Text className={`text-lg font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Quick Access
            </Text>
            <View className="flex-row space-x-3">
              <TouchableOpacity className={`${isDark ? 'bg-green-900/20' : 'bg-green-50'} rounded-2xl p-4 flex-1 items-center`}>
                <Ionicons name="home" size={24} color="#059669" />
                <Text className={`font-medium mt-2 ${isDark ? 'text-green-200' : 'text-green-800'}`}>
                  {t('favorites.home')}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity className={`${isDark ? 'bg-blue-900/20' : 'bg-blue-50'} rounded-2xl p-4 flex-1 items-center`}>
                <Ionicons name="briefcase" size={24} color="#2563eb" />
                <Text className={`font-medium mt-2 ${isDark ? 'text-blue-200' : 'text-blue-800'}`}>
                  {t('favorites.work')}
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* All Favorites */}
          <Text className={`text-lg font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            All Favorites
          </Text>
          {favorites.map((item, index) => (
            <FavoriteItem key={`${item.origin}-${item.destination}-${index}`} item={item} index={index} />
          ))}
          <View className="pb-6" />
        </ScrollView>
      )}
    </SafeAreaView>
  );
}