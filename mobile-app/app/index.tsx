
import React, { useEffect } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function Index() {
  useEffect(() => {
    // Simulate checking authentication status
    const checkAuthStatus = async () => {
      try {
        // TODO: Check if user is authenticated via AsyncStorage or SecureStore
        // const token = await SecureStore.getItemAsync('access_token');
        // if (token) {
        //   router.replace('/(main)/(tabs)/home');
        // } else {
        //   router.replace('/(auth)/login');
        // }

        // For now, always go to login
        setTimeout(() => {
          router.replace('/(auth)/login');
        }, 2000);
      } catch (error) {
        console.error('Auth check failed:', error);
        router.replace('/(auth)/login');
      }
    };

    checkAuthStatus();
  }, []);

  return (
    <SafeAreaView className="flex-1 bg-blue-600">
      <View className="flex-1 justify-center items-center px-6">
        {/* App Logo */}
        <View className="items-center mb-8">
          <View className="w-24 h-24 bg-white rounded-full items-center justify-center mb-4">
            <Text className="text-4xl">🚌</Text>
          </View>
          <Text className="text-white text-3xl font-bold text-center mb-2">
            Transit Companion
          </Text>
          <Text className="text-blue-100 text-lg text-center">
            AI-Powered Travel Assistant
          </Text>
          <Text className="text-blue-200 text-sm text-center mt-2">
            For Sri Lankan Transportation
          </Text>
        </View>

        {/* Loading Animation */}
        <View className="items-center">
          <ActivityIndicator size="large" color="white" />
          <Text className="text-white text-base mt-4">
            Initializing AI Agents...
          </Text>
        </View>

        {/* SLAIC 2025 Badge */}
        <View className="absolute bottom-8 items-center">
          <View className="bg-white/20 px-4 py-2 rounded-full">
            <Text className="text-white text-sm font-medium">
              🏆 SLAIC 2025 • 10 AI Agents
            </Text>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}
