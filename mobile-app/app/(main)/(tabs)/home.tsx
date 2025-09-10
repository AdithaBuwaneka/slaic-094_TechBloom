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
    mode: SriLankanTravelMode.TRANSIT
  });
  const [showModeSelector, setShowModeSelector] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'si' | 'ta'>('en');
  const [isPlanning, setIsPlanning] = useState(false);
  const [showAgentAnimation, setShowAgentAnimation] = useState(false);

  const handleModeSelect = (mode: SriLankanTravelMode) => {
    setRouteRequest(prev => ({ ...prev, mode }));
    setShowModeSelector(false);
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
        console.log('Route planning response:', response.data);
        // Store the planned route with safety checks for the correct API structure
        if (response.data.response) {
          const apiResponse = response.data.response;
          
          // Check for routes in the actual API structure
          if (apiResponse.best_route) {
            console.log('Found best route:', apiResponse.best_route);
            setCurrentRoute(apiResponse.best_route);
            await addToRouteHistory(apiResponse.best_route);
          } else if (apiResponse.all_routes && apiResponse.all_routes.length > 0) {
            console.log('Found routes in all_routes:', apiResponse.all_routes);
            const bestRoute = apiResponse.all_routes[0];
            setCurrentRoute(bestRoute);
            await addToRouteHistory(bestRoute);
          } else {
            console.warn('No routes found. Total routes found:', apiResponse.total_routes_found);
            
            // Create a mock route for testing purposes
            const mockRoute: any = {
              route_id: `mock_${Date.now()}`,
              title: `${requestWithUser.source} → ${requestWithUser.destination}`,
              duration: '2h 30m',
              fare: 'Rs. 350',
              modes: [requestWithUser.mode],
              carbonFootprint: '2.1 kg CO₂',
              aiRecommendation: 'AI optimized route with cost efficiency',
              agentsUsed: response.data.agents_used || [],
              source: requestWithUser.source,
              destination: requestWithUser.destination,
              mode: requestWithUser.mode,
              steps: [
                { step: 1, instruction: `Start from ${requestWithUser.source}`, duration: '0m', fare: 'Rs. 0' },
                { step: 2, instruction: `Travel via ${requestWithUser.mode}`, duration: '2h 30m', fare: 'Rs. 350' },
                { step: 3, instruction: `Arrive at ${requestWithUser.destination}`, duration: '0m', fare: 'Rs. 0' }
              ]
            };
            
            console.log('Created mock route for testing:', mockRoute);
            setCurrentRoute(mockRoute);
            await addToRouteHistory(mockRoute);
            
            Alert.alert(
              'Mock Route Created', 
              `Created a test route for ${requestWithUser.source} to ${requestWithUser.destination}. Check the Routes tab to see it.`,
              [
                { text: 'OK' },
                { text: 'View Routes', onPress: () => console.log('Navigate to routes tab') }
              ]
            );
          }
        } else {
          console.warn('No response data found');
        }
      } else {
        console.warn('Route planning failed:', response);
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
              <Text className="text-white text-2xl font-bold">
                Good morning{user?.name ? `, ${user.name.split(' ')[0]}` : ''}!
              </Text>
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
            <Text className="text-sm font-medium mb-2" style={{ color: theme.textSecondary }}>To</Text>
            <View className="flex-row items-center border rounded-lg" style={{ borderColor: theme.border }}>
              <Ionicons name="flag" size={20} color={theme.textTertiary} className="ml-3" />
              <TextInput
                className="flex-1 px-3 py-3 text-base"
                style={{ color: theme.text }}
                placeholder="Enter destination"
                placeholderTextColor={theme.textTertiary}
                value={routeRequest.destination}
                onChangeText={(value) => setRouteRequest(prev => ({ ...prev, destination: value }))}
              />
            </View>
          </View>

          {/* Transport Mode Selection */}
          <View className="mb-6">
            <Text className="text-sm font-medium mb-3" style={{ color: theme.textSecondary }}>Travel Mode</Text>
            <TouchableOpacity
              className="border rounded-lg p-4 flex-row items-center justify-between"
              style={{ borderColor: theme.border, backgroundColor: theme.surface }}
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
                   routeRequest.mode === SriLankanTravelMode.TRANSIT ? '🚊' :
                   routeRequest.mode === SriLankanTravelMode.WALKING ? '🚶' : 
                   '🚌'}
                </Text>
                <View>
                  <Text className="text-base font-medium" style={{ color: theme.text }}>
                    {routeRequest.mode === SriLankanTravelMode.BUS ? 'Bus' :
                     routeRequest.mode === SriLankanTravelMode.TRAIN ? 'Train' :
                     routeRequest.mode === SriLankanTravelMode.TUK_TUK ? 'Tuk Tuk' :
                     routeRequest.mode === SriLankanTravelMode.UBER ? 'Uber/PickMe' :
                     routeRequest.mode === SriLankanTravelMode.DRIVING ? 'Own Vehicle' :
                     routeRequest.mode === SriLankanTravelMode.TWO_WHEELER ? 'Motorbike' :
                     routeRequest.mode === SriLankanTravelMode.TRANSIT ? 'Mixed Transit' :
                     routeRequest.mode === SriLankanTravelMode.WALKING ? 'Walking' :
                     'Transit'}
                  </Text>
                  <Text className="text-sm" style={{ color: theme.textSecondary }}>Tap to change mode</Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={20} color={theme.textTertiary} />
            </TouchableOpacity>
          </View>

          {/* Plan Route Button */}
          <TouchableOpacity
            className={`rounded-lg py-3 ${isPlanning ? 'opacity-70' : ''}`}
            style={{ backgroundColor: theme.primary }}
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
          <Text className="text-lg font-semibold mb-3" style={{ color: theme.text }}>Popular Destinations</Text>
          <View className="flex-row flex-wrap gap-3">
            {quickDestinations.map((dest, index) => (
              <TouchableOpacity
                key={index}
                className="flex-row items-center px-4 py-3 rounded-lg shadow-sm border"
                style={{ backgroundColor: theme.surface, borderColor: theme.border }}
                onPress={() => selectQuickDestination(dest.name)}
              >
                <Text className="mr-2">{dest.icon}</Text>
                <Text className="text-sm font-medium" style={{ color: theme.text }}>{dest.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Features Overview */}
        <View className="px-4 mb-6">
          <Text className="text-lg font-semibold mb-3" style={{ color: theme.text }}>AI-Powered Features</Text>
          <View className="space-y-3">
            {[
              { icon: '🤖', title: '10 AI Agents', description: 'Multi-agent route optimization' },
              { icon: '⚡', title: 'Real-time Updates', description: 'Live disruption monitoring' },
              { icon: '💰', title: 'Fare Optimization', description: 'Find cheapest combinations' },
              { icon: '🌍', title: 'Multilingual', description: 'English, Sinhala, Tamil support' }
            ].map((feature, index) => (
              <View key={index} className="p-4 rounded-lg shadow-sm border flex-row items-center" style={{ backgroundColor: theme.surface, borderColor: theme.border }}>
                <Text className="text-2xl mr-4">{feature.icon}</Text>
                <View className="flex-1">
                  <Text className="text-base font-medium" style={{ color: theme.text }}>{feature.title}</Text>
                  <Text className="text-sm" style={{ color: theme.textSecondary }}>{feature.description}</Text>
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Recent Activity */}
        <View className="px-4 mb-8">
          <Text className="text-lg font-semibold mb-3" style={{ color: theme.text }}>Recent Routes</Text>
          <View className="p-4 rounded-lg shadow-sm border" style={{ backgroundColor: theme.surface, borderColor: theme.border }}>
            <Text className="text-center py-4" style={{ color: theme.textSecondary }}>
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
        <View className="absolute inset-0 bg-black/50 justify-center px-4">
          <View className="rounded-2xl max-h-[80%]" style={{ backgroundColor: theme.surface }}>
            <View className="flex-row justify-between items-center p-4 border-b" style={{ borderColor: theme.border }}>
              <Text className="text-lg font-bold" style={{ color: theme.text }}>Select Travel Mode</Text>
              <TouchableOpacity
                onPress={() => setShowModeSelector(false)}
                className="p-1"
              >
                <Ionicons name="close" size={24} color={theme.textTertiary} />
              </TouchableOpacity>
            </View>
            <ScrollView className="max-h-[400px]" showsVerticalScrollIndicator={false}>
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