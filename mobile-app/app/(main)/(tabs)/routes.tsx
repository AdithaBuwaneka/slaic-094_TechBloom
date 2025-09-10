import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { RouteOption } from '../../src/types';

interface RouteStep {
  mode: string;
  description: string;
  duration: string;
  icon: string;
}

export default function Routes() {
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);
  const [activeRoutes, setActiveRoutes] = useState<RouteOption[]>([]);
  const [recentRoutes, setRecentRoutes] = useState<RouteOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load recent routes from AsyncStorage on component mount
  useEffect(() => {
    loadRecentRoutes();
  }, []);

  const loadRecentRoutes = async () => {
    try {
      setIsLoading(true);
      const storedRoutes = await AsyncStorage.getItem('recent_routes');
      if (storedRoutes) {
        const routes: RouteOption[] = JSON.parse(storedRoutes);
        setRecentRoutes(routes.slice(0, 5)); // Show last 5 routes
      }
    } catch (error) {
      console.error('Error loading recent routes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Backup sample routes (only used for UI demonstration)
  const sampleRoutes: RouteOption[] = [
    {
      id: '1',
      title: 'Colombo Fort → Kandy',
      duration: '2h 45m',
      fare: 'Rs. 280',
      modes: ['🚂', '🚌'],
      carbonFootprint: '2.1 kg CO₂',
      aiRecommendation: 'Fastest option with scenic mountain views',
      disruptions: [],
      agentsUsed: [
        'Route Optimization Agent',
        'Fare Calculation Agent', 
        'User Preference Agent',
        'Disruption Monitoring Agent'
      ],
      steps: [
        {
          mode: 'walking',
          description: 'Walk to Colombo Fort Railway Station',
          duration: '5 min',
          icon: '🚶'
        },
        {
          mode: 'train',
          description: 'Intercity Express to Kandy',
          duration: '2h 30m',
          icon: '🚂'
        },
        {
          mode: 'walking',
          description: 'Walk to destination',
          duration: '10 min',
          icon: '🚶'
        }
      ]
    },
    {
      id: '2',
      title: 'Colombo → Airport',
      duration: '45m',
      fare: 'Rs. 110',
      modes: ['🚌'],
      carbonFootprint: '1.8 kg CO₂',
      aiRecommendation: 'Most economical airport transfer',
      disruptions: ['Minor delay: 15 mins due to traffic'],
      agentsUsed: [
        'Route Optimization Agent',
        'Fare Optimization Agent',
        'Disruption Monitoring Agent',
        'Local Knowledge Agent'
      ],
      steps: [
        {
          mode: 'walking',
          description: 'Walk to Bastian Mawatha Bus Stand',
          duration: '8 min',
          icon: '🚶'
        },
        {
          mode: 'bus',
          description: 'Airport Express Bus 187',
          duration: '45 min',
          icon: '🚌'
        }
      ]
    }
  ];

  const agentStatuses = [
    { name: 'Input Processing', status: 'completed', icon: '✅' },
    { name: 'Route Optimization', status: 'completed', icon: '✅' },
    { name: 'Fare Calculation', status: 'completed', icon: '✅' },
    { name: 'Fare Optimization', status: 'completed', icon: '✅' },
    { name: 'User Preferences', status: 'completed', icon: '✅' },
    { name: 'Disruption Monitoring', status: 'in_progress', icon: '🔄' },
    { name: 'Local Knowledge', status: 'pending', icon: '⏳' },
  ];

  const startRoute = (route: RouteOption) => {
    setActiveRoutes(prev => [...prev, route]);
    Alert.alert(
      'Route Started', 
      `Navigation started for ${route.title}. You'll receive real-time updates.`,
      [{ text: 'OK' }]
    );
  };

  const stopRoute = (routeId: string) => {
    setActiveRoutes(prev => prev.filter(r => r.id !== routeId));
    Alert.alert('Route Stopped', 'Navigation has been stopped.');
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <ScrollView className="flex-1">
        {/* Header */}
        <View className="bg-white px-4 py-4 border-b border-gray-200">
          <Text className="text-2xl font-bold text-gray-800">My Routes</Text>
          <Text className="text-sm text-gray-600">AI-powered route planning results</Text>
        </View>

        {/* Active Routes */}
        {activeRoutes.length > 0 && (
          <View className="bg-green-50 mx-4 mt-4 p-4 rounded-lg border border-green-200">
            <Text className="text-lg font-semibold text-green-800 mb-2">🟢 Active Routes</Text>
            {activeRoutes.map((route) => (
              <View key={route.id} className="flex-row items-center justify-between bg-white p-3 rounded-lg mb-2">
                <View className="flex-1">
                  <Text className="font-medium text-gray-800">{route.title}</Text>
                  <Text className="text-sm text-gray-600">In progress • {route.duration}</Text>
                </View>
                <TouchableOpacity
                  className="bg-red-100 px-3 py-1 rounded-full"
                  onPress={() => stopRoute(route.id)}
                >
                  <Text className="text-red-700 text-sm">Stop</Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>
        )}

        {/* AI Agent Status */}
        <View className="bg-white mx-4 mt-4 p-4 rounded-lg shadow-sm">
          <Text className="text-lg font-semibold text-gray-800 mb-3">🤖 AI Agents Status</Text>
          <View className="space-y-2">
            {agentStatuses.map((agent, index) => (
              <View key={index} className="flex-row items-center justify-between">
                <Text className="text-sm text-gray-700">{agent.name}</Text>
                <View className="flex-row items-center">
                  <Text className="text-xs text-gray-500 mr-2">{agent.status}</Text>
                  <Text>{agent.icon}</Text>
                </View>
              </View>
            ))}
          </View>
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
              <TouchableOpacity className="bg-blue-600 px-4 py-2 rounded-lg">
                <Text className="text-white font-medium">Plan a Route</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View className="space-y-4">
              {recentRoutes.map((route) => (
                <View key={route.id} className="bg-white rounded-lg shadow-sm overflow-hidden">
                  <TouchableOpacity
                    className="p-4"
                    onPress={() => setSelectedRoute(selectedRoute === route.id ? null : route.id)}
                  >
                    <View className="flex-row items-center justify-between mb-2">
                      <Text className="text-lg font-semibold text-gray-800">{route.title}</Text>
                      <View className="flex-row">
                        {route.modes.map((mode, index) => (
                          <Text key={index} className="text-lg ml-1">{mode}</Text>
                        ))}
                      </View>
                    </View>
                    
                    <View className="flex-row items-center mb-3">
                      <View className="flex-row items-center mr-4">
                        <Ionicons name="time" size={16} color="#6b7280" />
                        <Text className="text-sm text-gray-600 ml-1">{route.duration}</Text>
                      </View>
                      <View className="flex-row items-center mr-4">
                        <Ionicons name="cash" size={16} color="#6b7280" />
                        <Text className="text-sm text-gray-600 ml-1">{route.fare}</Text>
                      </View>
                      <View className="flex-row items-center">
                        <Ionicons name="leaf" size={16} color="#10b981" />
                        <Text className="text-sm text-green-600 ml-1">{route.carbonFootprint}</Text>
                      </View>
                    </View>

                    <View className="bg-blue-50 p-3 rounded-lg mb-3">
                      <Text className="text-sm font-medium text-blue-800">🤖 AI Recommendation</Text>
                      <Text className="text-sm text-blue-700">{route.aiRecommendation}</Text>
                    </View>

                    {route.disruptions.length > 0 && (
                      <View className="bg-orange-50 p-3 rounded-lg mb-3">
                        <Text className="text-sm font-medium text-orange-800">⚠️ Current Disruptions</Text>
                        {route.disruptions.map((disruption, index) => (
                          <Text key={index} className="text-sm text-orange-700">{disruption}</Text>
                        ))}
                      </View>
                    )}

                    <View className="flex-row items-center justify-between">
                      <TouchableOpacity
                        className="flex-1 bg-blue-600 py-2 px-4 rounded-lg mr-2"
                        onPress={() => startRoute(route)}
                      >
                        <Text className="text-white text-center font-medium">Start Navigation</Text>
                      </TouchableOpacity>
                      <TouchableOpacity className="p-2">
                        <Ionicons 
                          name={selectedRoute === route.id ? "chevron-up" : "chevron-down"} 
                          size={20} 
                          color="#6b7280" 
                        />
                      </TouchableOpacity>
                    </View>
                  </TouchableOpacity>

                  {/* Expanded Details */}
                  {selectedRoute === route.id && (
                    <View className="border-t border-gray-100 p-4">
                      {/* Route Steps */}
                      <Text className="text-sm font-medium text-gray-800 mb-3">Route Steps</Text>
                      <View className="space-y-3 mb-4">
                        {route.steps.map((step, index) => (
                          <View key={index} className="flex-row items-center">
                            <Text className="text-lg mr-3">{step.icon}</Text>
                            <View className="flex-1">
                              <Text className="text-sm font-medium text-gray-800">{step.description}</Text>
                              <Text className="text-xs text-gray-600">{step.duration}</Text>
                            </View>
                          </View>
                        ))}
                      </View>

                      {/* AI Agents Used */}
                      <Text className="text-sm font-medium text-gray-800 mb-2">AI Agents Used</Text>
                      <View className="flex-row flex-wrap">
                        {route.agentsUsed.map((agent, index) => (
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
    </SafeAreaView>
  );
}