import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Alert, Modal, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { RouteOption } from '../../../src/types';
import { useRoutes, useAuth } from '../../../src/contexts/AppContext';
import { useRouter } from 'expo-router';
import { useFocusEffect } from '@react-navigation/native';
import { useTheme } from '../../../src/contexts/ThemeContext';
import { useLanguage } from '../../../src/contexts/LanguageContext';
import { LinearGradient } from 'expo-linear-gradient';

// Utility function to convert various distance formats to kilometers
const convertToKilometers = (distanceText: string): string => {
  if (!distanceText || distanceText === 'Distance not available' || distanceText === 'N/A') {
    return 'Distance not available';
  }

  // Extract number from the distance text
  const numberMatch = distanceText.match(/[\d.]+/);
  if (!numberMatch) {
    return distanceText; // Return original if no number found
  }

  const value = parseFloat(numberMatch[0]);
  const text = distanceText.toLowerCase();

  let kilometers = 0;

  // Convert to kilometers based on unit
  if (text.includes('km')) {
    kilometers = value;
  } else if (text.includes('mi') || text.includes('mile')) {
    kilometers = value * 1.60934; // Miles to km
  } else if (text.includes('ft') || text.includes('feet')) {
    kilometers = value * 0.0003048; // Feet to km
  } else if (text.includes('m') && !text.includes('mi') && !text.includes('km')) {
    kilometers = value / 1000; // Meters to km
  } else if (text.includes('yd') || text.includes('yard')) {
    kilometers = value * 0.0009144; // Yards to km
  } else {
    // If no unit specified, assume it's already in km
    kilometers = value;
  }

  // Format the output appropriately
  if (kilometers < 0.001) {
    return `${Math.round(kilometers * 1000000)} mm`;
  } else if (kilometers < 1) {
    return `${Math.round(kilometers * 1000)} m`;
  } else if (kilometers < 10) {
    return `${kilometers.toFixed(1)} km`;
  } else {
    return `${Math.round(kilometers)} km`;
  }
};

// Helper function to parse duration text to minutes
const parseDurationToMinutes = (durationText: string): number => {
  if (!durationText || durationText === 'N/A' || durationText === 'Duration not available') {
    return 0;
  }

  let totalMinutes = 0;
  const text = durationText.toLowerCase();

  // Extract hours
  const hoursMatch = text.match(/(\d+)\s*(?:hour|hr|h)/);
  if (hoursMatch) {
    totalMinutes += parseInt(hoursMatch[1]) * 60;
  }

  // Extract minutes
  const minutesMatch = text.match(/(\d+)\s*(?:minute|min|m)/);
  if (minutesMatch) {
    totalMinutes += parseInt(minutesMatch[1]);
  }

  // Extract seconds (convert to minutes)
  const secondsMatch = text.match(/(\d+)\s*(?:second|sec|s)/);
  if (secondsMatch) {
    totalMinutes += Math.round(parseInt(secondsMatch[1]) / 60);
  }

  return totalMinutes;
};

// Helper function to parse distance text to kilometers
const parseDistanceToKilometers = (distanceText: string): number => {
  if (!distanceText || distanceText === 'N/A' || distanceText === 'Distance not available') {
    return 0;
  }

  const numberMatch = distanceText.match(/[\d.]+/);
  if (!numberMatch) {
    return 0;
  }

  const value = parseFloat(numberMatch[0]);
  const text = distanceText.toLowerCase();

  let kilometers = 0;

  if (text.includes('km')) {
    kilometers = value;
  } else if (text.includes('mi') || text.includes('mile')) {
    kilometers = value * 1.60934;
  } else if (text.includes('ft') || text.includes('feet')) {
    kilometers = value * 0.0003048;
  } else if (text.includes('m') && !text.includes('mi') && !text.includes('km')) {
    kilometers = value / 1000;
  } else if (text.includes('yd') || text.includes('yard')) {
    kilometers = value * 0.0009144;
  } else {
    kilometers = value;
  }

  return kilometers;
};

