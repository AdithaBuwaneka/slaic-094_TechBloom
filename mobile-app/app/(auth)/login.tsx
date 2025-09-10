import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../../src/contexts/AppContext';
import { useTheme } from '../../src/contexts/ThemeContext';

export default function Login() {
  const { login } = useAuth();
  const { theme } = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const success = await login(email, password);
      
      if (success) {
        router.replace('/(main)/(tabs)/home');
      } else {
        Alert.alert('Error', 'Invalid credentials. Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Login failed. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView className="flex-1" style={{ backgroundColor: theme.background }}>
      <View className="flex-1 justify-center px-6">
        {/* Header */}
        <View className="items-center mb-8">
          <Text className="text-3xl font-bold mb-2" style={{ color: theme.primary }}>
            Transit Companion
          </Text>
          <Text className="text-lg text-center" style={{ color: theme.textSecondary }}>
            Your AI-powered travel assistant for Sri Lanka
          </Text>
        </View>

        {/* Login Form */}
        <View className="space-y-4">
          <View>
            <Text className="text-sm font-medium mb-2" style={{ color: theme.textSecondary }}>Email</Text>
            <TextInput
              className="border rounded-lg px-4 py-3 text-base"
              style={{ 
                borderColor: theme.border, 
                backgroundColor: theme.surface,
                color: theme.text 
              }}
              placeholder="Enter your email"
              placeholderTextColor={theme.textTertiary}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
            />
          </View>

          <View>
            <Text className="text-sm font-medium mb-2" style={{ color: theme.textSecondary }}>Password</Text>
            <TextInput
              className="border rounded-lg px-4 py-3 text-base"
              style={{ 
                borderColor: theme.border, 
                backgroundColor: theme.surface,
                color: theme.text 
              }}
              placeholder="Enter your password"
              placeholderTextColor={theme.textTertiary}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />
          </View>

          <TouchableOpacity
            className={`rounded-lg py-3 mt-6 ${loading ? 'opacity-70' : ''}`}
            style={{ backgroundColor: theme.primary }}
            onPress={handleLogin}
            disabled={loading}
          >
            <Text className="text-white text-center text-lg font-semibold">
              {loading ? 'Signing In...' : 'Sign In'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            className="mt-4"
            onPress={() => router.push('/(auth)/register')}
          >
            <Text className="text-center text-base" style={{ color: theme.primary }}>
              Don't have an account? Sign Up
            </Text>
          </TouchableOpacity>
        </View>

        {/* Language Selection */}
        <View className="mt-8">
          <Text className="text-sm text-gray-600 text-center mb-3">Choose Language</Text>
          <View className="flex-row justify-center space-x-4">
            <TouchableOpacity className="bg-gray-100 px-4 py-2 rounded-lg">
              <Text className="text-gray-700">English</Text>
            </TouchableOpacity>
            <TouchableOpacity className="bg-gray-100 px-4 py-2 rounded-lg">
              <Text className="text-gray-700">සිංහල</Text>
            </TouchableOpacity>
            <TouchableOpacity className="bg-gray-100 px-4 py-2 rounded-lg">
              <Text className="text-gray-700">தமிழ்</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}