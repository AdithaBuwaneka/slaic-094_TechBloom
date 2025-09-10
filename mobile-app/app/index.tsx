
import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function Index() {
  return (
    <SafeAreaView className="flex-1 bg-blue-600">
      <View className="flex-1 justify-center items-center px-6">
        {/* App Logo */}
        <View className="items-center mb-12">
          <View className="w-32 h-32 bg-white rounded-full items-center justify-center mb-6">
            <Text className="text-5xl">🚌</Text>
          </View>
          <Text className="text-white text-4xl font-bold text-center mb-3">
            Transit Companion
          </Text>
          <Text className="text-blue-100 text-xl text-center mb-2">
            AI-Powered Travel Assistant
          </Text>
          <Text className="text-blue-200 text-base text-center">
            For Sri Lankan Transportation
          </Text>
        </View>

        {/* Action Buttons */}
        <View className="w-full max-w-sm">
          <TouchableOpacity 
            className="bg-white rounded-xl py-4 px-8 items-center mb-4"
            onPress={() => router.push('/(auth)/login')}
          >
            <Text className="text-blue-600 text-lg font-semibold">
              Login
            </Text>
          </TouchableOpacity>

          <TouchableOpacity 
            className="bg-blue-500 border-2 border-white rounded-xl py-4 px-8 items-center"
            onPress={() => router.push('/(auth)/register')}
          >
            <Text className="text-white text-lg font-semibold">
              Register
            </Text>
          </TouchableOpacity>
        </View>

        {/* Features Preview */}
        <View className="mt-8 items-center">
          <Text className="text-blue-100 text-sm text-center mb-2">
            • Real-time route planning • 10 AI agents • Community reports
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
