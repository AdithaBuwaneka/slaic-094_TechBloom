import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../../src/contexts/AppContext';

export default function Register() {
  const { register } = useAuth();
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
    // Prevent double submission
    if (loading) return;
    
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
      console.log('Registration attempt:', formData);
      
      // Prepare registration data for backend
      const registrationData = {
        name: formData.name,
        email: formData.email,
        password: formData.password,
        phone: formData.phone,
        preferred_language: formData.language
      };
      
      // Call the AppContext register function (which sets user state)
      console.log('Calling register with:', registrationData);
      const success = await register(registrationData);
      
      setLoading(false);
      
      if (success) {
        console.log('Registration successful');
        // Navigate to onboarding welcome page
        router.replace('/(onboarding)/welcome');
      } else {
        console.log('Registration failed');
        Alert.alert('Registration Failed', 'Please try again.');
      }
    } catch (error) {
      setLoading(false);
      console.error('Registration error:', error);
      Alert.alert('Error', 'Registration failed. Please check your connection and try again.');
    }
  };

  const updateForm = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1"
      >
        <ScrollView 
          className="flex-1"
          contentContainerStyle={{ flexGrow: 1 }}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View className="flex-1 justify-center px-6 py-8 min-h-full">
            {/* Header */}
            <View className="items-center mb-8">
              <Text className="text-3xl font-bold text-blue-600 mb-3">
                Create Account
              </Text>
              <Text className="text-base text-gray-600 text-center">
                Join the smart transit revolution in Sri Lanka
              </Text>
            </View>

            {/* Registration Form */}
            <View className="w-full max-w-sm mx-auto">
              <View className="mb-4">
                <Text className="text-sm font-medium text-gray-700 mb-2">Full Name *</Text>
                <TextInput
                  className="border border-gray-300 rounded-lg px-4 py-4 text-base bg-gray-50"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChangeText={(value) => updateForm('name', value)}
                />
              </View>

              <View className="mb-4">
                <Text className="text-sm font-medium text-gray-700 mb-2">Email *</Text>
                <TextInput
                  className="border border-gray-300 rounded-lg px-4 py-4 text-base bg-gray-50"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChangeText={(value) => updateForm('email', value)}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
              </View>

              <View className="mb-4">
                <Text className="text-sm font-medium text-gray-700 mb-2">Phone Number</Text>
                <TextInput
                  className="border border-gray-300 rounded-lg px-4 py-4 text-base bg-gray-50"
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
            onPress={() => router.push('/(auth)/login')}
          >
            <Text className="text-blue-600 text-center text-base">
              Already have an account? Sign In
            </Text>
          </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}