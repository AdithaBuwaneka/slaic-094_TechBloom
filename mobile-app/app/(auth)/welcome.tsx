import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useApp } from '@/context/AppContext';

export default function WelcomeScreen() {
  const router = useRouter();
  const { t } = useTranslation();
  const { language, changeLanguage } = useApp();

  return (
    <LinearGradient
      colors={['#1e40af', '#3b82f6', '#60a5fa']}
      className="flex-1"
    >
      <SafeAreaView className="flex-1 justify-center items-center px-6">
        {/* Logo/Icon Area */}
        <View className="items-center mb-12">
          <View className="w-24 h-24 bg-white/20 rounded-full items-center justify-center mb-4">
            <Text className="text-4xl text-white">🚌</Text>
          </View>
          <Text className="text-3xl font-bold text-white text-center mb-2">
            Smart Transit
          </Text>
          <Text className="text-xl font-semibold text-blue-100 text-center">
            Companion
          </Text>
        </View>

        {/* Welcome Message */}
        <View className="items-center mb-16">
          <Text className="text-lg text-white/90 text-center leading-6">
            {t('auth.welcome')}
          </Text>
          <Text className="text-base text-blue-100 text-center mt-2 leading-5">
            Your AI-powered journey planner for Sri Lanka
          </Text>
        </View>

        {/* Action Buttons */}
        <View className="w-full space-y-4">
          <TouchableOpacity
            onPress={() => router.push('/login')}
            className="bg-white rounded-xl py-4 px-8 w-full"
          >
            <Text className="text-blue-600 font-semibold text-lg text-center">
              {t('auth.login')}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => router.push('/register')}
            className="bg-white/10 border border-white/30 rounded-xl py-4 px-8 w-full"
          >
            <Text className="text-white font-semibold text-lg text-center">
              {t('auth.register')}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Language Selection */}
        <View className="flex-row space-x-4 mt-12">
          <TouchableOpacity 
            onPress={() => changeLanguage('en')}
            className={`px-4 py-2 rounded-full ${language === 'en' ? 'bg-white/30' : 'bg-white/10'}`}
          >
            <Text className="text-white font-medium">English</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            onPress={() => changeLanguage('si')}
            className={`px-4 py-2 rounded-full ${language === 'si' ? 'bg-white/30' : 'bg-white/10'}`}
          >
            <Text className="text-white font-medium">සිංහල</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            onPress={() => changeLanguage('ta')}
            className={`px-4 py-2 rounded-full ${language === 'ta' ? 'bg-white/30' : 'bg-white/10'}`}
          >
            <Text className="text-white font-medium">தமிழ்</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}