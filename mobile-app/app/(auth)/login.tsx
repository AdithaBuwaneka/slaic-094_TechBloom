import { useState, useEffect } from 'react';
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
import { biometricService } from '@/services/biometric';

export default function LoginScreen() {
  const router = useRouter();
  const { t } = useTranslation();
  const { login, isLoading } = useApp();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [biometricAvailable, setBiometricAvailable] = useState(false);

  useEffect(() => {
    checkBiometricAvailability();
  }, []);

  const checkBiometricAvailability = async () => {
    const available = await biometricService.isBiometricLoginEnabled();
    setBiometricAvailable(available);
  };

  const handleBiometricLogin = async () => {
    try {
      const result = await biometricService.quickLogin();
      if (result.success) {
        // Biometric authentication successful, navigate to app
        router.replace('/home');
      } else {
        Alert.alert('Authentication Failed', result.error || 'Biometric authentication failed');
      }
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Biometric authentication error');
    }
  };

  const handleLogin = async () => {
    if (isLoading) {
      return; // Prevent multiple simultaneous login attempts
    }

    if (!email.trim() || !password.trim()) {
      Alert.alert(t('common.error'), 'Please fill in all fields');
      return;
    }

    try {
      await login(email.trim(), password);
      console.log('🎉 Login successful - navigating to home');
      router.replace('/(tabs)/home');
    } catch (error: any) {
      Alert.alert(t('common.error'), error.message || t('auth.invalidCredentials'));
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
                {t('auth.welcome')}
              </Text>
              <Text className="text-gray-600 text-center">
                Sign in to continue your journey
              </Text>
            </View>
          </View>

          {/* Form */}
          <View className="px-6 space-y-6">
            {/* Email Input */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-2">
                {t('auth.email')}
              </Text>
              <View className="bg-gray-50 rounded-xl px-4 py-3 border border-gray-200">
                <TextInput
                  value={email}
                  onChangeText={setEmail}
                  placeholder="Enter your email"
                  placeholderTextColor="#9ca3af"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  className="text-base text-gray-900"
                />
              </View>
            </View>

            {/* Password Input */}
            <View>
              <Text className="text-sm font-medium text-gray-700 mb-2">
                {t('auth.password')}
              </Text>
              <View className="bg-gray-50 rounded-xl px-4 py-3 border border-gray-200 flex-row items-center">
                <TextInput
                  value={password}
                  onChangeText={setPassword}
                  placeholder="Enter your password"
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

            {/* Forgot Password */}
            <TouchableOpacity className="self-end">
              <Text className="text-blue-600 font-medium">
                {t('auth.forgotPassword')}
              </Text>
            </TouchableOpacity>

            {/* Biometric Login Button */}
            {biometricAvailable && (
              <TouchableOpacity
                onPress={handleBiometricLogin}
                className="bg-saffron-500 rounded-xl py-4 px-8 mb-4"
              >
                <View className="flex-row items-center justify-center">
                  <Ionicons name="finger-print" size={20} color="white" className="mr-2" />
                  <Text className="text-white font-semibold text-lg ml-2">
                    Use Biometric
                  </Text>
                </View>
              </TouchableOpacity>
            )}

            {/* Login Button */}
            <TouchableOpacity
              onPress={handleLogin}
              disabled={isLoading}
              className={`bg-blue-600 rounded-xl py-4 px-8 ${
                isLoading ? 'opacity-70' : ''
              }`}
            >
              <Text className="text-white font-semibold text-lg text-center">
                {isLoading ? t('common.loading') : t('auth.signIn')}
              </Text>
            </TouchableOpacity>

            {/* Sign Up Link */}
            <View className="flex-row justify-center items-center space-x-2 pt-8">
              <Text className="text-gray-600">
                {t('auth.dontHaveAccount')}
              </Text>
              <TouchableOpacity onPress={() => router.push('/register')}>
                <Text className="text-blue-600 font-semibold">
                  {t('auth.signUp')}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}