// Helper function to format minutes to readable duration
const formatMinutesToDuration = (minutes: number): string => {
  if (minutes <= 0) {
    return 'Duration not available';
  }

  if (minutes < 60) {
    return `${minutes} min${minutes !== 1 ? 's' : ''}`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (remainingMinutes === 0) {
    return `${hours} hour${hours !== 1 ? 's' : ''}`;
  }

  return `${hours} hour${hours !== 1 ? 's' : ''} ${remainingMinutes} min${remainingMinutes !== 1 ? 's' : ''}`;
};

// Helper function to format kilometers to readable distance
const formatKilometersToDistance = (kilometers: number): string => {
  if (kilometers <= 0) {
    return 'Distance not available';
  }

  if (kilometers < 1) {
    return `${Math.round(kilometers * 1000)} m`;
  } else if (kilometers < 10) {
    return `${kilometers.toFixed(1)} km`;
  } else {
    return `${Math.round(kilometers)} km`;
  }
};

// Calculate total duration from individual steps
const calculateTotalDurationFromSteps = (route: RouteOption): string => {
  const steps = route.steps || (route as any).route_data?.steps || [];

  if (steps.length === 0) {
    // Fallback to route-level duration if no steps
    return (route as any).route_data?.duration_text || route.duration || 'Duration not available';
  }

  let totalMinutes = 0;

  for (const step of steps) {
    const stepDuration = (step as any).duration;
    if (stepDuration) {
      totalMinutes += parseDurationToMinutes(stepDuration);
    }
  }

  if (totalMinutes === 0) {
    // Fallback to route-level duration if steps don't have duration
    return (route as any).route_data?.duration_text || route.duration || 'Duration not available';
  }

  return formatMinutesToDuration(totalMinutes);
};

// Calculate total distance from individual steps
const calculateTotalDistanceFromSteps = (route: RouteOption): string => {
  const steps = route.steps || (route as any).route_data?.steps || [];

  if (steps.length === 0) {
    // Fallback to route-level distance if no steps
    const fallbackDistance = (route as any).route_data?.distance_text || (route as any).distance || 'Distance not available';
    return convertToKilometers(fallbackDistance);
  }

  let totalKilometers = 0;

  for (const step of steps) {
    const stepDistance = (step as any).distance;
    if (stepDistance) {
      totalKilometers += parseDistanceToKilometers(stepDistance);
    }
  }

  if (totalKilometers === 0) {
    // Fallback to route-level distance if steps don't have distance
    const fallbackDistance = (route as any).route_data?.distance_text || (route as any).distance || 'Distance not available';
    return convertToKilometers(fallbackDistance);
  }

  return formatKilometersToDistance(totalKilometers);
};


export default function Routes() {
  const { loadTravelRequestsFromBackend } = useRoutes();
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const { theme } = useTheme();
  const { t } = useLanguage();
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);
  const [recentRoutes, setRecentRoutes] = useState<RouteOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRouteForModal, setSelectedRouteForModal] = useState<RouteOption | null>(null);
  const [showRouteModal, setShowRouteModal] = useState(false);

  // Collapsible section states
  const [expandedSections, setExpandedSections] = useState<{[key: string]: boolean}>({
    steps: true,
    alternatives: false,
    aiAnalysis: true,
    disruption: true,
    technical: false,
    destination: true
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // SINGLE UNIFIED REFRESH MECHANISM
  const refreshData = useCallback(async () => {
    setIsLoading(true);
    console.log('🔄 Refreshing route data...');
    
    try {
      // Check if user is authenticated
      if (!isAuthenticated || !user) {
        console.log('❌ User not authenticated, cannot load routes');
        setRecentRoutes([]);
        return;
      }
      
      console.log('👤 Loading travel requests for authenticated user:', user.user_id);
      
      // Load from travel requests (backend) - primary source
      const backendRoutes = await loadTravelRequestsFromBackend();
      if (backendRoutes.length > 0) {
        console.log('✅ Loaded travel requests from backend:', backendRoutes.length, 'requests');
        setRecentRoutes(backendRoutes.slice(0, 10)); // Show last 10 travel requests
      } else {
        console.log('⚠️ No travel requests found in backend for user:', user.user_id);
        // If no backend data, try local storage as fallback
        const storedRoutes = await AsyncStorage.getItem('recent_routes');
        if (storedRoutes) {
          const localRoutes: RouteOption[] = JSON.parse(storedRoutes);
          console.log('💾 Using fallback local routes:', localRoutes.length);
          setRecentRoutes(localRoutes.slice(0, 5));
        } else {
          console.log('📭 No local routes found either');
          setRecentRoutes([]);
        }
      }
      
    } catch (error: any) {
      console.error('❌ Error refreshing route data:', error);
      console.error('📋 Error details:', {
        message: error?.message,
        stack: error?.stack,
        name: error?.name
      });
      
      // Fallback to local storage on error
      try {
        const storedRoutes = await AsyncStorage.getItem('recent_routes');
        if (storedRoutes) {
          const localRoutes: RouteOption[] = JSON.parse(storedRoutes);
          console.log('💾 Error fallback: using local routes:', localRoutes.length);
          setRecentRoutes(localRoutes.slice(0, 5));
        } else {
          console.log('📭 No local routes available as fallback');
          setRecentRoutes([]);
        }
      } catch (localError: any) {
        console.error('❌ Error loading local routes:', localError);
        setRecentRoutes([]);
      }
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, user, loadTravelRequestsFromBackend]);

  // Load on component mount
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  // Reload when screen is focused
  useFocusEffect(
    useCallback(() => {
      refreshData();
    }, [refreshData])
  );






  return (
    <SafeAreaView className="flex-1" style={{ backgroundColor: theme.background }}>
      <ScrollView 
        className="flex-1"
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={refreshData}
            tintColor={theme.primary}
          />
        }
      >
        {/* Header */}
        <View className="px-4 py-4 border-b" style={{ backgroundColor: theme.surface, borderColor: theme.border }}>
          <View className="flex-row items-center justify-between">
            <View>
              <Text className="text-2xl font-bold" style={{ color: theme.text }}>{t('routes.title')}</Text>
              <Text className="text-sm" style={{ color: theme.textSecondary }}>{t('routes.subtitle')}</Text>
            </View>
            <View className="flex-row space-x-2">
              <TouchableOpacity
                onPress={async () => {
                  console.log('🧪 Testing travel requests connection...');
                  try {
                    // Test both connection and data fetching
                    console.log('📡 Testing backend connection...');
                    const testRequests = await loadTravelRequestsFromBackend();
                    console.log('✅ Travel requests test successful:', testRequests.length, 'requests');
                    
                    // Log detailed route data for debugging
                    if (testRequests.length > 0) {
                      const firstRoute = testRequests[0];
                      console.log('🔍 First route data sample:', {
                        route_id: firstRoute.route_id,
                        source: firstRoute.source,
                        destination: firstRoute.destination,
                        duration: firstRoute.duration,
                        fare: firstRoute.fare,
                        route_data: {
                          duration_text: (firstRoute as any).route_data?.duration_text,
                          distance_text: (firstRoute as any).route_data?.distance_text,
                          estimated_cost: (firstRoute as any).route_data?.estimated_cost,
                          cost_currency: (firstRoute as any).route_data?.cost_currency
                        }
                      });
                    }
                    
                    // Show detailed connection info
                    const backendUrl = 'http://10.47.78.83:8000/api/v1';
                    const connectionInfo = `
✅ Backend Connection: SUCCESS
📊 Travel Requests Found: ${testRequests.length}
🔗 Backend URL: ${backendUrl}
👤 User ID: ${user?.user_id || 'Not available'}
📧 User Email: ${user?.email || 'Not available'}
🔑 Authenticated: ${isAuthenticated ? 'Yes' : 'No'}

${testRequests.length > 0 ? `
📋 Sample Route Data:
🚌 Route: ${testRequests[0].source} → ${testRequests[0].destination}
⏱️ Duration: ${testRequests[0].duration}
💰 Fare: ${testRequests[0].fare}
📏 Distance: ${(testRequests[0] as any).route_data?.distance_text || 'N/A'}
` : ''}
                    `.trim();
                    
                    Alert.alert('Backend Test - SUCCESS', connectionInfo);
                  } catch (error: any) {
                    console.error('❌ Travel requests test failed:', error);
                    
                    // Show detailed error info
                    const errorInfo = `
❌ Backend Connection: FAILED
🔗 Trying to connect to: http://10.47.78.83:8000/api/v1
👤 User ID: ${user?.user_id || 'Not available'}
📧 User Email: ${user?.email || 'Not available'}
🔑 Authenticated: ${isAuthenticated ? 'Yes' : 'No'}

Error Details:
${error?.message || 'Unknown error'}

Troubleshooting:
1. Check if backend is running on port 8000
2. Verify network connection
3. Check firewall settings
4. Ensure user is logged in
                    `.trim();
                    
                    Alert.alert('Backend Test - FAILED', errorInfo);
                  }
                }}
                className="bg-green-100 p-3 rounded-full mr-2"
              >
                <Ionicons name="bug" size={16} color="#10B981" />
              </TouchableOpacity>
              
              <TouchableOpacity
                onPress={refreshData}
                className="bg-blue-100 p-3 rounded-full"
                disabled={isLoading}
              >
                <Ionicons 
                  name="refresh" 
                  size={20} 
                  color={isLoading ? "#9CA3AF" : "#3B82F6"} 
                />
              </TouchableOpacity>
            </View>
          </View>
        </View>



        {/* Route Options */}
        <View className="px-4 mt-4">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-lg font-semibold" style={{ color: theme.text }}>{t('routes.recent')}</Text>
            
            {/* Connection Status Indicator */}
            <View className="flex-row items-center bg-gray-100 px-3 py-1 rounded-full">
              <View className={`w-2 h-2 rounded-full mr-2 ${isAuthenticated ? 'bg-green-500' : 'bg-red-500'}`} />
              <Text className="text-xs text-gray-600">
                {isAuthenticated ? `Backend: ${user?.email ? 'Connected' : 'Connecting...'}` : 'Not authenticated'}
              </Text>
            </View>
          </View>
          
          {isLoading ? (
            <View className="p-6 rounded-lg shadow-sm items-center" style={{ backgroundColor: theme.surface }}>
              <Text className="text-4xl mb-2">🔄</Text>
              <Text className="text-lg font-medium" style={{ color: theme.text }}>{t('routes.loading')}</Text>
              <Text className="text-sm mt-2" style={{ color: theme.textSecondary }}>
                Fetching from backend... User: {user?.email || 'Not logged in'}
              </Text>
            </View>
          ) : recentRoutes.length === 0 ? (
            <View className="p-6 rounded-lg shadow-sm items-center" style={{ backgroundColor: theme.surface }}>
              <Text className="text-4xl mb-2">🗺️</Text>
              <Text className="text-lg font-medium mb-2" style={{ color: theme.text }}>No Route History Available</Text>
              <Text className="text-sm text-center mb-4" style={{ color: theme.textSecondary }}>
                {isAuthenticated ? 
                  'No travel requests found in database. Start planning your journey from the Home tab to see AI-generated route options here.' :
                  'Please log in to see your route history and travel requests.'
                }
              </Text>
              <View className="flex-row space-x-2">
                <TouchableOpacity 
                  className="bg-blue-600 px-4 py-2 rounded-lg"
                  onPress={() => {
                    // Navigate to home tab for route planning
                    router.push('/(main)/(tabs)/home');
                  }}
                >
                  <Text className="text-white font-medium">Plan a Route</Text>
                </TouchableOpacity>
                
                {isAuthenticated && (
                  <TouchableOpacity 
                    className="bg-gray-600 px-4 py-2 rounded-lg ml-2"
                    onPress={refreshData}
                  >
                    <Text className="text-white font-medium">Refresh</Text>
                  </TouchableOpacity>
                )}
              </View>
              
              {/* Database Status Indicator */}
              <View className="mt-4 bg-gray-100 px-3 py-2 rounded-lg">
                <Text className="text-xs text-gray-600 text-center">
                  📊 Database Status: {isAuthenticated ? 'Connected - No routes stored yet' : 'Requires authentication'}
                </Text>
              </View>
            </View>
          ) : (
            <View className="space-y-4">
              {recentRoutes.map((route, index) => {
                // Use MongoDB _id or route_id for stable unique keys
                const uniqueKey = (route as any)._id || route.route_id || route.id || `route-${index}`;

                return (
                <View key={uniqueKey} className="bg-white rounded-lg shadow-sm overflow-hidden">
                  <TouchableOpacity
                    className="p-4"
                    onPress={() => {
                      setSelectedRoute(selectedRoute === uniqueKey ? null : uniqueKey);
                    }}
                  >
                    <View className="flex-row items-center justify-between mb-2">
                      <Text className="text-lg font-semibold text-gray-800">
                        {/* Display route from backend data */}
                        {route.source && route.destination ? 
                          `${route.source} → ${route.destination}` :
                          (route.title || `Route ${route.route_id || route.id || index + 1}`)}
                      </Text>
                      <View className="flex-row">
                        {(route.modes || ['🚌']).map((mode: string, modeIndex: number) => (
                          <Text key={modeIndex} className="text-lg ml-1">
                            {typeof mode === 'string' && mode.includes('🚌') ? mode : 
                             mode === 'bus' ? '🚌' : 
                             mode === 'train' ? '🚆' : 
                             mode === 'TRANSIT' ? '🚊' :
                             mode === 'walking' ? '🚶' : 
                             mode === 'tuk-tuk' ? '🛺' : 
                             mode === 'car' ? '🚗' : '🚌'}
                          </Text>
                        ))}
                      </View>
                    </View>
                    
                    <View className="flex-row items-center mb-3">
                      {/* Duration from backend route_data */}
                      <View className="flex-row items-center mr-4">
                            <Ionicons name="time" size={16} color="#6b7280" />
                            <Text className="text-sm text-gray-600 ml-1">
                              {/* Use total duration calculated from steps if available */}
                              {calculateTotalDurationFromSteps(route)}
                            </Text>
                      </View>
                      
                      {/* Start/End Times */}
                      {((route as any).route_data?.start_time || (route as any).route_data?.end_time) && (
                        <View className="flex-row items-center mr-4">
                          <Ionicons name="alarm" size={16} color="#059669" />
                          <Text className="text-sm text-green-600 ml-1">
                            {(route as any).route_data?.start_time || '--'} - {(route as any).route_data?.end_time || '--'}
                          </Text>
                        </View>
                      )}
                      
                      {/* Fare from backend route_data */}
                      <View className="flex-row items-center mr-4">
                        <Ionicons name="cash" size={16} color="#6b7280" />
                        <Text className="text-sm text-gray-600 ml-1">
                          {((route as any).route_data?.estimated_cost ? 
                            `${(route as any).route_data?.cost_currency || 'Rs.'} ${(route as any).route_data.estimated_cost}` :
                            (route.fare || 'Fare not available'))}
                        </Text>
                      </View>
                      
                      {/* Distance from backend route_data */}
                      <View className="flex-row items-center">
                            <Ionicons name="map" size={16} color="#10b981" />
                            <Text className="text-sm text-green-600 ml-1">
                              {/* Use total distance calculated from steps if available */}
                              {calculateTotalDistanceFromSteps(route)}
                            </Text>
                      </View>
                    </View>

                    <View className="bg-blue-50 p-3 rounded-lg mb-3">
                      <Text className="text-sm font-medium text-blue-800">🤖 AI Recommendation</Text>
                      <Text className="text-sm text-blue-700">
                        {route.aiRecommendation || 'AI-optimized route for best travel experience'}
                      </Text>
                    </View>

                    {(route.disruptions || []).length > 0 && (
                      <View className="bg-orange-50 p-3 rounded-lg mb-3">
                        <Text className="text-sm font-medium text-orange-800">⚠️ Current Disruptions</Text>
                        {(route.disruptions || []).map((disruption: string, index: number) => (
                          <Text key={index} className="text-sm text-orange-700">{disruption}</Text>
                        ))}
                      </View>
                    )}

                    <View className="flex-row items-center justify-between">
                      <TouchableOpacity 
                        className="flex-1 bg-blue-600 py-2 px-4 rounded-lg mr-2"
                        onPress={() => {
                          setSelectedRouteForModal(route);
                          setShowRouteModal(true);
                        }}
                      >
                        <Text className="text-white text-center font-medium">View Details</Text>
                      </TouchableOpacity>
                      <TouchableOpacity className="p-2">
                        <Ionicons
                          name={selectedRoute === uniqueKey ? "chevron-up" : "chevron-down"}
                          size={20}
                          color="#6b7280"
                        />
                      </TouchableOpacity>
                    </View>
                  </TouchableOpacity>

                  {/* Expanded Details */}
                  {selectedRoute === uniqueKey && (
                    <View className="border-t border-gray-100 p-4">
                      {/* Route Steps */}
                      <Text className="text-sm font-medium text-gray-800 mb-3">Route Steps</Text>
                      <View className="space-y-3 mb-4">
                        {(route.steps || []).map((step: any, index: number) => (
                          <View key={index} className="flex-row items-center">
                            <Text className="text-lg mr-3">{step.icon || '🚶'}</Text>
                            <View className="flex-1">
                              <Text className="text-sm font-medium text-gray-800">{step.description || step.instruction}</Text>
                              <Text className="text-xs text-gray-600">{step.duration}</Text>
                            </View>
                          </View>
                        ))}
                      </View>

                      {/* AI Agents Used */}
                      <Text className="text-sm font-medium text-gray-800 mb-2">AI Agents Used</Text>
                      <View className="flex-row flex-wrap">
                        {(route.agentsUsed || []).map((agent: string, index: number) => (
                          <View key={index} className="bg-purple-100 px-2 py-1 rounded-full mr-2 mb-2">
                            <Text className="text-xs text-purple-700">{agent}</Text>
                          </View>
                        ))}
                      </View>
                    </View>
                  )}
                </View>
              );
              })}
            </View>
          )}
        </View>

        {/* Tips */}
        <View className="bg-white mx-4 mt-4 mb-8 p-4 rounded-lg shadow-sm">
          <Text className="text-lg font-semibold text-gray-800 mb-3">💡 Smart Tips</Text>
          <View className="space-y-2">
            <Text className="text-sm text-gray-700">• Routes are optimized using 10 AI agents for best results</Text>
            <Text className="text-sm text-gray-700">• Real-time disruption monitoring keeps you updated</Text>
            <Text className="text-sm text-gray-700">• Fare optimization finds the cheapest combinations</Text>
            <Text className="text-sm text-gray-700">• Enable notifications for route updates</Text>
          </View>
        </View>
      </ScrollView>

      {/* Route Details Modal - Enhanced UI */}
      <Modal
        visible={showRouteModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView className="flex-1" style={{backgroundColor: '#f8fafc'}}>
          <LinearGradient
            colors={['#3B82F6', '#2563EB']}
            start={{x: 0, y: 0}}
            end={{x: 1, y: 1}}
            style={{paddingVertical: 20, paddingHorizontal: 16}}
          >
            <View className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-2xl font-bold text-white mb-1">Route Details</Text>
                <Text className="text-sm text-blue-100">AI-Optimized Travel Plan</Text>
              </View>
              <TouchableOpacity
                onPress={() => setShowRouteModal(false)}
                className="bg-white/20 p-2 rounded-full"
              >
                <Ionicons name="close" size={24} color="#ffffff" />
              </TouchableOpacity>
            </View>
          </LinearGradient>
          
          <ScrollView className="flex-1">
            {selectedRouteForModal && (
              <View className="p-4">
                {/* Route Header - Enhanced Card */}
                <View className="bg-white rounded-2xl p-6 mb-4 shadow-lg" style={{borderLeftWidth: 4, borderLeftColor: '#3B82F6'}}>
                  <View className="flex-row items-center mb-3">
                    <View className="bg-blue-100 p-3 rounded-full mr-3">
                      <Ionicons name="navigate" size={24} color="#3B82F6" />
                    </View>
                    <View className="flex-1">
                      <Text className="text-xs text-gray-500 uppercase font-semibold mb-1">Your Journey</Text>
                      <Text className="text-2xl font-bold text-gray-800" numberOfLines={2}>
                        {selectedRouteForModal.title ||
                         (selectedRouteForModal.source && selectedRouteForModal.destination && selectedRouteForModal.source !== 'Unknown' ?
                          `${selectedRouteForModal.source} → ${selectedRouteForModal.destination}` :
                          (selectedRouteForModal.route_data?.origin && selectedRouteForModal.route_data?.destination ?
                            `${selectedRouteForModal.route_data.origin} → ${selectedRouteForModal.route_data.destination}` : 'Route Details'))}
                      </Text>
                    </View>
                  </View>
                  <View className="flex-row items-center">
                    <View className="bg-gray-100 px-3 py-1.5 rounded-full">
                      <Text className="text-xs text-gray-600 font-mono">{selectedRouteForModal.route_id || selectedRouteForModal.id}</Text>
                    </View>
                  </View>
                </View>

                {/* Key Metrics - Enhanced Grid Layout */}
                <View className="mb-4">
                  <Text className="text-lg font-bold text-gray-800 mb-3 px-1">📊 Key Metrics</Text>
                  <View className="flex-row flex-wrap gap-3" style={{gap: 12}}>
                    {/* Duration - calculated from steps for accuracy */}
                    <View className="flex-1" style={{minWidth: '48%'}}>
                      <LinearGradient
                        colors={['#EFF6FF', '#DBEAFE']}
                        start={{x: 0, y: 0}}
                        end={{x: 1, y: 1}}
                        style={{borderRadius: 16, padding: 16}}
                      >
                        <View className="flex-row items-center mb-2">
                          <View className="bg-blue-500 p-2 rounded-full">
                            <Ionicons name="time" size={18} color="#ffffff" />
                          </View>
                          <Text className="text-xs text-blue-600 font-semibold ml-2 uppercase">Duration</Text>
                        </View>
                        <Text className="text-xl font-bold text-gray-800">
                          {calculateTotalDurationFromSteps(selectedRouteForModal)}
                        </Text>
                      </LinearGradient>
                    </View>

                    {/* Fare - always show with gradient card */}
                    <View className="flex-1" style={{minWidth: '48%'}}>
                      <LinearGradient
                        colors={['#FEF3C7', '#FDE68A']}
                        start={{x: 0, y: 0}}
                        end={{x: 1, y: 1}}
                        style={{borderRadius: 16, padding: 16}}
                      >
                        <View className="flex-row items-center mb-2">
                          <View className="bg-yellow-600 p-2 rounded-full">
                            <Ionicons name="cash" size={18} color="#ffffff" />
                          </View>
                          <Text className="text-xs text-yellow-800 font-semibold ml-2 uppercase">Total Fare</Text>
                        </View>
                        <Text className="text-xl font-bold text-gray-800">
                          {(selectedRouteForModal as any).route_data?.estimated_cost ?
                            `${(selectedRouteForModal as any).route_data.cost_currency || 'LKR'} ${(selectedRouteForModal as any).route_data.estimated_cost}` :
                            ((selectedRouteForModal as any).fare ||
                             (selectedRouteForModal.summary?.estimated_fare ? `LKR ${selectedRouteForModal.summary.estimated_fare}` :
                              'Fare not available'))}
                        </Text>
                      </LinearGradient>
                    </View>

                    {/* Distance - calculated from steps for accuracy */}
                    <View className="flex-1" style={{minWidth: '48%'}}>
                      <LinearGradient
                        colors={['#D1FAE5', '#A7F3D0']}
                        start={{x: 0, y: 0}}
                        end={{x: 1, y: 1}}
                        style={{borderRadius: 16, padding: 16}}
                      >
                        <View className="flex-row items-center mb-2">
                          <View className="bg-green-600 p-2 rounded-full">
                            <Ionicons name="map" size={18} color="#ffffff" />
                          </View>
                          <Text className="text-xs text-green-800 font-semibold ml-2 uppercase">Distance</Text>
                        </View>
                        <Text className="text-xl font-bold text-gray-800">
                          {calculateTotalDistanceFromSteps(selectedRouteForModal)}
                        </Text>
                      </LinearGradient>
                    </View>

                    {/* Start/End Times - if available */}
                    {(selectedRouteForModal.route_data?.start_time || selectedRouteForModal.route_data?.end_time) && (
                      <View className="flex-1" style={{minWidth: '48%'}}>
                        <LinearGradient
                          colors={['#FEF3C7', '#FDE68A']}
                          start={{x: 0, y: 0}}
                          end={{x: 1, y: 1}}
                          style={{borderRadius: 16, padding: 16}}
                        >
                          <View className="flex-row items-center mb-2">
                            <View className="bg-amber-600 p-2 rounded-full">
                              <Ionicons name="alarm" size={18} color="#ffffff" />
                            </View>
                            <Text className="text-xs text-amber-800 font-semibold ml-2 uppercase">Schedule</Text>
                          </View>
                          <Text className="text-lg font-bold text-gray-800">
                            {selectedRouteForModal.route_data?.start_time || '--'} - {selectedRouteForModal.route_data?.end_time || '--'}
                          </Text>
                        </LinearGradient>
                      </View>
                    )}

                    {/* Transfers - if available */}
                    {selectedRouteForModal.route_data?.transfers !== undefined && (
                      <View className="flex-1" style={{minWidth: '48%'}}>
                        <LinearGradient
                          colors={['#E0E7FF', '#C7D2FE']}
                          start={{x: 0, y: 0}}
                          end={{x: 1, y: 1}}
                          style={{borderRadius: 16, padding: 16}}
                        >
                          <View className="flex-row items-center mb-2">
                            <View className="bg-indigo-600 p-2 rounded-full">
                              <Ionicons name="git-branch" size={18} color="#ffffff" />
                            </View>
                            <Text className="text-xs text-indigo-800 font-semibold ml-2 uppercase">Transfers</Text>
                          </View>
                          <Text className="text-xl font-bold text-gray-800">
                            {selectedRouteForModal.route_data.transfers} transfer{selectedRouteForModal.route_data.transfers !== 1 ? 's' : ''}
                          </Text>
                        </LinearGradient>
                      </View>
                    )}
                  </View>
                </View>

                {/* Transport Modes */}
                <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                  <Text className="text-lg font-semibold text-gray-800 mb-3">🚌 Transport Modes</Text>
                  {(() => {
                    const modes = (selectedRouteForModal as any).route_data?.transit_modes || 
                                 (selectedRouteForModal as any).modes || 
                                 [];
                    
                    if (modes.length > 0) {
                      return (
                        <View className="flex-row flex-wrap">
                          {modes.map((mode: string, index: number) => (
                            <View key={index} className="bg-blue-100 px-3 py-1 rounded-full mr-2 mb-2">
                              <Text className="text-blue-700 font-medium">
                                {mode === 'bus' ? '🚌 Bus' : 
                                 mode === 'train' ? '🚆 Train' : 
                                 mode === 'walking' ? '🚶 Walking' : 
                                 mode === 'tuk-tuk' ? '🛺 Tuk-tuk' : 
                                 mode === 'car' ? '🚗 Car' : 
                                 mode === 'driving' ? '🚗 Driving' :
                                 mode === 'uber' ? '� Uber/PickMe' :
                                 mode === 'transit' ? '� Transit' :
                                 mode}
                              </Text>
                            </View>
                          ))}
                        </View>
                      );
                    }
                    
                    return <Text className="text-gray-500 italic">Transport mode information not available from backend</Text>;
                  })()}
                </View>

                {/* Fare Optimization Section */}
                {selectedRouteForModal.route_data?.fare_optimization && (
                  <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                    <Text className="text-lg font-semibold text-gray-800 mb-3">💰 Fare Optimization</Text>
                    
                    {/* Savings Summary */}
                    <View className="bg-green-50 rounded-lg p-3 mb-3">
                      <View className="flex-row items-center justify-between mb-2">
                        <Text className="text-sm font-medium text-green-800">💡 Best Savings Option</Text>
                        <View className="bg-green-200 px-2 py-1 rounded">
                          <Text className="text-sm font-bold text-green-800">
                            Save {selectedRouteForModal.route_data.fare_optimization.best_option?.savings || 0} {selectedRouteForModal.route_data.cost_currency || 'LKR'}
                          </Text>
                        </View>
                      </View>
                      <Text className="text-sm text-green-700 mb-2">
                        {selectedRouteForModal.route_data.fare_optimization.best_option?.description || 'Savings available'}
                      </Text>
                      <View className="flex-row items-center justify-between">
                        <Text className="text-xs text-green-600">
                          Original: {selectedRouteForModal.route_data.fare_optimization.original_cost} {selectedRouteForModal.route_data.cost_currency || 'LKR'}
                        </Text>
                        <Text className="text-xs text-green-600">
                          Optimized: {selectedRouteForModal.route_data.fare_optimization.optimized_cost} {selectedRouteForModal.route_data.cost_currency || 'LKR'}
                        </Text>
                      </View>
                    </View>

                    {/* All Discount Options */}
                    <Text className="text-sm font-medium text-gray-800 mb-2">Available Discounts</Text>
                    <View className="space-y-2">
                      {(selectedRouteForModal.route_data.fare_optimization.all_options || []).map((option: any, index: number) => (
                        <View key={index} className={`rounded-lg p-3 ${option.applicable ? 'bg-blue-50' : 'bg-gray-50'}`}>
                          <View className="flex-row items-center justify-between mb-1">
                            <Text className={`text-sm font-medium ${option.applicable ? 'text-blue-800' : 'text-gray-600'}`}>
                              {option.type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                            </Text>
                            <View className={`px-2 py-1 rounded ${option.applicable ? 'bg-blue-200' : 'bg-gray-200'}`}>
                              <Text className={`text-xs font-bold ${option.applicable ? 'text-blue-700' : 'text-gray-600'}`}>
                                -{option.savings} {(selectedRouteForModal as any).route_data?.cost_currency || 'LKR'}
                              </Text>
                            </View>
                          </View>
                          <Text className={`text-xs ${option.applicable ? 'text-blue-600' : 'text-gray-500'}`}>
                            {option.description}
                          </Text>
                          {!option.applicable && (
                            <Text className="text-xs text-red-600 mt-1">Not applicable for this journey</Text>
                          )}
                        </View>
                      ))}
                    </View>
                  </View>
                )}

                {/* Walking Distance Info */}
                {(selectedRouteForModal.route_data?.walking_distance !== undefined || selectedRouteForModal.route_data?.mode_details?.walking_km !== undefined) && (
                  <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                    <Text className="text-lg font-semibold text-gray-800 mb-3">🚶 Walking Details</Text>
                    <View className="bg-blue-50 rounded-lg p-3">
                      <View className="flex-row items-center justify-between">
                        <Text className="text-sm font-medium text-blue-800">Total Walking Distance</Text>
                        <Text className="text-lg font-bold text-blue-700">
                          {selectedRouteForModal.route_data?.walking_distance !== undefined ? 
                            `${selectedRouteForModal.route_data.walking_distance} km` :
                            `${selectedRouteForModal.route_data?.mode_details?.walking_km || 0} km`}
                        </Text>
                      </View>
                      <Text className="text-xs text-blue-600 mt-1">
                        This includes walking to/from stops and transfers
                      </Text>
                    </View>
                  </View>
                )}

                {/* Active Disruptions */}
                {(selectedRouteForModal.active_disruptions || (selectedRouteForModal as any).response?.active_disruptions || []).length > 0 && (
                  <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                    <Text className="text-lg font-semibold text-gray-800 mb-3">🚨 Active Disruptions</Text>
                    <View className="space-y-3">
                      {((selectedRouteForModal.active_disruptions || (selectedRouteForModal as any).response?.active_disruptions || []) as any[]).map((disruption: any, index: number) => (
                        <View key={index} className={`rounded-lg p-3 ${
                          disruption.severity === 'high' ? 'bg-red-50 border-l-4 border-red-500' :
                          disruption.severity === 'medium' ? 'bg-orange-50 border-l-4 border-orange-500' :
                          'bg-yellow-50 border-l-4 border-yellow-500'
                        }`}>
                          <View className="flex-row items-center justify-between mb-2">
                            <Text className={`text-sm font-semibold ${
                              disruption.severity === 'high' ? 'text-red-800' :
                              disruption.severity === 'medium' ? 'text-orange-800' :
                              'text-yellow-800'
                            }`}>
                              {disruption.type?.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()) || 'Disruption'}
                            </Text>
                            <View className={`px-2 py-1 rounded ${
                              disruption.severity === 'high' ? 'bg-red-200' :
                              disruption.severity === 'medium' ? 'bg-orange-200' :
                              'bg-yellow-200'
                            }`}>
                              <Text className={`text-xs font-bold ${
                                disruption.severity === 'high' ? 'text-red-700' :
                                disruption.severity === 'medium' ? 'text-orange-700' :
                                'text-yellow-700'
                              }`}>
                                {disruption.severity?.toUpperCase() || 'INFO'}
                              </Text>
                            </View>
                          </View>
                          
                          {disruption.location && (
                            <Text className={`text-xs mb-1 ${
                              disruption.severity === 'high' ? 'text-red-700' :
                              disruption.severity === 'medium' ? 'text-orange-700' :
                              'text-yellow-700'
                            }`}>
                              📍 Location: {disruption.location}
                            </Text>
                          )}
                          
                          <Text className={`text-sm ${
                            disruption.severity === 'high' ? 'text-red-700' :
                            disruption.severity === 'medium' ? 'text-orange-700' :
                            'text-yellow-700'
                          }`}>
                            {disruption.description || 'No details available'}
                          </Text>
                          
                          {disruption.timestamp && (
                            <Text className={`text-xs mt-1 ${
                              disruption.severity === 'high' ? 'text-red-600' :
                              disruption.severity === 'medium' ? 'text-orange-600' :
                              'text-yellow-600'
                            }`}>
                              ⏰ {new Date(disruption.timestamp).toLocaleString()}
                            </Text>
                          )}
                        </View>
                      ))}
                    </View>
                  </View>
                )}

                {/* Route Steps - Collapsible with Enhanced UI */}
                <View className="bg-white rounded-2xl mb-4 shadow-lg overflow-hidden">
                  <TouchableOpacity
                    onPress={() => toggleSection('steps')}
                    className="flex-row items-center justify-between p-4 bg-gradient-to-r from-indigo-50 to-blue-50"
                    style={{backgroundColor: '#EEF2FF'}}
                  >
                    <View className="flex-row items-center">
                      <View className="bg-indigo-500 p-2.5 rounded-full mr-3">
                        <Ionicons name="footsteps" size={20} color="#ffffff" />
                      </View>
                      <Text className="text-lg font-bold text-gray-800">Route Steps</Text>
                    </View>
                    <Ionicons
                      name={expandedSections.steps ? "chevron-up" : "chevron-down"}
                      size={24}
                      color="#6366F1"
                    />
                  </TouchableOpacity>

                  {expandedSections.steps && (
                    <View className="p-4"  style={{backgroundColor: '#FAFAFA'}}>
                  {(() => {
                    const steps = selectedRouteForModal.steps || selectedRouteForModal.route_data?.steps || [];
                    
                    if (steps.length > 0) {
                      return (
                        <View className="space-y-3">
                          {steps.map((step, index) => (
                            <View
                              key={index}
                              className="bg-white rounded-xl p-4 mb-3 shadow-sm"
                              style={{borderLeftWidth: 3, borderLeftColor: index === 0 ? '#10B981' : index === steps.length - 1 ? '#EF4444' : '#3B82F6'}}
                            >
                              <View className="flex-row items-start">
                                <View className="bg-gray-100 p-3 rounded-full mr-3">
                                  <Text className="text-2xl">{(step as any).icon || '📍'}</Text>
                                </View>
                                <View className="flex-1">
                                  <View className="flex-row items-center mb-1">
                                    <View className={`px-2 py-0.5 rounded ${index === 0 ? 'bg-green-100' : index === steps.length - 1 ? 'bg-red-100' : 'bg-blue-100'}`}>
                                      <Text className={`text-xs font-semibold ${index === 0 ? 'text-green-700' : index === steps.length - 1 ? 'text-red-700' : 'text-blue-700'}`}>
                                        {index === 0 ? 'START' : index === steps.length - 1 ? 'FINISH' : `STEP ${index + 1}`}
                                      </Text>
                                    </View>
                                  </View>
                                  <Text className="text-base font-medium text-gray-800 mb-2">
                                    {(step as any).description || (step as any).instruction || (step as any).html_instructions}
                                  </Text>
                                  
                                  {/* Transit Details */}
                                  {(step as any).transit_details && (
                                    <View className="bg-indigo-50 rounded-lg p-2 mb-2">
                                      <Text className="text-xs font-semibold text-indigo-800 mb-1">🚌 Transit Info</Text>
                                      <View className="space-y-1">
                                        {(step as any).transit_details.departure_stop && (
                                          <Text className="text-xs text-indigo-700">
                                            From: {(step as any).transit_details.departure_stop}
                                          </Text>
                                        )}
                                        {(step as any).transit_details.arrival_stop && (
                                          <Text className="text-xs text-indigo-700">
                                            To: {(step as any).transit_details.arrival_stop}
                                          </Text>
                                        )}
                                        {(step as any).transit_details.line_name && (
                                          <Text className="text-xs text-indigo-700">
                                            Line: {(step as any).transit_details.line_name}
                                          </Text>
                                        )}
                                        {(step as any).transit_details.vehicle_type && (
                                          <Text className="text-xs text-indigo-700">
                                            Vehicle: {(step as any).transit_details.vehicle_type}
                                          </Text>
                                        )}
                                        {(step as any).transit_details.num_stops && (
                                          <Text className="text-xs text-indigo-700">
                                            Stops: {(step as any).transit_details.num_stops}
                                          </Text>
                                        )}
                                      </View>
                                    </View>
                                  )}

                                  {/* Fare Details */}
                                  {(step as any).fare_details && (step as any).fare_details.base_fare > 0 && (
                                    <View className="bg-yellow-50 rounded-lg p-2 mb-2">
                                      <Text className="text-xs font-semibold text-yellow-800 mb-1">💰 Fare Details</Text>
                                      <View className="space-y-1">
                                        <Text className="text-xs text-yellow-700">
                                          Base Fare: {(step as any).fare_details.base_fare} {(selectedRouteForModal as any).route_data?.cost_currency || 'LKR'}
                                        </Text>
                                        {(step as any).fare_details.distance_km && (
                                          <Text className="text-xs text-yellow-700">
                                            Distance: {(step as any).fare_details.distance_km} km
                                          </Text>
                                        )}
                                        {(step as any).fare_details.fare_calculation && (
                                          <Text className="text-xs text-yellow-700">
                                            Method: {(step as any).fare_details.fare_calculation.replace(/_/g, ' ')}
                                          </Text>
                                        )}
                                      </View>
                                    </View>
                                  )}
                                  <View className="flex-row items-center flex-wrap">
                                    {(step as any).duration && (step as any).duration !== 'N/A' && (
                                      <View className="bg-blue-50 px-3 py-1 rounded-full mr-2 mb-1 flex-row items-center">
                                        <Ionicons name="time-outline" size={14} color="#3B82F6" />
                                        <Text className="text-xs text-blue-700 font-medium ml-1">
                                          {(step as any).duration}
                                        </Text>
                                      </View>
                                    )}
                                    {(step as any).distance && (step as any).distance !== 'N/A' && (
                                      <View className="bg-green-50 px-3 py-1 rounded-full mr-2 mb-1 flex-row items-center">
                                        <Ionicons name="map-outline" size={14} color="#10B981" />
                                        <Text className="text-xs text-green-700 font-medium ml-1">
                                          {convertToKilometers((step as any).distance)}
                                        </Text>
                                      </View>
                                    )}
                                    {(step as any).fare && (step as any).fare !== 'N/A' && (
                                      <View className="bg-yellow-50 px-3 py-1 rounded-full mb-1 flex-row items-center">
                                        <Ionicons name="cash-outline" size={14} color="#F59E0B" />
                                        <Text className="text-xs text-yellow-700 font-medium ml-1">
                                          {(step as any).fare}
                                        </Text>
                                      </View>
                                    )}
                                  </View>
                                </View>
                              </View>
                            </View>
                          ))}
                        </View>
                      );
                    }
                    
                    // Generate steps based on route type if no database steps
                    let calculatedSteps: any[] = [];
                    const origin = selectedRouteForModal.route_data?.origin || selectedRouteForModal.source || 'Start Location';
                    const destination = selectedRouteForModal.route_data?.destination || selectedRouteForModal.destination || 'End Location';
                    const fare = selectedRouteForModal.route_data?.estimated_cost ? 
                                `${selectedRouteForModal.route_data.cost_currency || 'Rs.'} ${selectedRouteForModal.route_data.estimated_cost}` : 
                                'Fare varies';
                    
                    if (selectedRouteForModal.route_id?.includes('uber') || selectedRouteForModal.route_data?.route_id?.includes('uber')) {
                      calculatedSteps = [
                        { icon: '📍', description: `Meet driver at pickup location in ${origin}`, duration: '5 min', distance: '0.2 km' },
                        { icon: '🚗', description: `Travel via Uber/PickMe to ${destination}`, duration: '3-4 hours', fare: fare, distance: '116 km' },
                        { icon: '🏁', description: `Arrive at ${destination}`, duration: '0 min', distance: '0.1 km' }
                      ];
                    } else if (selectedRouteForModal.route_id?.includes('bus')) {
                      calculatedSteps = [
                        { icon: '🚶', description: `Walk to bus station in ${origin}`, duration: '10-15 min', distance: '0.8 km' },
                        { icon: '🚌', description: `Take bus from ${origin} to ${destination}`, duration: '5-6 hours', fare: fare, distance: '115 km' },
                        { icon: '🚶', description: `Walk to final destination in ${destination}`, duration: '5-10 min', distance: '0.5 km' }
                      ];
                    } else if (selectedRouteForModal.route_id?.includes('train')) {
                      calculatedSteps = [
                        { icon: '🚶', description: `Walk to railway station in ${origin}`, duration: '10-20 min', distance: '1.2 km' },
                        { icon: '🚂', description: `Take train from ${origin} to ${destination}`, duration: '7-8 hours', fare: fare, distance: '120 km' },
                        { icon: '🚶', description: `Walk to final destination in ${destination}`, duration: '10-15 min', distance: '0.7 km' }
                      ];
                    }
                    
                    if (calculatedSteps.length > 0) {
                      return (
                        <View className="space-y-3">
                          {calculatedSteps.map((step, index) => (
                            <View
                              key={index}
                              className="bg-white rounded-xl p-4 mb-3 shadow-sm"
                              style={{borderLeftWidth: 3, borderLeftColor: index === 0 ? '#10B981' : index === calculatedSteps.length - 1 ? '#EF4444' : '#3B82F6'}}
                            >
                              <View className="flex-row items-start">
                                <View className="bg-gray-100 p-3 rounded-full mr-3">
                                  <Text className="text-2xl">{step.icon}</Text>
                                </View>
                                <View className="flex-1">
                                  <View className="flex-row items-center mb-1">
                                    <View className={`px-2 py-0.5 rounded ${index === 0 ? 'bg-green-100' : index === calculatedSteps.length - 1 ? 'bg-red-100' : 'bg-blue-100'}`}>
                                      <Text className={`text-xs font-semibold ${index === 0 ? 'text-green-700' : index === calculatedSteps.length - 1 ? 'text-red-700' : 'text-blue-700'}`}>
                                        {index === 0 ? 'START' : index === calculatedSteps.length - 1 ? 'FINISH' : `STEP ${index + 1}`}
                                      </Text>
                                    </View>
                                  </View>
                                  <Text className="text-base font-medium text-gray-800 mb-2">
                                    {step.description}
                                  </Text>
                                  <View className="flex-row items-center flex-wrap">
                                    {step.duration && (
                                      <View className="bg-blue-50 px-3 py-1 rounded-full mr-2 mb-1 flex-row items-center">
                                        <Ionicons name="time-outline" size={14} color="#3B82F6" />
                                        <Text className="text-xs text-blue-700 font-medium ml-1">
                                          {step.duration}
                                        </Text>
                                      </View>
                                    )}
                                    {step.distance && (
                                      <View className="bg-green-50 px-3 py-1 rounded-full mr-2 mb-1 flex-row items-center">
                                        <Ionicons name="map-outline" size={14} color="#10B981" />
                                        <Text className="text-xs text-green-700 font-medium ml-1">
                                          {convertToKilometers(step.distance)}
                                        </Text>
                                      </View>
                                    )}
                                    {step.fare && (
                                      <View className="bg-yellow-50 px-3 py-1 rounded-full mb-1 flex-row items-center">
                                        <Ionicons name="cash-outline" size={14} color="#F59E0B" />
                                        <Text className="text-xs text-yellow-700 font-medium ml-1">
                                          {step.fare}
                                        </Text>
                                      </View>
                                    )}
                                  </View>
                                </View>
                              </View>
                            </View>
                          ))}
                        </View>
                      );
                    }

                    return (
                      <View className="bg-gray-100 rounded-lg p-4 text-center">
                        <Text className="text-gray-500 italic text-center">Step-by-step directions not available</Text>
                      </View>
                    );
                  })()}
                    </View>
                  )}
                </View>

                {/* AI Recommendation - Enhanced Card */}
                <LinearGradient
                  colors={['#DBEAFE', '#BFDBFE']}
                  start={{x: 0, y: 0}}
                  end={{x: 1, y: 1}}
                  style={{borderRadius: 16, padding: 16, marginBottom: 16}}
                >
                  <View className="flex-row items-center mb-3">
                    <View className="bg-blue-600 p-2.5 rounded-full mr-3">
                      <Ionicons name="sparkles" size={20} color="#ffffff" />
                    </View>
                    <Text className="text-lg font-bold text-blue-900">AI Recommendation</Text>
                  </View>
                  <Text className="text-base text-blue-800 leading-6">
                    {selectedRouteForModal.aiRecommendation || 
                     selectedRouteForModal.route_data?.aiRecommendation ||
                     selectedRouteForModal.agent_analysis?.recommendations?.[0] ||
                     selectedRouteForModal.route_data?.agent_analysis?.recommendations?.[0] ||
                     (() => {
                       // Generate recommendation based on actual database scores
                       const score = selectedRouteForModal.route_data?.recommendation_score;
                       const scoreBreakdown = selectedRouteForModal.route_data?.score_breakdown;
                       
                       if (score && scoreBreakdown) {
                         const percentage = Math.round(score * 100);
                         const strengths = [];
                         
                         if (scoreBreakdown.convenience && scoreBreakdown.convenience >= 0.8) strengths.push('convenient');
                         if (scoreBreakdown.reliability && scoreBreakdown.reliability >= 0.6) strengths.push('reliable');
                         if (scoreBreakdown.comfort && scoreBreakdown.comfort >= 0.5) strengths.push('comfortable');
                         
                         if (strengths.length > 0) {
                           return `This route scores ${percentage}% overall and is particularly ${strengths.join(', ')}.`;
                         } else {
                           return `This route has a ${percentage}% recommendation score based on AI analysis.`;
                         }
                       }
                       
                       return 'This route has been optimized by our AI agents for the best balance of time, cost, and comfort.';
                     })()}
                  </Text>
                </LinearGradient>

                {/* Alternative Routes - Collapsible */}
                {(() => {
                  const allRoutes = (selectedRouteForModal as any).all_routes || [];
                  const alternativeRoutes = allRoutes.filter((route: any) => route.route_id !== selectedRouteForModal.route_data?.route_id);

                  if (alternativeRoutes.length > 0) {
                    return (
                      <View className="bg-white rounded-2xl mb-4 shadow-lg overflow-hidden">
                        <TouchableOpacity
                          onPress={() => toggleSection('alternatives')}
                          className="flex-row items-center justify-between p-4"
                          style={{backgroundColor: '#FEF3C7'}}
                        >
                          <View className="flex-row items-center">
                            <View className="bg-amber-600 p-2.5 rounded-full mr-3">
                              <Ionicons name="git-branch" size={20} color="#ffffff" />
                            </View>
                            <Text className="text-lg font-bold text-gray-800">Alternative Routes ({alternativeRoutes.length})</Text>
                          </View>
                          <Ionicons
                            name={expandedSections.alternatives ? "chevron-up" : "chevron-down"}
                            size={24}
                            color="#D97706"
                          />
                        </TouchableOpacity>

                        {expandedSections.alternatives && (
                          <View className="p-4" style={{backgroundColor: '#FFFBEB'}}>
                        {alternativeRoutes.map((route: any, index: number) => (
                          <View key={index} className="bg-white rounded-xl p-4 mb-3 shadow-sm" style={{borderLeftWidth: 3, borderLeftColor: '#F59E0B'}}>
                            <View className="flex-row items-center justify-between mb-3">
                              <View className="flex-row items-center">
                                <View className="bg-amber-100 px-3 py-1 rounded-full mr-2">
                                  <Text className="text-xs font-bold text-amber-800">#{index + 1}</Text>
                                </View>
                                <View className="bg-blue-100 px-3 py-1 rounded-full">
                                  <Text className="text-xs font-semibold text-blue-700">{route.route_source || 'Alternative'}</Text>
                                </View>
                              </View>
                              <View className="bg-green-100 px-2.5 py-1 rounded-full">
                                <Text className="text-xs font-bold text-green-700">
                                  {Math.round((route.recommendation_score || 0) * 100)}%
                                </Text>
                              </View>
                            </View>
                            <View className="flex-row items-center flex-wrap">
                              <View className="bg-blue-50 px-3 py-1.5 rounded-full mr-2 mb-2 flex-row items-center">
                                <Ionicons name="time-outline" size={14} color="#3B82F6" />
                                <Text className="text-xs text-blue-700 font-medium ml-1">{route.duration_text}</Text>
                              </View>
                              {route.distance_text && (
                                <View className="bg-green-50 px-3 py-1.5 rounded-full mr-2 mb-2 flex-row items-center">
                                  <Ionicons name="map-outline" size={14} color="#10B981" />
                                  <Text className="text-xs text-green-700 font-medium ml-1">{convertToKilometers(route.distance_text)}</Text>
                                </View>
                              )}
                              <View className="bg-yellow-50 px-3 py-1.5 rounded-full mb-2 flex-row items-center">
                                <Ionicons name="cash-outline" size={14} color="#F59E0B" />
                                <Text className="text-xs text-yellow-700 font-medium ml-1">{route.cost_currency} {route.estimated_cost}</Text>
                              </View>
                            </View>
                          </View>
                        ))}
                          </View>
                        )}
                      </View>
                    );
                  }
                  return null;
                })()}

                {/* AI Analysis & Scoring - Collapsible with Enhanced Progress Bars */}
                {(() => {
                  const scoreBreakdown = selectedRouteForModal.route_data?.score_breakdown;
                  const recommendationScore = selectedRouteForModal.route_data?.recommendation_score;

                  if (scoreBreakdown || recommendationScore) {
                    return (
                      <View className="bg-white rounded-2xl mb-4 shadow-lg overflow-hidden">
                        <TouchableOpacity
                          onPress={() => toggleSection('aiAnalysis')}
                          className="flex-row items-center justify-between p-4"
                          style={{backgroundColor: '#F3E8FF'}}
                        >
                          <View className="flex-row items-center">
                            <View className="bg-purple-600 p-2.5 rounded-full mr-3">
                              <Ionicons name="analytics" size={20} color="#ffffff" />
                            </View>
                            <Text className="text-lg font-bold text-gray-800">AI Analysis & Scoring</Text>
                          </View>
                          <Ionicons
                            name={expandedSections.aiAnalysis ? "chevron-up" : "chevron-down"}
                            size={24}
                            color="#9333EA"
                          />
                        </TouchableOpacity>

                        {expandedSections.aiAnalysis && (
                          <View className="p-4" style={{backgroundColor: '#FAF5FF'}}>
                        
                        {recommendationScore && (
                          <View className="mb-4">
                            <LinearGradient
                              colors={['#EDE9FE', '#DDD6FE']}
                              start={{x: 0, y: 0}}
                              end={{x: 1, y: 0}}
                              style={{borderRadius: 12, padding: 16}}
                            >
                              <View className="flex-row items-center justify-between mb-3">
                                <View className="flex-row items-center">
                                  <View className="bg-purple-600 p-2 rounded-full mr-2">
                                    <Ionicons name="trophy" size={16} color="#ffffff" />
                                  </View>
                                  <Text className="text-sm font-bold text-purple-900">Overall Score</Text>
                                </View>
                                <Text className="text-2xl font-bold text-purple-700">{Math.round(recommendationScore * 100)}%</Text>
                              </View>
                              <View className="bg-purple-200 rounded-full h-3 overflow-hidden">
                                <LinearGradient
                                  colors={['#A855F7', '#9333EA']}
                                  start={{x: 0, y: 0}}
                                  end={{x: 1, y: 0}}
                                  style={{height: '100%', width: `${recommendationScore * 100}%`, borderRadius: 9999}}
                                />
                              </View>
                            </LinearGradient>
                          </View>
                        )}
                        
                        {scoreBreakdown && (
                          <View className="space-y-3">
                            <Text className="text-sm font-bold text-purple-900 mb-2">Score Breakdown</Text>
                            {Object.entries(scoreBreakdown).map(([key, value]: [string, any]) => {
                              const percentage = Math.round((value || 0) * 100);
                              const label = key.charAt(0).toUpperCase() + key.slice(1);
                              const isHigh = percentage >= 70;
                              const isMedium = percentage >= 40 && percentage < 70;
                              const iconName =
                                key === 'time' ? 'speedometer' :
                                key === 'cost' ? 'wallet' :
                                key === 'comfort' ? 'heart' :
                                key === 'reliability' ? 'shield-checkmark' :
                                key === 'convenience' ? 'star' : 'checkmark-circle';

                              return (
                                <View key={key} className="bg-white rounded-xl p-3 shadow-sm">
                                  <View className="flex-row items-center justify-between mb-2">
                                    <View className="flex-row items-center">
                                      <Ionicons
                                        name={iconName as any}
                                        size={16}
                                        color={isHigh ? '#10B981' : isMedium ? '#F59E0B' : '#EF4444'}
                                      />
                                      <Text className="text-sm font-medium text-gray-800 ml-2">{label}</Text>
                                    </View>
                                    <Text className={`text-sm font-bold ${isHigh ? 'text-green-600' : isMedium ? 'text-yellow-600' : 'text-red-600'}`}>
                                      {percentage}%
                                    </Text>
                                  </View>
                                  <View className="bg-gray-200 rounded-full h-2 overflow-hidden">
                                    <View
                                      className={`h-2 rounded-full ${
                                        isHigh ? 'bg-gradient-to-r from-green-400 to-green-600' :
                                        isMedium ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' :
                                        'bg-gradient-to-r from-red-400 to-red-600'
                                      }`}
                                      style={{
                                        width: `${percentage}%`,
                                        backgroundColor: isHigh ? '#10B981' : isMedium ? '#F59E0B' : '#EF4444'
                                      }}
                                    />
                                  </View>
                                </View>
                              );
                            })}
                          </View>
                        )}
                          </View>
                        )}
                      </View>
                    );
                  }
                  return null;
                })()}

                {/* AI Disruption Analysis - Collapsible */}
                {(() => {
                  const aiAnalysis = (selectedRouteForModal as any).ai_disruption_analysis;

                  if (aiAnalysis) {
                    return (
                      <View className="bg-white rounded-2xl mb-4 shadow-lg overflow-hidden">
                        <TouchableOpacity
                          onPress={() => toggleSection('disruption')}
                          className="flex-row items-center justify-between p-4"
                          style={{backgroundColor: '#FEE2E2'}}
                        >
                          <View className="flex-row items-center">
                            <View className="bg-red-600 p-2.5 rounded-full mr-3">
                              <Ionicons name="warning" size={20} color="#ffffff" />
                            </View>
                            <Text className="text-lg font-bold text-gray-800">AI Disruption Analysis</Text>
                          </View>
                          <Ionicons
                            name={expandedSections.disruption ? "chevron-up" : "chevron-down"}
                            size={24}
                            color="#DC2626"
                          />
                        </TouchableOpacity>

                        {expandedSections.disruption && (
                          <View className="p-4" style={{backgroundColor: '#FEF2F2'}}>
                        
                        <View className="bg-blue-50 rounded-lg p-3 mb-3">
                          <View className="flex-row items-center justify-between mb-2">
                            <Text className="text-sm font-medium text-blue-800">Analysis Confidence</Text>
                            <View className="bg-blue-200 px-2 py-1 rounded">
                              <Text className="text-sm font-semibold text-blue-800">{aiAnalysis.confidence_score}%</Text>
                            </View>
                          </View>
                          <Text className="text-xs text-blue-600 mb-1">Model: {aiAnalysis.model_used}</Text>
                          <Text className="text-xs text-blue-600">
                            Analysis Time: {new Date(aiAnalysis.analysis_timestamp).toLocaleTimeString()}
                          </Text>
                        </View>
                        
                        {aiAnalysis.summary && (
                          <View className="bg-gray-50 rounded-lg p-3 mb-3">
                            <Text className="text-sm font-medium text-gray-800 mb-1">📋 Summary</Text>
                            <Text className="text-sm text-gray-700">{aiAnalysis.summary}</Text>
                          </View>
                        )}
                        
                        {aiAnalysis.reasoning && (
                          <View className="bg-gray-50 rounded-lg p-3 mb-3">
                            <Text className="text-sm font-medium text-gray-800 mb-1">💭 AI Reasoning</Text>
                            <Text className="text-sm text-gray-700">{aiAnalysis.reasoning}</Text>
                          </View>
                        )}
                        
                        {aiAnalysis.disruption_impact && (
                          <View className="bg-gray-50 rounded-lg p-3">
                            <Text className="text-sm font-medium text-gray-800 mb-2">🚨 Disruption Impact</Text>
                            <View className="space-y-1">
                              <Text className="text-xs text-red-600">High Impact: {aiAnalysis.disruption_impact.high_impact_routes?.length || 0} routes</Text>
                              <Text className="text-xs text-yellow-600">Medium Impact: {aiAnalysis.disruption_impact.medium_impact_routes?.length || 0} routes</Text>
                              <Text className="text-xs text-green-600">Unaffected: {aiAnalysis.disruption_impact.unaffected_routes?.length || 0} routes</Text>
                            </View>
                          </View>
                        )}
                        </View>
                      )}
                      </View>
                    );
                  }
                  return null;
                })()}

                {/* Route Technical Details - Collapsible */}
                <View className="bg-white rounded-2xl mb-4 shadow-lg overflow-hidden">
                  <TouchableOpacity
                    onPress={() => toggleSection('technical')}
                    className="flex-row items-center justify-between p-4"
                    style={{backgroundColor: '#E0E7FF'}}
                  >
                    <View className="flex-row items-center">
                      <View className="bg-indigo-600 p-2.5 rounded-full mr-3">
                        <Ionicons name="settings" size={20} color="#ffffff" />
                      </View>
                      <Text className="text-lg font-bold text-gray-800">Technical Details</Text>
                    </View>
                    <Ionicons
                      name={expandedSections.technical ? "chevron-up" : "chevron-down"}
                      size={24}
                      color="#4F46E5"
                    />
                  </TouchableOpacity>

                  {expandedSections.technical && (
                    <View className="p-4" style={{backgroundColor: '#EEF2FF'}}>
                      <View className="space-y-2">
                        <View className="flex-row items-center justify-between">
                          <Text className="text-sm text-gray-600">Route Source</Text>
                          <View className="bg-blue-100 px-2 py-1 rounded">
                            <Text className="text-xs text-blue-700">
                              {selectedRouteForModal.route_data?.route_source || 'Standard'}
                            </Text>
                          </View>
                        </View>
                        
                        <View className="flex-row items-center justify-between">
                          <Text className="text-sm text-gray-600">Route ID</Text>
                          <Text className="text-sm text-gray-800 font-mono">
                            {selectedRouteForModal.route_data?.route_id || selectedRouteForModal.id}
                          </Text>
                        </View>
                        
                        {/* Processing Metadata */}
                        <View className="flex-row items-center justify-between">
                          <Text className="text-sm text-gray-600">Processing Time</Text>
                          <Text className="text-sm text-gray-800">
                            {(selectedRouteForModal as any).processing_time ? 
                              `${Math.round((selectedRouteForModal as any).processing_time * 10) / 10}s` : 
                              'Not available'}
                          </Text>
                        </View>
                        
                        {/* Agents Used */}
                        <View className="flex-row items-center justify-between">
                          <Text className="text-sm text-gray-600">AI Agents Used</Text>
                          <Text className="text-sm text-gray-800">
                            {(selectedRouteForModal as any).agents_used?.length || 
                             selectedRouteForModal.agents_count || 0} agents
                          </Text>
                        </View>

                        {/* Trace ID */}
                        {(selectedRouteForModal as any).trace_id && (
                          <View className="flex-row items-center justify-between">
                            <Text className="text-sm text-gray-600">Trace ID</Text>
                            <Text className="text-sm text-gray-800 font-mono">
                              {(selectedRouteForModal as any).trace_id}
                            </Text>
                          </View>
                        )}

                        {/* Transfers Count */}
                        {selectedRouteForModal.route_data?.transfers !== undefined && (
                          <View className="flex-row items-center justify-between">
                            <Text className="text-sm text-gray-600">Transfers</Text>
                            <Text className="text-sm text-gray-800">
                              {selectedRouteForModal.route_data.transfers} transfer{selectedRouteForModal.route_data.transfers !== 1 ? 's' : ''}
                            </Text>
                          </View>
                        )}

                        {/* Total Routes Found */}
                        {(selectedRouteForModal as any).total_routes_found && (
                          <View className="flex-row items-center justify-between">
                            <Text className="text-sm text-gray-600">Total Routes Found</Text>
                            <Text className="text-sm text-gray-800">
                              {(selectedRouteForModal as any).total_routes_found} routes
                            </Text>
                          </View>
                        )}
                        
                        {selectedRouteForModal.request_timestamp && (
                          <View className="flex-row items-center justify-between">
                            <Text className="text-sm text-gray-600">Request Time</Text>
                            <Text className="text-sm text-gray-800">
                              {new Date(selectedRouteForModal.request_timestamp).toLocaleString()}
                            </Text>
                          </View>
                        )}

                        {/* Agents Used List */}
                        {(selectedRouteForModal as any).agents_used && (selectedRouteForModal as any).agents_used.length > 0 && (
                          <View className="mt-3">
                            <Text className="text-sm font-medium text-gray-800 mb-2">AI Agents Pipeline</Text>
                            <View className="flex-row flex-wrap">
                              {(selectedRouteForModal as any).agents_used.map((agent: string, index: number) => (
                                <View key={index} className="bg-purple-100 px-2 py-1 rounded-full mr-2 mb-1">
                                  <Text className="text-xs text-purple-700">
                                    {agent.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                                  </Text>
                                </View>
                              ))}
                            </View>
                          </View>
                        )}
                      </View>
                    </View>
                  )}
                </View>

                {/* Disruptions - Only show if there are active disruptions */}
                {(selectedRouteForModal.disruptions || selectedRouteForModal.route_data?.disruptions || []).length > 0 && (
                  <View className="bg-orange-50 rounded-lg p-4 mb-4">
                    <Text className="text-lg font-semibold text-orange-800 mb-3">⚠️ Active Disruptions</Text>
                    <View className="space-y-2">
                      {(selectedRouteForModal.disruptions || selectedRouteForModal.route_data?.disruptions || []).map((disruption, index) => (
                        <Text key={index} className="text-orange-700">{disruption}</Text>
                      ))}
                    </View>
                  </View>
                )}

                {/* Destination Insights - Collapsible */}
                {selectedRouteForModal.destination_summary && (
                  <View className="bg-white rounded-2xl mb-4 shadow-lg overflow-hidden">
                    <TouchableOpacity
                      onPress={() => toggleSection('destination')}
                      className="flex-row items-center justify-between p-4"
                      style={{backgroundColor: '#D1FAE5'}}
                    >
                      <View className="flex-row items-center">
                        <View className="bg-green-600 p-2.5 rounded-full mr-3">
                          <Ionicons name="location" size={20} color="#ffffff" />
                        </View>
                        <Text className="text-lg font-bold text-gray-800">Destination Insights</Text>
                      </View>
                      <Ionicons
                        name={expandedSections.destination ? "chevron-up" : "chevron-down"}
                        size={24}
                        color="#059669"
                      />
                    </TouchableOpacity>

                    {expandedSections.destination && (
                      <View className="p-4" style={{backgroundColor: '#ECFDF5'}}>
                        <LinearGradient
                          colors={['#D1FAE5', '#A7F3D0']}
                          start={{x: 0, y: 0}}
                          end={{x: 1, y: 1}}
                          style={{borderRadius: 12, padding: 16}}
                        >
                          <View className="flex-row items-center mb-3">
                            <View className="bg-green-600 p-2 rounded-full mr-2">
                              <Ionicons name="map" size={16} color="#ffffff" />
                            </View>
                            <Text className="text-sm font-bold text-green-900">Local Information</Text>
                          </View>
                          <Text className="text-sm text-green-800 leading-6">
                            {selectedRouteForModal.destination_summary}
                          </Text>
                        </LinearGradient>
                      </View>
                    )}
                  </View>
                )}



                {/* Actions - Enhanced Close Button */}
                <View className="flex-row justify-center mt-6 mb-4">
                  <TouchableOpacity
                    onPress={() => setShowRouteModal(false)}
                  >
                    <LinearGradient
                      colors={['#3B82F6', '#2563EB']}
                      start={{x: 0, y: 0}}
                      end={{x: 1, y: 0}}
                      style={{borderRadius: 12, paddingVertical: 16, paddingHorizontal: 48, flexDirection: 'row', alignItems: 'center', justifyContent: 'center'}}
                    >
                      <Ionicons name="checkmark-circle" size={20} color="#ffffff" style={{marginRight: 8}} />
                      <Text className="text-white text-center font-bold text-base">Done</Text>
                    </LinearGradient>
                  </TouchableOpacity>
                </View>
              </View>
            )}
          </ScrollView>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}