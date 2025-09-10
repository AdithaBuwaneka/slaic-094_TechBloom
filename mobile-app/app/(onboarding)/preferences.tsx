import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Switch } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

interface Preferences {
  transitModes: string[];
  maxWalkingDistance: number;
  budgetPreference: string;
  timeVsCost: number;
  comfort: number;
  accessibility: string[];
  notifications: {
    delays: boolean;
    offers: boolean;
    reminders: boolean;
  };
}

export default function PreferencesSetup() {
  const [preferences, setPreferences] = useState<Preferences>({
    transitModes: ['bus', 'train'],
    maxWalkingDistance: 1.0,
    budgetPreference: 'medium',
    timeVsCost: 0.5,
    comfort: 0.7,
    accessibility: [],
    notifications: {
      delays: true,
      offers: true,
      reminders: true
    }
  });

  const transitModes = [
    { id: 'bus', label: 'Bus', icon: '🚌', description: 'Inter-city & local buses' },
    { id: 'train', label: 'Train', icon: '🚂', description: 'Sri Lanka Railways' },
    { id: 'tuk-tuk', label: 'Tuk-tuk', icon: '🛺', description: 'Three-wheelers' },
    { id: 'uber', label: 'Ride-sharing', icon: '🚗', description: 'Uber, PickMe' },
    { id: 'walking', label: 'Walking', icon: '🚶', description: 'Pedestrian routes' }
  ];

  const budgetOptions = [
    { id: 'low', label: 'Budget-conscious', icon: '💰' },
    { id: 'medium', label: 'Balanced', icon: '⚖️' },
    { id: 'high', label: 'Premium comfort', icon: '💎' }
  ];

  const accessibilityOptions = [
    { id: 'wheelchair', label: 'Wheelchair accessible' },
    { id: 'visual', label: 'Visual assistance' },
    { id: 'hearing', label: 'Hearing assistance' },
    { id: 'elderly', label: 'Senior-friendly routes' }
  ];

  const toggleTransitMode = (mode: string) => {
    setPreferences(prev => ({
      ...prev,
      transitModes: prev.transitModes.includes(mode)
        ? prev.transitModes.filter(m => m !== mode)
        : [...prev.transitModes, mode]
    }));
  };

  const toggleAccessibility = (option: string) => {
    setPreferences(prev => ({
      ...prev,
      accessibility: prev.accessibility.includes(option)
        ? prev.accessibility.filter(a => a !== option)
        : [...prev.accessibility, option]
    }));
  };

  const updateNotification = (type: keyof typeof preferences.notifications) => {
    setPreferences(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [type]: !prev.notifications[type]
      }
    }));
  };

  const handleSavePreferences = async () => {
    try {
      // TODO: Send preferences to backend API
      console.log('Saving preferences:', preferences);
      
      // Navigate to main app
      router.replace('/(main)/(tabs)/home');
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <ScrollView className="flex-1 px-6 py-4">
        {/* Header */}
        <View className="mb-6">
          <Text className="text-2xl font-bold text-gray-800 mb-2">
            Set Your Preferences
          </Text>
          <Text className="text-base text-gray-600">
            Help us personalize your travel experience
          </Text>
        </View>

        {/* Preferred Transit Modes */}
        <View className="mb-6">
          <Text className="text-lg font-semibold text-gray-800 mb-3">
            Preferred Transport Modes
          </Text>
          <View className="space-y-3">
            {transitModes.map((mode) => (
              <TouchableOpacity
                key={mode.id}
                className={`flex-row items-center p-4 rounded-lg border ${
                  preferences.transitModes.includes(mode.id)
                    ? 'bg-blue-50 border-blue-300'
                    : 'bg-gray-50 border-gray-200'
                }`}
                onPress={() => toggleTransitMode(mode.id)}
              >
                <Text className="text-2xl mr-3">{mode.icon}</Text>
                <View className="flex-1">
                  <Text className="text-base font-medium text-gray-800">
                    {mode.label}
                  </Text>
                  <Text className="text-sm text-gray-600">
                    {mode.description}
                  </Text>
                </View>
                <View className={`w-6 h-6 rounded-full border-2 ${
                  preferences.transitModes.includes(mode.id)
                    ? 'bg-blue-600 border-blue-600'
                    : 'border-gray-300'
                }`}>
                  {preferences.transitModes.includes(mode.id) && (
                    <Text className="text-white text-center text-xs">✓</Text>
                  )}
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Budget Preference */}
        <View className="mb-6">
          <Text className="text-lg font-semibold text-gray-800 mb-3">
            Budget Preference
          </Text>
          <View className="flex-row space-x-3">
            {budgetOptions.map((option) => (
              <TouchableOpacity
                key={option.id}
                className={`flex-1 p-4 rounded-lg border items-center ${
                  preferences.budgetPreference === option.id
                    ? 'bg-blue-50 border-blue-300'
                    : 'bg-gray-50 border-gray-200'
                }`}
                onPress={() => setPreferences(prev => ({ ...prev, budgetPreference: option.id }))}
              >
                <Text className="text-2xl mb-2">{option.icon}</Text>
                <Text className="text-sm font-medium text-gray-800 text-center">
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Walking Distance */}
        <View className="mb-6">
          <Text className="text-lg font-semibold text-gray-800 mb-3">
            Maximum Walking Distance
          </Text>
          <View className="flex-row space-x-3">
            {[0.5, 1.0, 2.0].map((distance) => (
              <TouchableOpacity
                key={distance}
                className={`flex-1 p-3 rounded-lg border ${
                  preferences.maxWalkingDistance === distance
                    ? 'bg-blue-50 border-blue-300'
                    : 'bg-gray-50 border-gray-200'
                }`}
                onPress={() => setPreferences(prev => ({ ...prev, maxWalkingDistance: distance }))}
              >
                <Text className="text-center font-medium text-gray-800">
                  {distance} km
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Accessibility Needs */}
        <View className="mb-6">
          <Text className="text-lg font-semibold text-gray-800 mb-3">
            Accessibility Needs (Optional)
          </Text>
          <View className="space-y-2">
            {accessibilityOptions.map((option) => (
              <TouchableOpacity
                key={option.id}
                className="flex-row items-center justify-between p-3 bg-gray-50 rounded-lg"
                onPress={() => toggleAccessibility(option.id)}
              >
                <Text className="text-base text-gray-800">{option.label}</Text>
                <View className={`w-6 h-6 rounded border-2 ${
                  preferences.accessibility.includes(option.id)
                    ? 'bg-blue-600 border-blue-600'
                    : 'border-gray-300'
                }`}>
                  {preferences.accessibility.includes(option.id) && (
                    <Text className="text-white text-center text-xs">✓</Text>
                  )}
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Notification Preferences */}
        <View className="mb-8">
          <Text className="text-lg font-semibold text-gray-800 mb-3">
            Notifications
          </Text>
          <View className="space-y-3">
            <View className="flex-row items-center justify-between p-3 bg-gray-50 rounded-lg">
              <Text className="text-base text-gray-800">Delay alerts</Text>
              <Switch
                value={preferences.notifications.delays}
                onValueChange={() => updateNotification('delays')}
              />
            </View>
            <View className="flex-row items-center justify-between p-3 bg-gray-50 rounded-lg">
              <Text className="text-base text-gray-800">Fare offers & deals</Text>
              <Switch
                value={preferences.notifications.offers}
                onValueChange={() => updateNotification('offers')}
              />
            </View>
            <View className="flex-row items-center justify-between p-3 bg-gray-50 rounded-lg">
              <Text className="text-base text-gray-800">Journey reminders</Text>
              <Switch
                value={preferences.notifications.reminders}
                onValueChange={() => updateNotification('reminders')}
              />
            </View>
          </View>
        </View>

        {/* Save Button */}
        <TouchableOpacity
          className="bg-blue-600 rounded-lg py-4 mb-4"
          onPress={handleSavePreferences}
        >
          <Text className="text-white text-center text-lg font-semibold">
            Save Preferences & Continue
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          className="mb-6"
          onPress={() => router.replace('/(main)/(tabs)/home')}
        >
          <Text className="text-gray-500 text-center text-base">
            Skip for now
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}