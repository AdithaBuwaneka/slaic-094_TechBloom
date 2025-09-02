import { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  TextInput,
  Alert,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';
import { locationService } from '@/services/location';
import { apiService } from '@/services/api';
import RouteMap from '@/components/MapView';
import type { Location, AIJourneyResponse } from '@/types';

export default function MapScreen() {
  const { currentLocation, theme } = useApp();
  
  console.log('🗺️ MapScreen rendered');
  console.log('🗺️ Current location:', currentLocation);
  
  const [origin, setOrigin] = useState<Location | undefined>();
  const [destination, setDestination] = useState<Location | undefined>();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Location[]>([]);
  const [journeyResult, setJourneyResult] = useState<AIJourneyResponse | null>(null);
  const [selectedRoute, setSelectedRoute] = useState(0);
  const [isPlanning, setIsPlanning] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  
  const isDark = theme === 'dark';

  useEffect(() => {
    if (currentLocation) {
      setOrigin(currentLocation);
    }
  }, [currentLocation]);

  const searchLocation = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const results = await locationService.searchLocation(query);
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
      Alert.alert('Search Error', 'Failed to search location');
    } finally {
      setIsSearching(false);
    }
  };

  const handleLocationSelect = (coordinate: { latitude: number; longitude: number }) => {
    console.log('📍 Location selected:', coordinate);
    
    const newLocation: Location = {
      latitude: coordinate.latitude,
      longitude: coordinate.longitude,
      address: `${coordinate.latitude.toFixed(4)}, ${coordinate.longitude.toFixed(4)}`,
    };

    if (!origin) {
      setOrigin(newLocation);
    } else if (!destination) {
      setDestination(newLocation);
    } else {
      // Reset and set as new origin
      setOrigin(newLocation);
      setDestination(undefined);
    }
  };

  const handlePlanJourney = async () => {
    if (!origin || !destination) {
      Alert.alert('Missing Information', 'Please select both origin and destination');
      return;
    }

    setIsPlanning(true);
    try {
      console.log('🛣️ Planning journey from', origin.address, 'to', destination.address);
      
      const result = await apiService.planJourney({
        origin: origin.address,
        destination: destination.address,
        mode: 'transit',
      });

      console.log('✅ Journey planned:', result);
      console.log('✅ Route options:', result.route_options);
      console.log('✅ First route polyline:', result.route_options?.[0]?.polyline);
      setJourneyResult(result);
    } catch (error) {
      console.error('Journey planning error:', error);
      Alert.alert('Planning Error', 'Failed to plan journey');
    } finally {
      setIsPlanning(false);
    }
  };

  const swapLocations = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  const clearRoute = () => {
    setOrigin(undefined);
    setDestination(undefined);
    setJourneyResult(null);
    setSearchQuery('');
    setSearchResults([]);
  };

  return (
    <SafeAreaView className={`flex-1 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
      
      {/* Header with controls - Fixed at top */}
      <View className="p-4 space-y-3">
        
        {/* Title and Quick Actions */}
        <View className="flex-row items-center justify-between">
          <Text className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
            🗺️ Live Map
          </Text>
          <View className="flex-row space-x-2">
            <TouchableOpacity
              onPress={() => {
                console.log('🧪 Test Route button clicked');
                // Clear any existing routes first
                clearRoute();
                
                // Set Colombo as origin
                setTimeout(() => {
                  console.log('🧪 Setting Colombo as origin');
                  handleLocationSelect({ latitude: 6.9271, longitude: 79.8612 });
                }, 100);
                
                // Set Kandy as destination after a delay
                setTimeout(() => {
                  console.log('🧪 Setting Kandy as destination');
                  handleLocationSelect({ latitude: 7.2906, longitude: 80.6337 });
                }, 1000);
              }}
              className={`px-3 py-1 ${isDark ? 'bg-orange-600' : 'bg-orange-500'} rounded-full`}
            >
              <Text className="text-white text-xs font-bold">Test Route</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={async () => {
                console.log('🧭 Manual location request');
                await getCurrentLocation();
              }}
              className={`px-3 py-1 ${isDark ? 'bg-blue-600' : 'bg-blue-500'} rounded-full`}
            >
              <Text className="text-white text-xs font-bold">📍 Location</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={clearRoute}
              className={`px-3 py-1 ${isDark ? 'bg-gray-600' : 'bg-gray-400'} rounded-full`}
            >
              <Text className="text-white text-xs font-bold">Clear</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Location Selection Card */}
        <View className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-xl p-4 shadow-sm border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          
          {/* Origin */}
          <View className="flex-row items-center space-x-3">
            <View className="w-6 h-6 rounded-full bg-green-500 items-center justify-center">
              <Ionicons name="radio-button-on" size={14} color="white" />
            </View>
            <Text className={`flex-1 text-sm ${isDark ? 'text-white' : 'text-gray-900'}`} numberOfLines={1}>
              {origin?.address || 'Tap map to set origin'}
            </Text>
            <TouchableOpacity 
              onPress={async () => {
                if (currentLocation) {
                  setOrigin(currentLocation);
                } else {
                  // Request location if not available
                  await getCurrentLocation();
                }
              }}
            >
              <Ionicons name="locate" size={18} color="#6b7280" />
            </TouchableOpacity>
          </View>
          
          {/* Swap button */}
          {origin && destination && (
            <TouchableOpacity onPress={swapLocations} className="items-center py-2">
              <Ionicons name="swap-vertical" size={16} color="#6b7280" />
            </TouchableOpacity>
          )}
          
          {/* Destination */}
          <View className="flex-row items-center space-x-3 mt-2">
            <View className="w-6 h-6 rounded-full bg-red-500 items-center justify-center">
              <Ionicons name="location" size={14} color="white" />
            </View>
            <Text className={`flex-1 text-sm ${isDark ? 'text-white' : 'text-gray-900'}`} numberOfLines={1}>
              {destination?.address || 'Tap map to set destination'}
            </Text>
          </View>
        </View>

        {/* Search and Plan Row */}
        <View className="flex-row space-x-2">
          <View className="flex-1">
            <TextInput
              placeholder="Search locations..."
              value={searchQuery}
              onChangeText={setSearchQuery}
              className={`${isDark ? 'bg-gray-700 text-white' : 'bg-white text-gray-900'} rounded-xl px-4 py-2 text-sm border ${isDark ? 'border-gray-600' : 'border-gray-200'}`}
              placeholderTextColor={isDark ? '#9ca3af' : '#6b7280'}
              onSubmitEditing={() => searchLocation(searchQuery)}
            />
          </View>
          
          <TouchableOpacity
            className={`px-4 py-2 ${isDark ? 'bg-blue-600' : 'bg-blue-500'} rounded-xl`}
            onPress={() => searchLocation(searchQuery)}
            disabled={isSearching}
          >
            <Text className="text-white text-sm font-semibold">
              {isSearching ? '...' : 'Search'}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            className={`px-4 py-2 ${origin && destination ? (isDark ? 'bg-green-600' : 'bg-green-500') : (isDark ? 'bg-gray-600' : 'bg-gray-400')} rounded-xl`}
            onPress={handlePlanJourney}
            disabled={isPlanning || !origin || !destination}
          >
            <Text className="text-white text-sm font-semibold">
              {isPlanning ? '...' : 'Plan'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <View className={`${isDark ? 'bg-gray-800' : 'bg-white'} rounded-xl border ${isDark ? 'border-gray-700' : 'border-gray-200'} max-h-32`}>
            <ScrollView>
              {searchResults.map((result, index) => (
                <TouchableOpacity
                  key={index}
                  className="p-3 border-b border-gray-200 last:border-b-0"
                  onPress={() => {
                    handleLocationSelect({
                      latitude: result.latitude,
                      longitude: result.longitude,
                    });
                    setSearchResults([]);
                    setSearchQuery('');
                  }}
                >
                  <Text className={`text-sm ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    📍 {result.address}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        {/* Route Summary */}
        {journeyResult?.route_options?.[selectedRoute] && (
          <View className={`${isDark ? 'bg-blue-900' : 'bg-blue-50'} rounded-xl p-3 border ${isDark ? 'border-blue-800' : 'border-blue-200'}`}>
            <Text className={`text-sm font-semibold ${isDark ? 'text-blue-100' : 'text-blue-800'}`}>
              🚌 {journeyResult.route_options[selectedRoute].total_duration} • 
              📏 {journeyResult.route_options[selectedRoute].total_distance}
              {journeyResult.route_options[selectedRoute].total_cost && 
                ` • 💰 LKR ${journeyResult.route_options[selectedRoute].total_cost}`
              }
            </Text>
          </View>
        )}
      </View>

      {/* Map Container - Takes remaining space */}
      <View className="flex-1">
        {console.log('🗺️ Passing to RouteMap - journeyResult:', journeyResult)}
        {console.log('🗺️ Passing to RouteMap - selectedRoute:', selectedRoute)}  
        {console.log('🗺️ Passing to RouteMap - route:', journeyResult?.route_options?.[selectedRoute])}
        <RouteMap
          origin={origin}
          destination={destination}
          route={journeyResult?.route_options?.[selectedRoute]}
          showUserLocation={true}
          onLocationSelect={handleLocationSelect}
        />
      </View>

      {/* Bottom Status */}
      <View className={`${isDark ? 'bg-gray-800' : 'bg-white'} px-4 py-2 border-t ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <Text className={`text-xs text-center ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
          {!origin && !destination ? 'Tap on the map to set origin and destination' :
           !destination ? 'Tap map again to set destination' :
           'Ready to plan your journey!'}
        </Text>
      </View>
    </SafeAreaView>
  );
}