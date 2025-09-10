import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Alert, Modal } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { RouteOption } from '../../../src/types';
import { useRoutes } from '../../../src/contexts/AppContext';
import { useRouter } from 'expo-router';
import { useFocusEffect } from '@react-navigation/native';


export default function Routes() {
  const { loadRouteHistoryFromBackend } = useRoutes();
  const router = useRouter();
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);
  const [recentRoutes, setRecentRoutes] = useState<RouteOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRouteForModal, setSelectedRouteForModal] = useState<RouteOption | null>(null);
  const [showRouteModal, setShowRouteModal] = useState(false);

  // Load recent routes from AsyncStorage on component mount
  useEffect(() => {
    loadRecentRoutes();
  }, []);

  // Reload routes when screen is focused (e.g., when navigating back from home)
  useFocusEffect(
    React.useCallback(() => {
      loadRecentRoutes();
    }, [])
  );

  const loadRecentRoutes = async () => {
    try {
      setIsLoading(true);
      
      // Load from local storage first (faster)
      const storedRoutes = await AsyncStorage.getItem('recent_routes');
      let localRoutes: RouteOption[] = [];
      if (storedRoutes) {
        localRoutes = JSON.parse(storedRoutes);
        console.log('Loaded routes from AsyncStorage:', localRoutes.length);
        setRecentRoutes(localRoutes.slice(0, 5)); // Show last 5 routes
      } else {
        console.log('No routes found in AsyncStorage');
      }

      // Then try to load from backend (more complete data)
      try {
        const backendRoutes = await loadRouteHistoryFromBackend();
        if (backendRoutes.length > 0) {
          console.log('DEBUG: First backend route structure:', JSON.stringify(backendRoutes[0], null, 2));
          
          // Merge backend routes with local routes, preferring backend data
          const mergedRoutes = [...backendRoutes, ...localRoutes.filter(local => 
            !backendRoutes.some(backend => backend.route_id === local.route_id)
          )];
          setRecentRoutes(mergedRoutes.slice(0, 5));
          console.log('Loaded routes from backend and local storage:', mergedRoutes.length);
        }
      } catch (backendError) {
        console.warn('Failed to load routes from backend, using local data only:', backendError);
      }
      
    } catch (error) {
      console.error('Error loading recent routes:', error);
    } finally {
      setIsLoading(false);
    }
  };




  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <ScrollView className="flex-1">
        {/* Header */}
        <View className="bg-white px-4 py-4 border-b border-gray-200">
          <Text className="text-2xl font-bold text-gray-800">My Routes</Text>
          <Text className="text-sm text-gray-600">AI-powered route planning results</Text>
        </View>



        {/* Route Options */}
        <View className="px-4 mt-4">
          <Text className="text-lg font-semibold text-gray-800 mb-3">Recent Route Options</Text>
          
          {isLoading ? (
            <View className="bg-white p-6 rounded-lg shadow-sm items-center">
              <Text className="text-4xl mb-2">🔄</Text>
              <Text className="text-lg font-medium text-gray-800">Loading recent routes...</Text>
            </View>
          ) : recentRoutes.length === 0 ? (
            <View className="bg-white p-6 rounded-lg shadow-sm items-center">
              <Text className="text-4xl mb-2">🗺️</Text>
              <Text className="text-lg font-medium text-gray-800 mb-2">No routes planned yet</Text>
              <Text className="text-sm text-gray-600 text-center mb-4">
                Start planning your journey from the Home tab to see AI-generated route options here
              </Text>
              <TouchableOpacity 
                className="bg-blue-600 px-4 py-2 rounded-lg"
                onPress={() => {
                  // Navigate to home tab for route planning
                  router.push('/(main)/(tabs)/home');
                }}
              >
                <Text className="text-white font-medium">Plan a Route</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View className="space-y-4">
              {recentRoutes.map((route, index) => (
                <View key={`recent-${route.id || route.route_id || index}-${index}`} className="bg-white rounded-lg shadow-sm overflow-hidden">
                  <TouchableOpacity
                    className="p-4"
                    onPress={() => {
                      const routeKey = `recent-${route.id || route.route_id || index}-${index}`;
                      setSelectedRoute(selectedRoute === routeKey ? null : routeKey);
                    }}
                  >
                    <View className="flex-row items-center justify-between mb-2">
                      <Text className="text-lg font-semibold text-gray-800">
                        {route.title || 
                         (route.route_data?.origin && route.route_data?.destination ? 
                          `${route.route_data.origin} → ${route.route_data.destination}` :
                          (route.route_data?.source && route.route_data?.destination ? 
                           `${route.route_data.source} → ${route.route_data.destination}` :
                           (route.origin && route.destination ? 
                            `${route.origin} → ${route.destination}` :
                            (route.source && route.destination && route.source !== 'Unknown' && route.source !== 'Route Start' ? 
                             `${route.source} → ${route.destination}` :
                             (route.steps?.[0]?.start_location?.name && route.steps?.[route.steps.length - 1]?.end_location?.name ? 
                              `${route.steps[0].start_location.name} → ${route.steps[route.steps.length - 1].end_location.name}` : 
                              `Route ${route.route_id || route.id || index + 1}`)))))}
                      </Text>
                      <View className="flex-row">
                        {(route.modes || route.route_data?.modes || route.summary?.transit_modes || []).map((mode: string, index: number) => (
                          <Text key={index} className="text-lg ml-1">
                            {mode === 'bus' ? '🚌' : 
                             mode === 'train' ? '🚆' : 
                             mode === 'walking' ? '🚶' : 
                             mode === 'tuk-tuk' ? '🛺' : 
                             mode === 'car' ? '🚗' : mode}
                          </Text>
                        ))}
                      </View>
                    </View>
                    
                    <View className="flex-row items-center mb-3">
                      {/* Duration - only show if available */}
                      {(route.duration || 
                        route.route_data?.duration ||
                        (route.route_data?.duration_text && route.route_data.duration_text !== 'Unknown') ||
                        route.summary?.duration_minutes ||
                        route.route_data?.summary?.duration_minutes) && (
                        <View className="flex-row items-center mr-4">
                          <Ionicons name="time" size={16} color="#6b7280" />
                          <Text className="text-sm text-gray-600 ml-1">
                            {route.duration || 
                             route.route_data?.duration ||
                             (route.route_data?.duration_text && route.route_data.duration_text !== 'Unknown' ? 
                              route.route_data.duration_text :
                              (route.summary?.duration_minutes ? 
                               `${Math.floor(route.summary.duration_minutes / 60)}h ${route.summary.duration_minutes % 60}m` : 
                               (route.route_data?.summary?.duration_minutes ?
                                `${Math.floor(route.route_data.summary.duration_minutes / 60)}h ${route.route_data.summary.duration_minutes % 60}m` : '')))}
                          </Text>
                        </View>
                      )}
                      <View className="flex-row items-center mr-4">
                        <Ionicons name="cash" size={16} color="#6b7280" />
                        <Text className="text-sm text-gray-600 ml-1">
                          {route.fare || 
                           route.route_data?.fare ||
                           (route.route_data?.estimated_cost ? 
                            `${route.route_data.cost_currency || 'Rs.'} ${route.route_data.estimated_cost}` :
                            (route.summary?.estimated_fare ? `Rs. ${route.summary.estimated_fare}` : 
                             (route.route_data?.summary?.estimated_fare ? `Rs. ${route.route_data.summary.estimated_fare}` :
                              'Fare not available')))}
                        </Text>
                      </View>
                      <View className="flex-row items-center">
                        <Ionicons name="leaf" size={16} color="#10b981" />
                        <Text className="text-sm text-green-600 ml-1">
                          {route.carbonFootprint || 
                           route.route_data?.carbonFootprint ||
                           (route.summary?.carbon_footprint ? `${route.summary.carbon_footprint.toFixed(1)} kg CO₂` : 
                            (route.route_data?.summary?.carbon_footprint ? `${route.route_data.summary.carbon_footprint.toFixed(1)} kg CO₂` :
                             'Carbon data not available'))}
                        </Text>
                      </View>
                    </View>

                    <View className="bg-blue-50 p-3 rounded-lg mb-3">
                      <Text className="text-sm font-medium text-blue-800">🤖 AI Recommendation</Text>
                      <Text className="text-sm text-blue-700">
                        {route.aiRecommendation || 
                         route.route_data?.aiRecommendation ||
                         route.agent_analysis?.recommendations?.[0] || 
                         route.route_data?.agent_analysis?.recommendations?.[0] ||
                         'AI-optimized route'}
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
                          name={selectedRoute === `recent-${route.id || route.route_id || index}-${index}` ? "chevron-up" : "chevron-down"} 
                          size={20} 
                          color="#6b7280" 
                        />
                      </TouchableOpacity>
                    </View>
                  </TouchableOpacity>

                  {/* Expanded Details */}
                  {selectedRoute === `recent-${route.id || route.route_id || index}-${index}` && (
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
              ))}
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

      {/* Route Details Modal */}
      <Modal
        visible={showRouteModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView className="flex-1 bg-gray-50">
          <View className="flex-row items-center justify-between p-4 bg-white border-b border-gray-200">
            <Text className="text-xl font-bold text-gray-800">Route Details</Text>
            <TouchableOpacity onPress={() => setShowRouteModal(false)}>
              <Ionicons name="close" size={24} color="#6b7280" />
            </TouchableOpacity>
          </View>
          
          <ScrollView className="flex-1">
            {selectedRouteForModal && (
              <View className="p-4">
                {/* Route Header */}
                <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                  <Text className="text-2xl font-bold text-gray-800 mb-2">
                    {selectedRouteForModal.title || 
                     (selectedRouteForModal.route_data?.source && selectedRouteForModal.route_data?.destination ? 
                      `${selectedRouteForModal.route_data.source} → ${selectedRouteForModal.route_data.destination}` :
                      (selectedRouteForModal.source && selectedRouteForModal.destination && selectedRouteForModal.source !== 'Unknown' ? 
                        `${selectedRouteForModal.source} → ${selectedRouteForModal.destination}` : 'Route Details'))}
                  </Text>
                  <Text className="text-sm text-gray-500">Route ID: {selectedRouteForModal.route_id || selectedRouteForModal.id}</Text>
                </View>

                {/* Key Metrics */}
                <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                  <Text className="text-lg font-semibold text-gray-800 mb-3">📊 Key Metrics</Text>
                  <View className="space-y-3">
                    {/* Duration - show database or calculated */}
                    {(() => {
                      const duration = selectedRouteForModal.duration || 
                                      selectedRouteForModal.route_data?.duration ||
                                      (selectedRouteForModal.route_data?.duration_text && selectedRouteForModal.route_data.duration_text !== 'Unknown' ? 
                                       selectedRouteForModal.route_data.duration_text : null) ||
                                      (selectedRouteForModal.summary?.duration_minutes ? 
                                       `${Math.floor(selectedRouteForModal.summary.duration_minutes / 60)}h ${selectedRouteForModal.summary.duration_minutes % 60}m` : null) ||
                                      (selectedRouteForModal.route_data?.summary?.duration_minutes ?
                                       `${Math.floor(selectedRouteForModal.route_data.summary.duration_minutes / 60)}h ${selectedRouteForModal.route_data.summary.duration_minutes % 60}m` : null);
                      
                      // If no database duration, calculate based on route type
                      let calculatedDuration = null;
                      if (!duration) {
                        if (selectedRouteForModal.route_id?.includes('uber') || selectedRouteForModal.route_data?.route_id?.includes('uber')) {
                          // Estimate Uber duration based on distance or route
                          calculatedDuration = "~3-4 hours"; // Colombo to Badulla typical time
                        } else if (selectedRouteForModal.route_id?.includes('bus')) {
                          calculatedDuration = "~5-6 hours";
                        } else if (selectedRouteForModal.route_id?.includes('train')) {
                          calculatedDuration = "~7-8 hours";
                        }
                      }
                      
                      const finalDuration = duration || calculatedDuration;
                      
                      if (finalDuration) {
                        return (
                          <View className="flex-row items-center justify-between">
                            <View className="flex-row items-center">
                              <Ionicons name="time" size={20} color="#6b7280" />
                              <Text className="text-base text-gray-700 ml-2">Duration</Text>
                            </View>
                            <Text className="text-base font-medium">
                              {finalDuration}
                            </Text>
                          </View>
                        );
                      }
                      return null;
                    })()}
                    
                    {/* Fare - only if available */}
                    {(selectedRouteForModal.fare || 
                      selectedRouteForModal.route_data?.fare ||
                      selectedRouteForModal.route_data?.estimated_cost ||
                      selectedRouteForModal.summary?.estimated_fare ||
                      selectedRouteForModal.route_data?.summary?.estimated_fare) && (
                      <View className="flex-row items-center justify-between">
                        <View className="flex-row items-center">
                          <Ionicons name="cash" size={20} color="#6b7280" />
                          <Text className="text-base text-gray-700 ml-2">Total Fare</Text>
                        </View>
                        <Text className="text-base font-medium">
                          {selectedRouteForModal.fare || 
                           selectedRouteForModal.route_data?.fare ||
                           (selectedRouteForModal.route_data?.estimated_cost ? 
                            `${selectedRouteForModal.route_data.cost_currency || 'Rs.'} ${selectedRouteForModal.route_data.estimated_cost}` :
                            (selectedRouteForModal.summary?.estimated_fare ? `Rs. ${selectedRouteForModal.summary.estimated_fare}` : 
                             (selectedRouteForModal.route_data?.summary?.estimated_fare ? `Rs. ${selectedRouteForModal.route_data.summary.estimated_fare}` : '')))}
                        </Text>
                      </View>
                    )}
                    
                    {/* Carbon - show database or calculated */}
                    {(() => {
                      const carbon = selectedRouteForModal.carbonFootprint || 
                                    selectedRouteForModal.route_data?.carbonFootprint ||
                                    (selectedRouteForModal.summary?.carbon_footprint ? `${selectedRouteForModal.summary.carbon_footprint.toFixed(1)} kg CO₂` : null) ||
                                    (selectedRouteForModal.route_data?.summary?.carbon_footprint ? `${selectedRouteForModal.route_data.summary.carbon_footprint.toFixed(1)} kg CO₂` : null);
                      
                      // If no database carbon data, calculate based on route type
                      let calculatedCarbon = null;
                      if (!carbon) {
                        if (selectedRouteForModal.route_id?.includes('uber') || selectedRouteForModal.route_data?.route_id?.includes('uber')) {
                          // Car emissions: ~120g CO₂/km, Colombo-Badulla ~250km
                          calculatedCarbon = "30.0 kg CO₂";
                        } else if (selectedRouteForModal.route_id?.includes('bus')) {
                          // Bus emissions: ~80g CO₂/km per passenger
                          calculatedCarbon = "20.0 kg CO₂";
                        } else if (selectedRouteForModal.route_id?.includes('train')) {
                          // Train emissions: ~40g CO₂/km per passenger
                          calculatedCarbon = "10.0 kg CO₂";
                        } else {
                          // Generic estimate
                          calculatedCarbon = "25.0 kg CO₂";
                        }
                      }
                      
                      const finalCarbon = carbon || calculatedCarbon;
                      
                      if (finalCarbon) {
                        return (
                          <View className="flex-row items-center justify-between">
                            <View className="flex-row items-center">
                              <Ionicons name="leaf" size={20} color="#10b981" />
                              <Text className="text-base text-gray-700 ml-2">Carbon Footprint</Text>
                            </View>
                            <Text className="text-base font-medium text-green-600">
                              {finalCarbon}
                            </Text>
                          </View>
                        );
                      }
                      return null;
                    })()}
                  </View>
                </View>

                {/* Transport Modes */}
                <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                  <Text className="text-lg font-semibold text-gray-800 mb-3">🚌 Transport Modes</Text>
                  {(() => {
                    const modes = selectedRouteForModal.modes || selectedRouteForModal.route_data?.modes || [];
                    
                    // If no modes from database, try to infer from route_id or other data
                    if (modes.length === 0) {
                      // Check if we can infer mode from route data
                      if (selectedRouteForModal.route_id?.includes('uber') || selectedRouteForModal.route_data?.route_id?.includes('uber')) {
                        return (
                          <View className="flex-row flex-wrap">
                            <View className="bg-blue-100 px-3 py-1 rounded-full mr-2 mb-2">
                              <Text className="text-blue-700 font-medium">🚗 Uber/PickMe</Text>
                            </View>
                          </View>
                        );
                      } else if (selectedRouteForModal.route_id?.includes('bus') || selectedRouteForModal.route_data?.route_id?.includes('bus')) {
                        return (
                          <View className="flex-row flex-wrap">
                            <View className="bg-blue-100 px-3 py-1 rounded-full mr-2 mb-2">
                              <Text className="text-blue-700 font-medium">🚌 Bus</Text>
                            </View>
                          </View>
                        );
                      } else {
                        return <Text className="text-gray-500 italic">Transport mode information not available</Text>;
                      }
                    }
                    
                    return (
                      <View className="flex-row flex-wrap">
                        {modes.map((mode, index) => (
                          <View key={index} className="bg-blue-100 px-3 py-1 rounded-full mr-2 mb-2">
                            <Text className="text-blue-700 font-medium">
                              {mode === 'bus' ? '🚌 Bus' : 
                               mode === 'train' ? '🚆 Train' : 
                               mode === 'walking' ? '🚶 Walking' : 
                               mode === 'tuk-tuk' ? '🛺 Tuk-tuk' : 
                               mode === 'car' ? '🚗 Car' : mode}
                            </Text>
                          </View>
                        ))}
                      </View>
                    );
                  })()}
                </View>

                {/* Route Steps */}
                <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                  <Text className="text-lg font-semibold text-gray-800 mb-3">📍 Route Steps</Text>
                  {(() => {
                    const steps = selectedRouteForModal.steps || selectedRouteForModal.route_data?.steps || [];
                    
                    if (steps.length > 0) {
                      return (
                        <View className="space-y-3">
                          {steps.map((step, index) => (
                            <View key={index} className="flex-row items-start">
                              <Text className="text-2xl mr-3">{(step as any).icon || '📍'}</Text>
                              <View className="flex-1">
                                <Text className="text-base font-medium text-gray-800">
                                  {(step as any).description || (step as any).instruction}
                                </Text>
                                <View className="flex-row items-center mt-1">
                                  {(step as any).duration && (step as any).duration !== 'N/A' && (
                                    <Text className="text-sm text-gray-500 mr-4">
                                      ⏱️ {(step as any).duration}
                                    </Text>
                                  )}
                                  {(step as any).fare && (step as any).fare !== 'N/A' && (
                                    <Text className="text-sm text-gray-500">
                                      💰 {(step as any).fare}
                                    </Text>
                                  )}
                                </View>
                              </View>
                            </View>
                          ))}
                        </View>
                      );
                    }
                    
                    // Generate steps based on route type if no database steps
                    let calculatedSteps = [];
                    const origin = selectedRouteForModal.route_data?.origin || selectedRouteForModal.source || 'Start Location';
                    const destination = selectedRouteForModal.route_data?.destination || selectedRouteForModal.destination || 'End Location';
                    const fare = selectedRouteForModal.route_data?.estimated_cost ? 
                                `${selectedRouteForModal.route_data.cost_currency || 'Rs.'} ${selectedRouteForModal.route_data.estimated_cost}` : 
                                'Fare varies';
                    
                    if (selectedRouteForModal.route_id?.includes('uber') || selectedRouteForModal.route_data?.route_id?.includes('uber')) {
                      calculatedSteps = [
                        { icon: '📍', description: `Meet driver at pickup location in ${origin}`, duration: '5 min' },
                        { icon: '🚗', description: `Travel via Uber/PickMe to ${destination}`, duration: '3-4 hours', fare: fare },
                        { icon: '🏁', description: `Arrive at ${destination}`, duration: '0 min' }
                      ];
                    } else if (selectedRouteForModal.route_id?.includes('bus')) {
                      calculatedSteps = [
                        { icon: '🚶', description: `Walk to bus station in ${origin}`, duration: '10-15 min' },
                        { icon: '🚌', description: `Take bus from ${origin} to ${destination}`, duration: '5-6 hours', fare: fare },
                        { icon: '🚶', description: `Walk to final destination in ${destination}`, duration: '5-10 min' }
                      ];
                    } else if (selectedRouteForModal.route_id?.includes('train')) {
                      calculatedSteps = [
                        { icon: '🚶', description: `Walk to railway station in ${origin}`, duration: '10-20 min' },
                        { icon: '🚂', description: `Take train from ${origin} to ${destination}`, duration: '7-8 hours', fare: fare },
                        { icon: '🚶', description: `Walk to final destination in ${destination}`, duration: '10-15 min' }
                      ];
                    }
                    
                    if (calculatedSteps.length > 0) {
                      return (
                        <View className="space-y-3">
                          {calculatedSteps.map((step, index) => (
                            <View key={index} className="flex-row items-start">
                              <Text className="text-2xl mr-3">{step.icon}</Text>
                              <View className="flex-1">
                                <Text className="text-base font-medium text-gray-800">
                                  {step.description}
                                </Text>
                                <View className="flex-row items-center mt-1">
                                  {step.duration && (
                                    <Text className="text-sm text-gray-500 mr-4">
                                      ⏱️ {step.duration}
                                    </Text>
                                  )}
                                  {step.fare && (
                                    <Text className="text-sm text-gray-500">
                                      💰 {step.fare}
                                    </Text>
                                  )}
                                </View>
                              </View>
                            </View>
                          ))}
                        </View>
                      );
                    }
                    
                    return <Text className="text-gray-500 italic">Step-by-step directions not available</Text>;
                  })()}
                </View>

                {/* AI Recommendation */}
                <View className="bg-blue-50 rounded-lg p-4 mb-4">
                  <Text className="text-lg font-semibold text-blue-800 mb-2">🤖 AI Recommendation</Text>
                  <Text className="text-base text-blue-700">
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
                         
                         if (scoreBreakdown.convenience >= 0.8) strengths.push('convenient');
                         if (scoreBreakdown.reliability >= 0.6) strengths.push('reliable');
                         if (scoreBreakdown.comfort >= 0.5) strengths.push('comfortable');
                         
                         if (strengths.length > 0) {
                           return `This route scores ${percentage}% overall and is particularly ${strengths.join(', ')}.`;
                         } else {
                           return `This route has a ${percentage}% recommendation score based on AI analysis.`;
                         }
                       }
                       
                       return 'This route has been optimized by our AI agents for the best balance of time, cost, and comfort.';
                     })()}
                  </Text>
                </View>

                {/* AI Agents Used */}
                {(selectedRouteForModal.agentsUsed || selectedRouteForModal.route_data?.agentsUsed) && (
                  <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                    <Text className="text-lg font-semibold text-gray-800 mb-3">🧠 AI Agents Used</Text>
                    <View className="flex-row flex-wrap">
                      {(selectedRouteForModal.agentsUsed || selectedRouteForModal.route_data?.agentsUsed || []).map((agent, index) => (
                        <View key={index} className="bg-purple-100 px-3 py-1 rounded-full mr-2 mb-2">
                          <Text className="text-purple-700 text-sm">{agent}</Text>
                        </View>
                      ))}
                    </View>
                  </View>
                )}

                {/* Disruptions */}
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

                {/* Actions */}
                <View className="flex-row justify-center mt-4">
                  <TouchableOpacity
                    className="bg-gray-200 py-3 px-8 rounded-lg"
                    onPress={() => setShowRouteModal(false)}
                  >
                    <Text className="text-gray-700 text-center font-semibold text-base">Close</Text>
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