import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';
import { apiService } from '@/services/api';
import { storageService } from '@/services/storage';
import type { JourneyRequest, AIJourneyResponse } from '@/types';

export default function JourneyScreen() {
  const { t } = useTranslation();
  const { user, currentLocation, theme } = useApp();
  
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [isPlanning, setIsPlanning] = useState(false);
  const [journeyResult, setJourneyResult] = useState<AIJourneyResponse | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [selectedTransport, setSelectedTransport] = useState('any');
  
  const isDark = theme === 'dark';

  const transportModes = [
    { id: 'any', name: t('journey.transportModes.any'), icon: 'apps' },
    { id: 'bus', name: t('journey.transportModes.bus'), icon: 'bus' },
    { id: 'train', name: t('journey.transportModes.train'), icon: 'train' },
    { id: 'tuk', name: t('journey.transportModes.tuk'), icon: 'car' },
    { id: 'walk', name: t('journey.transportModes.walk'), icon: 'walk' },
  ];

  const useCurrentLocation = () => {
    if (currentLocation?.address) {
      setOrigin(currentLocation.address);
    } else {
      Alert.alert(t('common.error'), t('location.locationError'));
    }
  };

  const swapLocations = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  const planJourney = async () => {
    if (!origin.trim() || !destination.trim()) {
      Alert.alert(t('common.error'), 'Please enter both origin and destination');
      return;
    }

    setIsPlanning(true);
    setShowResults(false);

    try {
      // Create natural language query for AI agent
      const transportMode = selectedTransport === 'any' ? '' : ` using ${selectedTransport}`;
      const query = `I want to travel from ${origin.trim()} to ${destination.trim()}${transportMode}`;
      
      const request: JourneyRequest = {
        query,
        language_preference: user?.preferred_language || 'en',
        accessibility_needs: user?.accessibility_needs,
        budget_preference: undefined,
        passenger_type: 'adult',
      };

      const result = await apiService.planJourney(request);
      setJourneyResult(result);
      setShowResults(true);

      // Save to history
      await storageService.addToHistory({
        origin: origin.trim(),
        destination: destination.trim(),
        transport_mode: selectedTransport,
        result,
      });

    } catch (error: any) {
      Alert.alert(t('common.error'), error.message || 'Failed to plan journey');
    } finally {
      setIsPlanning(false);
    }
  };

  const addToFavorites = async () => {
    if (!origin.trim() || !destination.trim()) return;

    try {
      await storageService.addToFavorites({
        origin: origin.trim(),
        destination: destination.trim(),
        transport_mode: selectedTransport,
      });
      Alert.alert(t('common.success'), t('journey.addedToFavorites'));
    } catch {
      Alert.alert(t('common.error'), 'Failed to add to favorites');
    }
  };

  const RouteCard = ({ route, index }: { route: any, index: number }) => (
    <View className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-4 mb-4 border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
      <View className="flex-row items-center justify-between mb-3">
        <View className="flex-row items-center">
          <View className="bg-blue-600 w-6 h-6 rounded-full items-center justify-center mr-2">
            <Text className="text-white text-xs font-bold">{index + 1}</Text>
          </View>
          <Text className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
            {route.summary}
          </Text>
        </View>
        <TouchableOpacity onPress={addToFavorites}>
          <Ionicons name="heart-outline" size={20} color="#6b7280" />
        </TouchableOpacity>
      </View>

      <View className="flex-row items-center space-x-4 mb-3">
        <View className="flex-row items-center">
          <Ionicons name="time" size={16} color="#6b7280" />
          <Text className={`text-sm ml-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            {route.total_duration}
          </Text>
        </View>
        <View className="flex-row items-center">
          <Ionicons name="location" size={16} color="#6b7280" />
          <Text className={`text-sm ml-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            {route.total_distance}
          </Text>
        </View>
        {route.total_cost && (
          <View className="flex-row items-center">
            <Ionicons name="card" size={16} color="#6b7280" />
            <Text className={`text-sm ml-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              LKR {route.total_cost}
            </Text>
          </View>
        )}
      </View>

      {/* Route Steps */}
      {route.legs && route.legs.length > 0 && (
        <View className="mb-3">
          <Text className={`text-xs font-medium mb-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            JOURNEY STEPS
          </Text>
          {route.legs.map((leg: any, legIndex: number) => (
            <View key={legIndex} className="flex-row items-center mb-1">
              <Ionicons 
                name={leg.travel_mode === 'WALKING' ? 'walk' : leg.travel_mode === 'TRANSIT' ? 'train' : 'bus'} 
                size={12} 
                color="#6b7280" 
              />
              <Text className={`text-xs ml-2 flex-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                {leg.summary} ({leg.duration})
              </Text>
            </View>
          ))}
        </View>
      )}

      <View className="flex-row space-x-2">
        <TouchableOpacity 
          className="flex-1 bg-blue-600 rounded-xl py-3"
          onPress={() => {
            // Navigate to map view with this route
            router.push({
              pathname: '/(tabs)/map',
              params: { 
                routeData: JSON.stringify(route),
                origin: JSON.stringify({ address: origin }),
                destination: JSON.stringify({ address: destination })
              }
            });
          }}
        >
          <View className="flex-row items-center justify-center">
            <Ionicons name="map" size={16} color="white" />
            <Text className="text-white font-semibold text-center ml-2">
              View on Map
            </Text>
          </View>
        </TouchableOpacity>
        
        <TouchableOpacity 
          className="bg-green-600 rounded-xl py-3 px-4"
          onPress={() => {
            // Start navigation or select route
            Alert.alert('Route Selected', `Starting navigation for ${route.summary}`);
          }}
        >
          <Ionicons name="navigate" size={16} color="white" />
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <SafeAreaView className={`flex-1 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View className="px-6 py-4">
          <Text className={`text-2xl font-bold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            {t('journey.planJourney')}
          </Text>
          <Text className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            AI-powered journey planning for Sri Lanka
          </Text>
        </View>

        {/* Journey Form */}
        <View className="px-6 space-y-4">
          {/* Origin Input */}
          <View>
            <Text className={`text-sm font-medium mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              {t('journey.from')}
            </Text>
            <View className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-xl px-4 py-3 border flex-row items-center`}>
              <Ionicons name="radio-button-on" size={20} color="#2563eb" />
              <TextInput
                value={origin}
                onChangeText={setOrigin}
                placeholder={t('journey.fromPlaceholder')}
                placeholderTextColor={isDark ? '#6b7280' : '#9ca3af'}
                className={`flex-1 ml-3 text-base ${isDark ? 'text-white' : 'text-gray-900'}`}
              />
              <TouchableOpacity onPress={useCurrentLocation}>
                <Ionicons name="locate" size={20} color="#6b7280" />
              </TouchableOpacity>
            </View>
          </View>

          {/* Swap Button */}
          <View className="items-center">
            <TouchableOpacity 
              onPress={swapLocations}
              className={`w-10 h-10 rounded-full items-center justify-center ${isDark ? 'bg-gray-800' : 'bg-white'} border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}
            >
              <Ionicons name="swap-vertical" size={20} color="#6b7280" />
            </TouchableOpacity>
          </View>

          {/* Destination Input */}
          <View>
            <Text className={`text-sm font-medium mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              {t('journey.to')}
            </Text>
            <View className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} rounded-xl px-4 py-3 border flex-row items-center`}>
              <Ionicons name="location" size={20} color="#dc2626" />
              <TextInput
                value={destination}
                onChangeText={setDestination}
                placeholder={t('journey.toPlaceholder')}
                placeholderTextColor={isDark ? '#6b7280' : '#9ca3af'}
                className={`flex-1 ml-3 text-base ${isDark ? 'text-white' : 'text-gray-900'}`}
              />
            </View>
          </View>

          {/* Transport Mode Selection */}
          <View>
            <Text className={`text-sm font-medium mb-3 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              {t('journey.transportMode')}
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} className="space-x-3">
              {transportModes.map((mode) => (
                <TouchableOpacity
                  key={mode.id}
                  onPress={() => setSelectedTransport(mode.id)}
                  className={`px-4 py-3 rounded-xl border mr-3 ${
                    selectedTransport === mode.id
                      ? 'bg-blue-600 border-blue-600'
                      : `${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`
                  }`}
                >
                  <View className="items-center">
                    <Ionicons 
                      name={mode.icon as any} 
                      size={20} 
                      color={selectedTransport === mode.id ? '#ffffff' : '#6b7280'} 
                    />
                    <Text className={`text-xs mt-1 ${
                      selectedTransport === mode.id 
                        ? 'text-white' 
                        : `${isDark ? 'text-gray-400' : 'text-gray-600'}`
                    }`}>
                      {mode.name}
                    </Text>
                  </View>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>

          {/* Find Routes Button */}
          <TouchableOpacity
            onPress={planJourney}
            disabled={isPlanning}
            className={`bg-blue-600 rounded-xl py-4 mt-6 ${isPlanning ? 'opacity-70' : ''}`}
          >
            <View className="flex-row items-center justify-center">
              {isPlanning && (
                <ActivityIndicator size="small" color="#ffffff" className="mr-2" />
              )}
              <Text className="text-white font-semibold text-lg">
                {isPlanning ? t('ai.analyzing') : t('journey.findRoutes')}
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Results */}
        {showResults && journeyResult && (
          <View className="px-6 mt-8">
            <Text className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              {t('journey.routeOptions')}
            </Text>

            {/* AI Insights */}
            {journeyResult.disruption_analysis && (
              <View className={`${isDark ? 'bg-yellow-900/20' : 'bg-yellow-50'} rounded-2xl p-4 mb-4 border-l-4 border-yellow-500`}>
                <View className="flex-row items-start">
                  <Ionicons name="warning" size={20} color="#f59e0b" />
                  <View className="ml-3 flex-1">
                    <Text className={`font-semibold mb-1 ${isDark ? 'text-yellow-200' : 'text-yellow-800'}`}>
                      {t('ai.disruptions')}
                    </Text>
                    <Text className={`text-sm ${isDark ? 'text-yellow-300' : 'text-yellow-700'}`}>
                      {journeyResult.disruption_analysis.user_message}
                    </Text>
                  </View>
                </View>
              </View>
            )}

            {/* Disruption Analysis */}
            {journeyResult.disruption_analysis && (
              <View className={`${isDark ? 'bg-red-900/20' : 'bg-red-50'} rounded-2xl p-4 mb-4`}>
                <View className="flex-row items-start">
                  <Ionicons name="warning" size={20} color="#dc2626" />
                  <View className="ml-3 flex-1">
                    <Text className={`font-semibold mb-1 ${isDark ? 'text-red-200' : 'text-red-800'}`}>
                      Traffic & Disruptions
                    </Text>
                    <Text className={`text-sm mb-2 ${isDark ? 'text-red-300' : 'text-red-700'}`}>
                      {journeyResult.disruption_analysis.user_message}
                    </Text>
                    {journeyResult.disruption_analysis.severity_level === 'high' && (
                      <View className={`${isDark ? 'bg-red-800' : 'bg-red-100'} rounded-lg p-2 mt-2`}>
                        <Text className={`text-xs font-medium ${isDark ? 'text-red-200' : 'text-red-800'}`}>
                          High Impact Warning
                        </Text>
                      </View>
                    )}
                  </View>
                </View>
              </View>
            )}

            {/* Route Options */}
            {journeyResult.direct_route_options?.map((route, index) => (
              <RouteCard key={index} route={route} index={index} />
            ))}

            {/* AI Recommendations */}
            {journeyResult.personalized_recommendations && (
              <View className={`${isDark ? 'bg-blue-900/20' : 'bg-blue-50'} rounded-2xl p-4 mb-4`}>
                <View className="flex-row items-start">
                  <Ionicons name="sparkles" size={20} color="#2563eb" />
                  <View className="ml-3 flex-1">
                    <Text className={`font-semibold mb-1 ${isDark ? 'text-blue-200' : 'text-blue-800'}`}>
                      {t('ai.personalizedTips')}
                    </Text>
                    <Text className={`text-sm ${isDark ? 'text-blue-300' : 'text-blue-700'}`}>
                      {journeyResult.personalized_recommendations.personalization_reason}
                    </Text>
                  </View>
                </View>
              </View>
            )}

            {/* Local Insights */}
            {journeyResult.local_insights?.local_tips && journeyResult.local_insights.local_tips.length > 0 && (
              <View className={`${isDark ? 'bg-green-900/20' : 'bg-green-50'} rounded-2xl p-4 mb-4`}>
                <View className="flex-row items-start">
                  <Ionicons name="bulb" size={20} color="#059669" />
                  <View className="ml-3 flex-1">
                    <Text className={`font-semibold mb-2 ${isDark ? 'text-green-200' : 'text-green-800'}`}>
                      Local Travel Tips
                    </Text>
                    {journeyResult.local_insights.local_tips.slice(0, 3).map((tip: string, tipIndex: number) => (
                      <View key={tipIndex} className="flex-row mb-1">
                        <Text className={`text-xs mr-2 ${isDark ? 'text-green-400' : 'text-green-600'}`}>•</Text>
                        <Text className={`text-xs flex-1 ${isDark ? 'text-green-300' : 'text-green-700'}`}>
                          {tip.replace(/"/g, '')}
                        </Text>
                      </View>
                    ))}
                  </View>
                </View>
              </View>
            )}
          </View>
        )}

        {/* Empty state when no results */}
        {showResults && (!journeyResult?.direct_route_options || journeyResult.direct_route_options.length === 0) && (
          <View className="px-6 mt-8">
            <View className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-2xl p-8 items-center`}>
              <Ionicons name="sad" size={48} color="#6b7280" />
              <Text className={`text-lg font-semibold mt-4 mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t('journey.noRoutesFound')}
              </Text>
              <Text className={`text-center ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                Try adjusting your search or check the locations
              </Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}