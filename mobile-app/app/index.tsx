
import { useEffect } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useApp } from '@/context/AppContext';

export default function Index() {
  const router = useRouter();
  const { isLoading, isAuthenticated } = useApp();

  useEffect(() => {
    console.log('🚦 Navigation check:', { isLoading, isAuthenticated });
    if (!isLoading) {
      // Navigate based on authentication status
      if (isAuthenticated) {
        console.log('✅ Redirecting to /(tabs)/home');
        router.replace('/(tabs)/home');
      } else {
        console.log('➡️ Redirecting to /(auth)/welcome');
        router.replace('/(auth)/welcome');
      }
    }
  }, [isLoading, isAuthenticated, router]);

  // Show loading screen while initializing
  return (
    <View className="flex-1 justify-center items-center bg-blue-600">
      <ActivityIndicator size="large" color="#ffffff" />
    </View>
  );
}
