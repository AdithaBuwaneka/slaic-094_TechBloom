import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, ScrollView } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function Register() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    language: 'en'
  });
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!formData.name || !formData.email || !formData.password) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      // TODO: Implement API registration call
      console.log('Registration attempt:', formData);
      
      // Simulate successful registration
      setTimeout(() => {
        setLoading(false);
        router.replace('/(onboarding)/welcome');
      }, 1500);
    } catch (error) {
      setLoading(false);
      Alert.alert('Error', 'Registration failed. Please try again.');
    }
  };

  const updateForm = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <ScrollView className="flex-1 px-6 py-4">
        {/* Header */}
        <View className="items-center mb-6">
          <Text className="text-2xl font-bold text-blue-600 mb-2">
            Create Account
          </Text>
          <Text className="text-base text-gray-600 text-center">
            Join the smart transit revolution in Sri Lanka
          </Text>
        </View>

        {/* Registration Form */}
        <View className="space-y-4">
          <View>
            <Text className="text-sm font-medium text-gray-700 mb-2">Full Name *</Text>
            <TextInput
              className="border border-gray-300 rounded-lg px-4 py-3 text-base"
              placeholder="Enter your full name"
              value={formData.name}
              onChangeText={(value) => updateForm('name', value)}
            />
          </View>

          <View>
            <Text className="text-sm font-medium text-gray-700 mb-2">Email *</Text>
            <TextInput
              className="border border-gray-300 rounded-lg px-4 py-3 text-base"
              placeholder="Enter your email"
              value={formData.email}
              onChangeText={(value) => updateForm('email', value)}
              keyboardType="email-address"
              autoCapitalize="none"
            />
          </View>

          <View>
            <Text className="text-sm font-medium text-gray-700 mb-2">Phone Number</Text>
            <TextInput
              className="border border-gray-300 rounded-lg px-4 py-3 text-base"
              placeholder="+94 771234567"
              value={formData.phone}
              onChangeText={(value) => updateForm('phone', value)}
              keyboardType="phone-pad"
            />
          </View>

          <View>
            <Text className="text-sm font-medium text-gray-700 mb-2">Password *</Text>
            <TextInput
              className="border border-gray-300 rounded-lg px-4 py-3 text-base"
              placeholder="Create a password (min 6 characters)"
              value={formData.password}
              onChangeText={(value) => updateForm('password', value)}
              secureTextEntry
            />
          </View>

          <View>
            <Text className="text-sm font-medium text-gray-700 mb-2">Confirm Password *</Text>
            <TextInput
              className="border border-gray-300 rounded-lg px-4 py-3 text-base"
              placeholder="Confirm your password"
              value={formData.confirmPassword}
              onChangeText={(value) => updateForm('confirmPassword', value)}
              secureTextEntry
            />
          </View>

          {/* Language Selection */}
          <View>
            <Text className="text-sm font-medium text-gray-700 mb-3">Preferred Language</Text>
            <View className="flex-row space-x-3">
              {[
                { code: 'en', label: 'English' },
                { code: 'si', label: 'සිංහල' },
                { code: 'ta', label: 'தமிழ்' }
              ].map((lang) => (
                <TouchableOpacity
                  key={lang.code}
                  className={`flex-1 py-3 px-3 rounded-lg border ${
                    formData.language === lang.code 
                      ? 'bg-blue-600 border-blue-600' 
                      : 'bg-gray-100 border-gray-300'
                  }`}
                  onPress={() => updateForm('language', lang.code)}
                >
                  <Text className={`text-center text-sm ${
                    formData.language === lang.code ? 'text-white' : 'text-gray-700'
                  }`}>
                    {lang.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <TouchableOpacity
            className={`bg-blue-600 rounded-lg py-3 mt-6 ${loading ? 'opacity-70' : ''}`}
            onPress={handleRegister}
            disabled={loading}
          >
            <Text className="text-white text-center text-lg font-semibold">
              {loading ? 'Creating Account...' : 'Create Account'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            className="mt-4"
            onPress={() => router.back()}
          >
            <Text className="text-blue-600 text-center text-base">
              Already have an account? Sign In
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}