import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  ScrollView,
  Platform,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';

export default function RegisterScreen() {
  const router = useRouter();
  const { t } = useTranslation();
  const { register, isLoading, language } = useApp();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    phone: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const validateForm = () => {
    // Check required fields
    if (!formData.email.trim() || !formData.password || !formData.fullName.trim()) {
      Alert.alert(t('common.error'), 'Please fill in all required fields');
      return false;
    }

    // Validate full name (at least 2 characters, no numbers)
    if (formData.fullName.trim().length < 2) {
      Alert.alert(t('common.error'), 'Full name must be at least 2 characters');
      return false;
    }

    // Enhanced email validation
    const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
    if (!emailRegex.test(formData.email.trim())) {
      Alert.alert(t('common.error'), 'Please enter a valid email address');
      return false;
    }

    // Enhanced password validation
    if (formData.password.length < 8) {
      Alert.alert(t('common.error'), 'Password must be at least 8 characters');
      return false;
    }

    // Check password strength
    const hasUpperCase = /[A-Z]/.test(formData.password);
    const hasLowerCase = /[a-z]/.test(formData.password);
    const hasNumbers = /\d/.test(formData.password);
    
    if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
      Alert.alert(
        t('common.error'), 
        'Password must contain at least one uppercase letter, one lowercase letter, and one number'
      );
      return false;
    }

    // Check password confirmation
    if (formData.password !== formData.confirmPassword) {
      Alert.alert(t('common.error'), 'Passwords do not match');
      return false;
    }

    // Validate phone number if provided
    if (formData.phone.trim()) {
      const phoneRegex = /^[+]?[\d\s\-()]{7,15}$/;
      if (!phoneRegex.test(formData.phone.trim())) {
        Alert.alert(t('common.error'), 'Please enter a valid phone number');
        return false;
      }
    }

    return true;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    try {
      await register({
        email: formData.email.trim(),
        password: formData.password,
        full_name: formData.fullName.trim(),
        phone: formData.phone.trim() ? formData.phone.replace(/[\s\-()]/g, '') : undefined,
        preferred_language: language,
        device_type: 'android', // Explicitly set device type
      });
      
      // Clear form on successful registration
      setFormData({
        email: '',
        password: '',
        confirmPassword: '',
        fullName: '',
        phone: '',
      });
      
      // Navigation is handled by the app context
    } catch (error: any) {
      console.error('Registration error:', error);
      
      // Handle specific error messages
      let errorMessage = 'Registration failed';
      if (error.message) {
        if (error.message.includes('already registered') || error.message.includes('already exists')) {
          errorMessage = 'This email is already registered. Please use a different email or try logging in.';
        } else if (error.message.includes('network') || error.message.includes('connection')) {
          errorMessage = 'Network error. Please check your internet connection and try again.';
        } else if (error.message.includes('validation') || error.message.includes('invalid')) {
          errorMessage = 'Please check your information and try again.';
        } else {
          errorMessage = error.message;
        }
      }
      
      Alert.alert(t('common.error'), errorMessage);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1"
      >
        <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
          {/* Header */}
          <View className="px-6 pt-8">
            <TouchableOpacity
              onPress={() => router.back()}
              className="w-10 h-10 rounded-full bg-gray-100 items-center justify-center mb-8"
            >
              <Ionicons name="arrow-back" size={20} color="#374151" />
            </TouchableOpacity>

            <View className="items-center mb-12">
              <View className="w-16 h-16 bg-blue-600 rounded-full items-center justify-center mb-4">
                <Text className="text-2xl text-white">🚌</Text>
              </View>
              <Text className="text-3xl font-bold text-gray-900 mb-2">
                Create Account
              </Text>
              <Text className="text-gray-600 text-center">
                Join thousands of smart commuters
              </Text>
            </View>
          </View>

          {/* Form */}
          <View className="px-6 space-y-4">
            {/* Full Name Input */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-2">
                {t('auth.fullName')} *
              </Text>
              <View className="bg-gray-50 rounded-xl px-4 py-3 border border-gray-200">
                <TextInput
                  value={formData.fullName}
                  onChangeText={(value) => updateField('fullName', value)}
                  placeholder="Enter your full name"
                  placeholderTextColor="#9ca3af"
                  autoCapitalize="words"
                  className="text-base text-gray-900"
                />
              </View>
            </View>

            {/* Email Input */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-2">
                {t('auth.email')} *
              </Text>
              <View className="bg-gray-50 rounded-xl px-4 py-3 border border-gray-200">
                <TextInput
                  value={formData.email}
                  onChangeText={(value) => updateField('email', value)}
                  placeholder="Enter your email"
                  placeholderTextColor="#9ca3af"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  className="text-base text-gray-900"
                />
              </View>
            </View>

            {/* Phone Input */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-2">
                {t('auth.phone')} (Optional)
              </Text>
              <View className="bg-gray-50 rounded-xl px-4 py-3 border border-gray-200">
                <TextInput
                  value={formData.phone}
                  onChangeText={(value) => updateField('phone', value)}
                  placeholder="Enter your phone number"
                  placeholderTextColor="#9ca3af"
                  keyboardType="phone-pad"
                  className="text-base text-gray-900"
                />
              </View>
            </View>

            {/* Password Input */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-2">
                {t('auth.password')} *
              </Text>
              <View className="bg-gray-50 rounded-xl px-4 py-3 border border-gray-200 flex-row items-center">
                <TextInput
                  value={formData.password}
                  onChangeText={(value) => updateField('password', value)}
                  placeholder="Password (8+ chars, A-z, 0-9)"
                  placeholderTextColor="#9ca3af"
                  secureTextEntry={!showPassword}
                  className="flex-1 text-base text-gray-900"
                />
                <TouchableOpacity
                  onPress={() => setShowPassword(!showPassword)}
                  className="p-1"
                >
                  <Ionicons
                    name={showPassword ? 'eye-off' : 'eye'}
                    size={20}
                    color="#6b7280"
                  />
                </TouchableOpacity>
              </View>
            </View>

            {/* Confirm Password Input */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-2">
                {t('auth.confirmPassword')} *
              </Text>
              <View className="bg-gray-50 rounded-xl px-4 py-3 border border-gray-200 flex-row items-center">
                <TextInput
                  value={formData.confirmPassword}
                  onChangeText={(value) => updateField('confirmPassword', value)}
                  placeholder="Confirm your password"
                  placeholderTextColor="#9ca3af"
                  secureTextEntry={!showConfirmPassword}
                  className="flex-1 text-base text-gray-900"
                />
                <TouchableOpacity
                  onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="p-1"
                >
                  <Ionicons
                    name={showConfirmPassword ? 'eye-off' : 'eye'}
                    size={20}
                    color="#6b7280"
                  />
                </TouchableOpacity>
              </View>
            </View>

            {/* Register Button */}
            <TouchableOpacity
              onPress={handleRegister}
              disabled={isLoading}
              className={`bg-blue-600 rounded-xl py-4 px-8 mt-6 ${
                isLoading ? 'opacity-70' : ''
              }`}
            >
              <Text className="text-white font-semibold text-lg text-center">
                {isLoading ? t('common.loading') : t('auth.signUp')}
              </Text>
            </TouchableOpacity>

            {/* Sign In Link */}
            <View className="flex-row justify-center items-center space-x-2 pt-8 pb-8">
              <Text className="text-gray-600">
                {t('auth.alreadyHaveAccount')}
              </Text>
              <TouchableOpacity onPress={() => router.push('/login')}>
                <Text className="text-blue-600 font-semibold">
                  {t('auth.signIn')}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}