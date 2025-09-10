import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../../src/contexts/AppContext';
import { useTheme } from '../../src/contexts/ThemeContext';

export default function Register() {
  const { register } = useAuth();
  const { theme, isDark } = useTheme();
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
    console.log(`Updating ${field} to ${value}`);
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <SafeAreaView className="flex-1" style={{ backgroundColor: theme.background }}>
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
              <Text className="text-3xl font-bold mb-3" style={{ color: theme.primary }}>
                Create Account
              </Text>
              <Text className="text-base text-center" style={{ color: theme.textSecondary }}>
                Join the smart transit revolution in Sri Lanka
              </Text>
            </View>

            {/* Registration Form */}
            <View className="w-full max-w-sm mx-auto">
              <View className="mb-4">
                <Text className="text-sm font-medium mb-2" style={{ color: theme.text }}>Full Name *</Text>
                <TextInput
                  className="border rounded-lg px-4 py-4 text-base"
                  style={{ 
                    borderColor: theme.border, 
                    backgroundColor: theme.surface,
                    color: theme.text 
                  }}
                  placeholder="Enter your full name"
                  placeholderTextColor={theme.textSecondary}
                  value={formData.name}
                  onChangeText={(value) => updateForm('name', value)}
                />
              </View>

              <View className="mb-4">
                <Text className="text-sm font-medium mb-2" style={{ color: theme.text }}>Email *</Text>
                <TextInput
                  className="border rounded-lg px-4 py-4 text-base"
                  style={{ 
                    borderColor: theme.border, 
                    backgroundColor: theme.surface,
                    color: theme.text 
                  }}
                  placeholder="Enter your email"
                  placeholderTextColor={theme.textSecondary}
                  value={formData.email}
                  onChangeText={(value) => updateForm('email', value)}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
              </View>

              <View className="mb-4">
                <Text className="text-sm font-medium mb-2" style={{ color: theme.text }}>Phone Number</Text>
                <TextInput
                  className="border rounded-lg px-4 py-4 text-base"
                  style={{ 
                    borderColor: theme.border, 
                    backgroundColor: theme.surface,
                    color: theme.text 
                  }}
                  placeholder="+94 771234567"
                  placeholderTextColor={theme.textSecondary}
                  value={formData.phone}
                  onChangeText={(value) => updateForm('phone', value)}
                  keyboardType="phone-pad"
                />
              </View>

          <View>
            <Text className="text-sm font-medium mb-2" style={{ color: theme.text }}>Password *</Text>
            <TextInput
              className="border rounded-lg px-4 py-3 text-base"
              style={{ 
                borderColor: theme.border, 
                backgroundColor: theme.surface,
                color: theme.text 
              }}
              placeholder="Create a password (min 6 characters)"
              placeholderTextColor={theme.textSecondary}
              value={formData.password}
              onChangeText={(value) => updateForm('password', value)}
              secureTextEntry
            />
          </View>

          <View>
            <Text className="text-sm font-medium mb-2" style={{ color: theme.text }}>Confirm Password *</Text>
            <TextInput
              className="border rounded-lg px-4 py-3 text-base"
              style={{ 
                borderColor: theme.border, 
                backgroundColor: theme.surface,
                color: theme.text 
              }}
              placeholder="Confirm your password"
              placeholderTextColor={theme.textSecondary}
              value={formData.confirmPassword}
              onChangeText={(value) => updateForm('confirmPassword', value)}
              secureTextEntry
            />
          </View>

          {/* Language Selection */}
          <View>
            <Text className="text-sm font-medium mb-3" style={{ color: theme.text }}>
              Preferred Language (Current: {formData.language})
            </Text>
            <View className="flex-row justify-between gap-3">
              {[
                { code: 'en', label: 'English' },
                { code: 'si', label: 'සිංහල' },
                { code: 'ta', label: 'தமிழ்' }
              ].map((lang) => (
                <TouchableOpacity
                  key={lang.code}
                  className="flex-1 py-3 px-3 rounded-lg border-2"
                  style={{
                    backgroundColor: formData.language === lang.code ? theme.primary : theme.surface,
                    borderColor: formData.language === lang.code ? theme.primary : theme.border,
                    elevation: formData.language === lang.code ? 2 : 0,
                    shadowColor: theme.primary,
                    shadowOffset: { width: 0, height: 1 },
                    shadowOpacity: formData.language === lang.code ? 0.3 : 0,
                    shadowRadius: 2
                  }}
                  onPress={() => updateForm('language', lang.code)}
                  activeOpacity={0.7}
                >
                  <Text 
                    className="text-center text-sm font-medium"
                    style={{
                      color: formData.language === lang.code ? 'white' : theme.text,
                      fontWeight: formData.language === lang.code ? '600' : '500'
                    }}
                  >
                    {lang.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <TouchableOpacity
            className={`rounded-lg py-3 mt-6 ${loading ? 'opacity-70' : ''}`}
            style={{ backgroundColor: theme.primary }}
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
            <Text className="text-center text-base" style={{ color: theme.primary }}>
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