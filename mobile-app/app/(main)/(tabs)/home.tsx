import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import MultiAgentAnimation from '../../../components/MultiAgentAnimation';
import SriLankanModeSelector from '../../../components/SriLankanModeSelector';
import { SriLankanTravelMode, RouteRequest as RouteRequestType } from '../../../src/types';
import { useApp, useAuth } from '../../../src/contexts/AppContext';
import { useTheme } from '../../../src/contexts/ThemeContext';
import { useLanguage } from '../../../src/contexts/LanguageContext';
import { travelService } from '../../../src/services/api/travelService';


export default function Home() {
  const { user } = useAuth();
  const { theme } = useTheme();
  const { t } = useLanguage();
  const { setCurrentRoute, addToRouteHistory } = useApp();
  const router = useRouter();
  
  const [routeRequest, setRouteRequest] = useState<RouteRequestType>({
    user_id: user?.user_id || '',
    source: '',
    destination: '',
    mode: SriLankanTravelMode.TRANSIT
  });

  // Update user_id when user changes
  React.useEffect(() => {
    if (user?.user_id && routeRequest.user_id !== user.user_id) {
      setRouteRequest(prev => ({ ...prev, user_id: user.user_id }));
    }
  }, [user?.user_id, routeRequest.user_id]);
  const [showModeSelector, setShowModeSelector] = useState(false);
  const [selectedLanguage] = useState<'en' | 'si' | 'ta'>('en');
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

      console.log('🚀 Starting route planning with agent workflow:', requestWithUser);

      // Call the travel service to plan the route
      const response = await travelService.planRoute(requestWithUser);
      
      if (response.success && response.data) {
        console.log('✅ Agent workflow completed successfully!');
        console.log('📊 Processing time:', response.data.processing_time, 'seconds');
        console.log('🤖 Agents used:', response.data.agents_used);
        
        // Extract the actual response data
        const apiResponse = response.data.response;
        
        if (!apiResponse) {
          throw new Error('No response data received from backend');
        }

        // Get the best route from backend
        const bestRoute = apiResponse.best_route as any;
        
        if (!bestRoute) {
          throw new Error('No route found from backend');
        }

        console.log('🛣️ Best route selected by AI:', bestRoute.route_id);
        console.log('📈 Recommendation score:', Math.round((bestRoute.recommendation_score || 0) * 100) + '%');

        // Transform backend route to mobile app format - COMPLETE DATA FROM AGENTS
        const transformedRoute: any = {
          // Core identification
          route_id: bestRoute.route_id,
          id: bestRoute.route_id,
          request_id: response.data.request_id,
          
          // Route details from user input
          source: requestWithUser.source,
          destination: requestWithUser.destination,
          title: `${requestWithUser.source} → ${requestWithUser.destination}`,
          mode: requestWithUser.mode,
          
          // AGENT-GENERATED DATA: Duration and distance from backend
          duration: bestRoute.duration_text,
          distance: bestRoute.distance_text,
          
          // AGENT-GENERATED DATA: Fare from fare calculation agent
          fare: bestRoute.estimated_cost !== undefined ? 
                `${bestRoute.cost_currency} ${bestRoute.estimated_cost}` : 
                'Fare not calculated',
          
          // AGENT-GENERATED DATA: Transit modes from transit aggregation agent
          modes: bestRoute.transit_modes || [],
          
          // AGENT-GENERATED DATA: AI recommendation from route optimization agent
          aiRecommendation: bestRoute.is_recommended 
            ? `🎯 AI Recommended (${Math.round((bestRoute.recommendation_score || 0) * 100)}% confidence)`
            : `Alternative Route (${Math.round((bestRoute.recommendation_score || 0) * 100)}% confidence)`,
          
          // AGENT-GENERATED DATA: Detailed steps from standard/transit route agents
          steps: (bestRoute.steps || []).map((step: any, index: number) => ({
            id: index,
            icon: step.travel_mode === 'TRANSIT' ? '🚌' : 
                  step.travel_mode === 'WALKING' ? '🚶' : 
                  step.travel_mode === 'DRIVING' ? '🚗' : '📍',
            description: step.html_instructions,
            instruction: step.html_instructions,
            duration: step.duration,
            distance: step.distance,
            travel_mode: step.travel_mode,
            transit_details: step.transit_details,
            fare_details: step.fare_details,
            fare: step.fare_details?.base_fare ? 
                  `${bestRoute.cost_currency || 'LKR'} ${step.fare_details.base_fare}` : 
                  step.travel_mode === 'WALKING' ? 'Free' : 'Included'
          })),
          
          // AGENT-GENERATED DATA: Complete backend route data from all agents
          route_data: bestRoute,
          
          // AGENT-GENERATED DATA: All routes found by agents
          all_routes: apiResponse.all_routes || [],
          total_routes_found: apiResponse.total_routes_found || 0,
          
          // AGENT-GENERATED DATA: AI disruption analysis from disruption monitoring agent
          ai_disruption_analysis: apiResponse.ai_disruption_analysis,
          
          // AGENT-GENERATED DATA: Destination insights from local knowledge agent
          destination_summary: apiResponse.destination_summary,
          
          // AGENT-GENERATED DATA: Active disruptions detected
          active_disruptions: apiResponse.active_disruptions || [],
          disruptions: (apiResponse.active_disruptions || []).map((d: any) => 
            `${d.type} at ${d.location} (${d.severity})`),
          
          // AGENT-GENERATED DATA: Agent workflow metadata
          agentsUsed: response.data.agents_used || [],
          agents_count: response.data.agents_used?.length || 0,
          processing_time: response.data.processing_time || 0,
          request_timestamp: new Date().toISOString(),
          trace_id: response.data.trace_id,
          
          // AGENT-GENERATED DATA: Score breakdown from route optimization agent
          score_breakdown: bestRoute.score_breakdown || {},
          recommendation_score: bestRoute.recommendation_score || 0,
          
          // Legacy fields for compatibility
          carbonFootprint: bestRoute.distance_text || 'Distance not available',
          summary: {
            duration_minutes: parseInt(bestRoute.duration_text?.match(/\d+/)?.[0] || '0'),
            distance_km: parseFloat(bestRoute.distance_text?.match(/[\d.]+/)?.[0] || '0'),
            estimated_fare: bestRoute.estimated_cost || 0,
            transit_modes: bestRoute.transit_modes || [],
            transfers: bestRoute.transfers || 0,
            walking_distance: bestRoute.walking_distance || 0,
            carbon_footprint: parseFloat(bestRoute.distance_text?.match(/[\d.]+/)?.[0] || '0')
          },
          fare_breakdown: {
            total_fare: bestRoute.estimated_cost || 0,
            currency: bestRoute.cost_currency || 'LKR',
            breakdown: bestRoute.step_fares || [],
            savings_vs_alternatives: 0,
            optimization_applied: false
          },
          agent_analysis: {
            user_preference_score: bestRoute.recommendation_score || 0,
            fare_optimization_score: bestRoute.score_breakdown?.cost || 0,
            disruption_risk_score: 1 - (bestRoute.score_breakdown?.reliability || 0.5),
            comfort_score: bestRoute.score_breakdown?.comfort || 0,
            recommendations: [bestRoute.is_recommended ? 'AI Recommended Route' : 'Alternative Route']
          },
          alternatives: (apiResponse.all_routes || []).filter((r: any) => r.route_id !== bestRoute.route_id)
        };

        console.log('✨ Route transformation complete with agent data');
        
        // Store in app state and history
        setCurrentRoute(transformedRoute);
        await addToRouteHistory(transformedRoute);
        
        setIsPlanning(false);
        setShowAgentAnimation(false);
        
        // Navigate to routes page
        router.push('/(main)/(tabs)/routes');
      } else {
        console.error('❌ Route planning failed:', response);
        Alert.alert('Error', 'Failed to plan route. Please try again.');
        setIsPlanning(false);
        setShowAgentAnimation(false);
      }
    } catch (error) {
      console.error('💥 Route planning error:', error);
      Alert.alert('Error', `Failed to plan route: ${error}`);
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
      [
        { text: 'OK' },
        { text: 'View Routes', onPress: () => router.push('/(main)/(tabs)/routes') }
      ]
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
              <Text className="text-blue-100 text-base">{t('home.subtitle')}</Text>
            </View>
            <TouchableOpacity className="p-2 bg-blue-500 rounded-full">
              <Ionicons name="notifications" size={24} color="white" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Route Planning Form */}
        <View className="mx-4 -mt-4 rounded-xl shadow-lg p-6 mb-6" style={{ backgroundColor: theme.surface }}>
          <Text className="text-lg font-semibold mb-4" style={{ color: theme.text }}>{t('home.planRoute')}</Text>
          
          {/* Source Input */}
          <View className="mb-4">
            <Text className="text-sm font-medium mb-2" style={{ color: theme.textSecondary }}>{t('home.from')}</Text>
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
            <Text className="text-sm font-medium mb-2" style={{ color: theme.textSecondary }}>{t('home.to')}</Text>
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
              {isPlanning ? t('common.loading') : `🤖 ${t('home.planRoute')}`}
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