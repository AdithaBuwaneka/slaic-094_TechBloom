import React from 'react';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function Welcome() {
  return (
    <SafeAreaView className="flex-1 bg-blue-50">
      <View className="flex-1 justify-center items-center px-6">
        {/* Welcome Illustration */}
        <View className="w-64 h-64 bg-blue-100 rounded-full justify-center items-center mb-8">
          <Text className="text-6xl">🚌</Text>
          <Text className="text-2xl mt-2">🚂</Text>
          <Text className="text-4xl">🛺</Text>
        </View>

        {/* Welcome Text */}
        <View className="items-center mb-8">
          <Text className="text-3xl font-bold text-gray-800 text-center mb-4">
            Welcome to Transit Companion!
          </Text>
          <Text className="text-lg text-gray-600 text-center leading-6">
            Your AI-powered travel assistant for navigating Sri Lankan public transport with ease
          </Text>
        </View>

        {/* Features List */}
        <View className="w-full mb-8">
          {[
            { icon: '🤖', text: 'AI-powered route planning' },
            { icon: '⚡', text: 'Real-time updates & disruptions' },
            { icon: '💰', text: 'Fare optimization & savings' },
            { icon: '🌍', text: 'Multi-language support' }
          ].map((feature, index) => (
            <View key={index} className="flex-row items-center mb-3">
              <Text className="text-2xl mr-3">{feature.icon}</Text>
              <Text className="text-base text-gray-700">{feature.text}</Text>
            </View>
          ))}
        </View>

        {/* Continue Button */}
        <TouchableOpacity
          className="bg-blue-600 rounded-lg py-4 px-8 w-full"
          onPress={() => router.push('/(onboarding)/preferences')}
        >
          <Text className="text-white text-center text-lg font-semibold">
            Let's Get Started
          </Text>
        </TouchableOpacity>

        {/* Skip Option */}
        <TouchableOpacity
          className="mt-4"
          onPress={() => router.replace('/(main)/(tabs)/home')}
        >
          <Text className="text-gray-500 text-center text-base">
            Skip Setup (Can configure later)
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}