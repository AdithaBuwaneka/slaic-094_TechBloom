import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import MultiAgentAnimation from '../../components/MultiAgentAnimation';
import SriLankanModeSelector from '../../components/SriLankanModeSelector';
import { SriLankanTravelMode, RouteRequest as RouteRequestType } from '../../../src/types';
import { useApp, useAuth } from '../../../src/contexts/AppContext';
import { useTheme } from '../../../src/contexts/ThemeContext';
import { travelService } from '../../../src/services/api/travelService';


export default function Home() {
  const { user } = useAuth();
  const { theme } = useTheme();
  const { currentRoute, setCurrentRoute, addToRouteHistory } = useApp();
  
  const [routeRequest, setRouteRequest] = useState<RouteRequestType>({
    user_id: user?.user_id || '',
    source: '',
    destination: '',
    mode: SriLankanTravelMode.TRANSIT,
    preferredTransit: ''
  });
  const [showModeSelector, setShowModeSelector] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'si' | 'ta'>('en');
  const [isPlanning, setIsPlanning] = useState(false);
  const [showAgentAnimation, setShowAgentAnimation] = useState(false);

  const handleModeSelect = (mode: SriLankanTravelMode) => {
    setRouteRequest(prev => ({ ...prev, mode }));
    setShowModeSelector(false);
  };

  const handleAgentAnimationComplete = (results: any) => {
    setIsPlanning(false);
    setShowAgentAnimation(false);
    
    if (results.success) {
      Alert.alert(
        '🎉 Route Planning Complete!', 
        `Found ${results.routes?.length || 0} optimized route(s) using ${results.agentSummary?.totalAgents || 10} AI agents.`,
        [{ text: 'View Routes', onPress: () => console.log('Navigate to routes') }]
      );
    } else {
      Alert.alert('Planning Failed', 'Unable to find suitable routes. Please try different options.');
    }
  };

  const handleCloseAnimation = () => {
    setShowAgentAnimation(false);
    setIsPlanning(false);
  };

  const quickDestinations = [
    { name: 'Colombo Fort', icon: '🏛️' },
    { name: 'Kandy', icon: '🏔️' },
    { name: 'Galle', icon: '🏖️' },
    { name: 'Airport', icon: '✈️' },
    { name: 'Negombo', icon: '🌊' },
    { name: 'Anuradhapura', icon: '🏛️' }
  ];

  const handlePlanRoute = async () => {
    if (!routeRequest.source || !routeRequest.destination) {
      Alert.alert('Error', 'Please enter both source and destination');
      return;
    }

    if (!user) {
      Alert.alert('Authentication Required', 'Please log in to plan routes');
      return;
    }

    setIsPlanning(true);
    setShowAgentAnimation(true);

    try {
      // Update route request with user ID
      const requestWithUser = {
        ...routeRequest,
        user_id: user.user_id
      };

      // Call the travel service to plan the route
      const response = await travelService.planRoute(requestWithUser);
      
      if (response.success && response.data) {
        // Store the planned route
        const bestRoute = response.data.response.recommended_routes[0];
        if (bestRoute) {
          setCurrentRoute(bestRoute);
          addToRouteHistory(bestRoute);
        }
      }
    } catch (error) {
      console.error('Route planning error:', error);
      Alert.alert('Error', 'Failed to plan route. Please try again.');
      setIsPlanning(false);
      setShowAgentAnimation(false);
    }
  };

  const handleAgentAnimationComplete = (results: any) => {
    setIsPlanning(false);
    setShowAgentAnimation(false);
    Alert.alert(
      '🎉 Route Planning Complete!', 
      `Found ${results.routes.length} optimized route(s) using ${results.agentSummary.totalAgents} AI agents. Check the Routes tab for details.`,
      [{ text: 'View Routes', onPress: () => console.log('Navigate to routes') }]
    );
  };

  const handleCloseAnimation = () => {
    setShowAgentAnimation(false);
    setIsPlanning(false);
  };

  const selectQuickDestination = (destination: string) => {
    setRouteRequest(prev => ({ ...prev, destination }));
  };

  return (
    <SafeAreaView className="flex-1" style={{ backgroundColor: theme.background }}>
      <ScrollView className="flex-1">
        {/* Header */}
        <View className="px-6 py-8" style={{ backgroundColor: theme.primary }}>
          <View className="flex-row justify-between items-center mb-4">
            <View>
              <Text className="text-white text-2xl font-bold">Good morning!</Text>
              <Text className="text-blue-100 text-base">Where would you like to go?</Text>
            </View>
            <TouchableOpacity className="p-2 bg-blue-500 rounded-full">
              <Ionicons name="notifications" size={24} color="white" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Route Planning Form */}
        <View className="mx-4 -mt-4 rounded-xl shadow-lg p-6 mb-6" style={{ backgroundColor: theme.surface }}>
          <Text className="text-lg font-semibold mb-4" style={{ color: theme.text }}>Plan Your Journey</Text>
          
          {/* Source Input */}
          <View className="mb-4">
            <Text className="text-sm font-medium mb-2" style={{ color: theme.textSecondary }}>From</Text>
            <View className="flex-row items-center border rounded-lg" style={{ borderColor: theme.border }}>
              <Ionicons name="location" size={20} color={theme.textTertiary} className="ml-3" />
              <TextInput
                className="flex-1 px-3 py-3 text-base"
                style={{ color: theme.text }}
                placeholder="Enter starting location"
                placeholderTextColor={theme.textTertiary}
                value={routeRequest.source}
                onChangeText={(value) => setRouteRequest(prev => ({ ...prev, source: value }))}
              />
            </View>
          </View>

          {/* Destination Input */}
          <View className="mb-4">
            <Text className="text-sm font-medium text-gray-600 mb-2">To</Text>
            <View className="flex-row items-center border border-gray-300 rounded-lg">
              <Ionicons name="flag" size={20} color="#6b7280" className="ml-3" />
              <TextInput
                className="flex-1 px-3 py-3 text-base"
                placeholder="Enter destination"
                value={routeRequest.destination}
                onChangeText={(value) => setRouteRequest(prev => ({ ...prev, destination: value }))}
              />
            </View>
          </View>

          {/* Transport Mode Selection */}
          <View className="mb-6">
            <Text className="text-sm font-medium text-gray-600 mb-3">Travel Mode</Text>
            <TouchableOpacity
              className="border border-gray-300 rounded-lg p-4 flex-row items-center justify-between bg-gray-50"
              onPress={() => setShowModeSelector(true)}
            >
              <View className="flex-row items-center">
                <Text className="mr-3 text-2xl">
                  {routeRequest.mode === SriLankanTravelMode.BUS ? '🚌' :
                   routeRequest.mode === SriLankanTravelMode.TRAIN ? '🚂' :
                   routeRequest.mode === SriLankanTravelMode.TUK_TUK ? '🛺' :
                   routeRequest.mode === SriLankanTravelMode.UBER ? '🚗' :
                   routeRequest.mode === SriLankanTravelMode.DRIVING ? '🚙' :
                   routeRequest.mode === SriLankanTravelMode.TWO_WHEELER ? '🏍️' :
                   '🚶'}
                </Text>
                <View>
                  <Text className="text-base font-medium text-gray-800">
                    {routeRequest.mode === SriLankanTravelMode.BUS ? 'Bus' :
                     routeRequest.mode === SriLankanTravelMode.TRAIN ? 'Train' :
                     routeRequest.mode === SriLankanTravelMode.TUK_TUK ? 'Tuk Tuk' :
                     routeRequest.mode === SriLankanTravelMode.UBER ? 'Uber/PickMe' :
                     routeRequest.mode === SriLankanTravelMode.DRIVING ? 'Own Vehicle' :
                     routeRequest.mode === SriLankanTravelMode.TWO_WHEELER ? 'Motorbike' :
                     'Walking'}
                  </Text>
                  <Text className="text-sm text-gray-600">Tap to change mode</Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#6b7280" />
            </TouchableOpacity>
          </View>

          {/* Plan Route Button */}
          <TouchableOpacity
            className={`bg-blue-600 rounded-lg py-3 ${isPlanning ? 'opacity-70' : ''}`}
            onPress={handlePlanRoute}
            disabled={isPlanning}
          >
            <Text className="text-white text-center text-lg font-semibold">
              {isPlanning ? 'Planning Route...' : '🤖 Plan with AI Agents'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Quick Destinations */}
        <View className="px-4 mb-6">
          <Text className="text-lg font-semibold text-gray-800 mb-3">Popular Destinations</Text>
          <View className="flex-row flex-wrap gap-3">
            {quickDestinations.map((dest, index) => (
              <TouchableOpacity
                key={index}
                className="bg-white flex-row items-center px-4 py-3 rounded-lg shadow-sm border border-gray-100"
                onPress={() => selectQuickDestination(dest.name)}
              >
                <Text className="mr-2">{dest.icon}</Text>
                <Text className="text-sm font-medium text-gray-700">{dest.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Features Overview */}
        <View className="px-4 mb-6">
          <Text className="text-lg font-semibold text-gray-800 mb-3">AI-Powered Features</Text>
          <View className="space-y-3">
            {[
              { icon: '🤖', title: '10 AI Agents', description: 'Multi-agent route optimization' },
              { icon: '⚡', title: 'Real-time Updates', description: 'Live disruption monitoring' },
              { icon: '💰', title: 'Fare Optimization', description: 'Find cheapest combinations' },
              { icon: '🌍', title: 'Multilingual', description: 'English, Sinhala, Tamil support' }
            ].map((feature, index) => (
              <View key={index} className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex-row items-center">
                <Text className="text-2xl mr-4">{feature.icon}</Text>
                <View className="flex-1">
                  <Text className="text-base font-medium text-gray-800">{feature.title}</Text>
                  <Text className="text-sm text-gray-600">{feature.description}</Text>
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Recent Activity */}
        <View className="px-4 mb-8">
          <Text className="text-lg font-semibold text-gray-800 mb-3">Recent Routes</Text>
          <View className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <Text className="text-gray-500 text-center py-4">
              No recent routes yet. Plan your first journey above!
            </Text>
          </View>
        </View>
      </ScrollView>

      {/* Multi-Agent Animation Modal */}
      <MultiAgentAnimation
        visible={showAgentAnimation}
        onComplete={handleAgentAnimationComplete}
        onClose={handleCloseAnimation}
        requestData={routeRequest}
      />

      {/* Sri Lankan Mode Selector Modal */}
      {showModeSelector && (
        <View className="absolute inset-0 bg-black bg-opacity-50 flex-1 justify-center px-4">
          <View className="bg-white rounded-2xl max-h-[80%] overflow-hidden">
            <View className="flex-row justify-between items-center p-4 border-b border-gray-200">
              <Text className="text-lg font-bold text-gray-900">Select Travel Mode</Text>
              <TouchableOpacity
                onPress={() => setShowModeSelector(false)}
                className="p-1"
              >
                <Ionicons name="close" size={24} color="#6b7280" />
              </TouchableOpacity>
            </View>
            <ScrollView className="flex-1">
              <SriLankanModeSelector
                selectedMode={routeRequest.mode}
                onModeSelect={handleModeSelect}
                language={selectedLanguage}
                isLoading={isPlanning}
                showDescriptions={true}
              />
            </ScrollView>
          </View>
        </View>
      )}
    </SafeAreaView>
  );
}