// =============================================================================
// LANGUAGE CONTEXT - Internationalization (i18n) Management
// =============================================================================

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type SupportedLanguage = 'en' | 'si' | 'ta';

interface LanguageContextType {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => Promise<void>;
  t: (key: string, params?: Record<string, string>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const LANGUAGE_STORAGE_KEY = '@transit_companion_language';

interface LanguageProviderProps {
  children: ReactNode;
}

// Translation strings
const translations = {
  en: {
    // Authentication
    'auth.login.title': 'Welcome Back',
    'auth.login.subtitle': 'Sign in to your Transit Companion account',
    'auth.login.email': 'Email',
    'auth.login.password': 'Password',
    'auth.login.button': 'Sign In',
    'auth.login.register': 'Don\'t have an account? Sign Up',
    'auth.register.title': 'Create Account',
    'auth.register.subtitle': 'Join the smart transit revolution in Sri Lanka',
    'auth.register.name': 'Full Name *',
    'auth.register.email': 'Email *',
    'auth.register.phone': 'Phone Number',
    'auth.register.password': 'Password *',
    'auth.register.confirmPassword': 'Confirm Password *',
    'auth.register.language': 'Preferred Language',
    'auth.register.button': 'Create Account',
    'auth.register.login': 'Already have an account? Sign In',
    
    // Navigation
    'nav.home': 'Home',
    'nav.routes': 'Routes',
    'nav.community': 'Community',
    'nav.chat': 'Assistant',
    'nav.profile': 'Profile',
    
    // Home Screen
    'home.title': 'Smart Transit',
    'home.subtitle': 'AI-powered journey planning for Sri Lanka',
    'home.from': 'From',
    'home.to': 'To',
    'home.planRoute': 'Plan Route',
    
    // Profile Screen
    'profile.title': 'Profile',
    'profile.impact': 'Your Impact',
    'profile.trips': 'Total Trips',
    'profile.distance': 'km Traveled',
    'profile.saved': 'Money Saved',
    'profile.carbon': 'kg CO₂ Reduced',
    'profile.appearance': 'Appearance',
    'profile.language': 'Language / භාෂාව / மொழி',
    'profile.notifications': 'Notifications',
    'profile.privacy': 'Privacy & Data',
    'profile.logout': 'Logout',
    
    // Community Screen
    'community.title': 'Community Reports',
    'community.subtitle': 'Share and discover real-time transport updates',
    'community.reports': 'Latest Reports',
    'community.create': 'Report Issue',
    'community.impact': 'Community Impact',
    'community.activeReports': 'Active Reports',
    'community.totalVotes': 'Total Votes',
    
    // Chat Screen
    'chat.title': 'AI Travel Assistant',
    'chat.subtitle': 'Online - RAG-Enhanced AI Assistant',
    'chat.thinking': 'AI is thinking...',
    'chat.placeholder': 'Ask about routes, fares, schedules...',
    
    // Routes Screen
    'routes.title': 'My Routes',
    'routes.subtitle': 'AI-powered route planning results',
    'routes.recent': 'Recent Route Options',
    'routes.loading': 'Loading recent routes...',
    'routes.noRoutes': 'No routes planned yet',
    
    // Common
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.cancel': 'Cancel',
    'common.ok': 'OK',
    'common.save': 'Save',
    'common.close': 'Close',
  },
  
  si: {
    // Authentication
    'auth.login.title': 'ආයෙත් සාදරයෙන්',
    'auth.login.subtitle': 'ට්‍රාන්සිට් කම්පැනියන් ගිණුමට පිවිසෙන්න',
    'auth.login.email': 'ඊමේල්',
    'auth.login.password': 'මුරපදය',
    'auth.login.button': 'පිවිසෙන්න',
    'auth.login.register': 'ගිණුමක් නැද්ද? ලියාපදිංචි වන්න',
    'auth.register.title': 'ගිණුමක් සාදන්න',
    'auth.register.subtitle': 'ශ්‍රී ලංකාවේ බුද්ධිමත් ප්‍රවාහන විප්ලවයට සම්බන්ධ වන්න',
    'auth.register.name': 'සම්පූර්ණ නම *',
    'auth.register.email': 'ඊමේල් *',
    'auth.register.phone': 'දුරකථන අංකය',
    'auth.register.password': 'මුරපදය *',
    'auth.register.confirmPassword': 'මුරපදය තහවුරු කරන්න *',
    'auth.register.language': 'කැමති භාෂාව',
    'auth.register.button': 'ගිණුම සාදන්න',
    'auth.register.login': 'දැනටම ගිණුමක් තිබේද? පිවිසෙන්න',
    
    // Navigation
    'nav.home': 'මුල් පිටුව',
    'nav.routes': 'මාර්ග',
    'nav.community': 'ප්‍රජාව',
    'nav.chat': 'සහායක',
    'nav.profile': 'පැතිකඩ',
    
    // Home Screen
    'home.title': 'බුද්ධිමත් ප්‍රවාහනය',
    'home.subtitle': 'ශ්‍රී ලංකාව සඳහා AI-බලගත ගමන් සැලසුම්',
    'home.from': 'සිට',
    'home.to': 'දක්වා',
    'home.planRoute': 'මාර්ගය සැලසුම් කරන්න',
    
    // Profile Screen
    'profile.title': 'පැතිකඩ',
    'profile.impact': 'ඔබේ බලපෑම',
    'profile.trips': 'මුළු ගමන්',
    'profile.distance': 'කි.මී. ගමන්',
    'profile.saved': 'ඉතිරි කළ මුදල්',
    'profile.carbon': 'කි.ග්‍රෑ CO₂ අඩු කළා',
    'profile.appearance': 'පෙනුම',
    'profile.language': 'Language / භාෂාව / மொழி',
    'profile.notifications': 'දැනුම්දීම්',
    'profile.privacy': 'රහස්‍යතාව සහ දත්ත',
    'profile.logout': 'ඉවත්වන්න',
    
    // Community Screen
    'community.title': 'ප්‍රජා වාර්තා',
    'community.subtitle': 'තත්‍ය කාලීන ප්‍රවාහන යාවත්කාලීන බෙදාගෙන සොයාගන්න',
    'community.reports': 'නවතම වාර්තා',
    'community.create': 'ගැටලුවක් වාර්තා කරන්න',
    'community.impact': 'ප්‍රජා බලපෑම',
    'community.activeReports': 'සක්‍රිය වාර්තා',
    'community.totalVotes': 'මුළු ඡන්ද',
    
    // Chat Screen
    'chat.title': 'AI ගමන් සහායක',
    'chat.subtitle': 'සබැඳි - RAG-උන්නත AI සහායක',
    'chat.thinking': 'AI සිතමින්...',
    'chat.placeholder': 'මාර්ග, ගාස්තු, කාලසටහන් ගැන අහන්න...',
    
    // Routes Screen
    'routes.title': 'මගේ මාර්ග',
    'routes.subtitle': 'AI-බලගත මාර්ග සැලසුම් ප්‍රතිඵල',
    'routes.recent': 'මෑත මාර්ග විකල්ප',
    'routes.loading': 'මෑත මාර්ග පූරණය වෙමින්...',
    'routes.noRoutes': 'තවම මාර්ග සැලසුම් කර නැත',
    
    // Common
    'common.loading': 'පූරණය වෙමින්...',
    'common.error': 'දෝෂය',
    'common.success': 'සාර්ථකයි',
    'common.cancel': 'අවලංගු කරන්න',
    'common.ok': 'හරි',
    'common.save': 'සුරකින්න',
    'common.close': 'වසන්න',
  },
  
  ta: {
    // Authentication
    'auth.login.title': 'மீண்டும் வரவேற்கிறோம்',
    'auth.login.subtitle': 'உங்கள் டிராண்சிட் கம்பானியன் கணக்கில் உள்நுழையவும்',
    'auth.login.email': 'மின்னஞ்சல்',
    'auth.login.password': 'கடவுச்சொல்',
    'auth.login.button': 'உள்நுழையவும்',
    'auth.login.register': 'கணக்கு இல்லையா? பதிவு செய்யவும்',
    'auth.register.title': 'கணக்கை உருவாக்கவும்',
    'auth.register.subtitle': 'இலங்கையின் ஸ்மார்ட் போக்குவரத்து புரட்சியில் சேரவும்',
    'auth.register.name': 'முழு பெயர் *',
    'auth.register.email': 'மின்னஞ்சல் *',
    'auth.register.phone': 'தொலைபேசி எண்',
    'auth.register.password': 'கடவுச்சொல் *',
    'auth.register.confirmPassword': 'கடவுச்சொல்லை உறுதிப்படுத்தவும் *',
    'auth.register.language': 'விருப்பமான மொழி',
    'auth.register.button': 'கணக்கை உருவாக்கவும்',
    'auth.register.login': 'ஏற்கனவே கணக்கு உள்ளதா? உள்நுழையவும்',
    
    // Navigation
    'nav.home': 'முகப்பு',
    'nav.routes': 'வழிகள்',
    'nav.community': 'சமூகம்',
    'nav.chat': 'உதவியாளர்',
    'nav.profile': 'விவரம்',
    
    // Home Screen
    'home.title': 'ஸ்மார்ட் போக்குவரத்து',
    'home.subtitle': 'இலங்கைக்கான AI-சக்தி பயண திட்டமிடல்',
    'home.from': 'இருந்து',
    'home.to': 'வரை',
    'home.planRoute': 'வழித்தடத்தைத் திட்டமிடவும்',
    
    // Profile Screen
    'profile.title': 'விவரம்',
    'profile.impact': 'உங்கள் தாக்கம்',
    'profile.trips': 'மொத்த பயணங்கள்',
    'profile.distance': 'கி.மீ. பயணித்தது',
    'profile.saved': 'சேமித்த பணம்',
    'profile.carbon': 'கி.கி CO₂ குறைக்கப்பட்டது',
    'profile.appearance': 'தோற்றம்',
    'profile.language': 'Language / භාෂාව / மொழி',
    'profile.notifications': 'அறிவிப்புகள்',
    'profile.privacy': 'தனியுரிமை & தரவு',
    'profile.logout': 'வெளியேறு',
    
    // Community Screen
    'community.title': 'சமூக அறிக்கைகள்',
    'community.subtitle': 'நிகழ்நேர போக்குவரத்து புதுப்பிப்புகளைப் பகிரவும் கண்டறியவும்',
    'community.reports': 'சமீபத்திய அறிக்கைகள்',
    'community.create': 'பிரச்சினையை அறிவிக்கவும்',
    'community.impact': 'சமூக தாக்கம்',
    'community.activeReports': 'செயலில் உள்ள அறிக்கைகள்',
    'community.totalVotes': 'மொத்த வாக்குகள்',
    
    // Chat Screen
    'chat.title': 'AI பயண உதவியாளர்',
    'chat.subtitle': 'ஆன்லைன் - RAG-மேம்பட்ட AI உதவியாளர்',
    'chat.thinking': 'AI சிந்தித்துக் கொண்டிருக்கிறது...',
    'chat.placeholder': 'வழிகள், கட்டணங்கள், அட்டவணைகளைப் பற்றி கேளுங்கள்...',
    
    // Routes Screen
    'routes.title': 'எனது வழிகள்',
    'routes.subtitle': 'AI-சக்தி வழித்தட திட்டமிடல் முடிவுகள்',
    'routes.recent': 'சமீபத்திய வழித்தட விருப்பங்கள்',
    'routes.loading': 'சமீபத்திய வழிகள் ஏற்றப்படுகின்றன...',
    'routes.noRoutes': 'இதுவரை வழிகள் திட்டமிடப்படவில்லை',
    
    // Common
    'common.loading': 'ஏற்றப்படுகிறது...',
    'common.error': 'பிழை',
    'common.success': 'வெற்றி',
    'common.cancel': 'ரத்து செய்',
    'common.ok': 'சரி',
    'common.save': 'சேமிக்கவும்',
    'common.close': 'மூடு',
  }
};

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [language, setLanguageState] = useState<SupportedLanguage>('en');

  // Load saved language preference on app start
  useEffect(() => {
    loadLanguagePreference();
  }, []);

  const loadLanguagePreference = async () => {
    try {
      const savedLanguage = await AsyncStorage.getItem(LANGUAGE_STORAGE_KEY);
      if (savedLanguage && ['en', 'si', 'ta'].includes(savedLanguage)) {
        setLanguageState(savedLanguage as SupportedLanguage);
      }
    } catch (error) {
      console.error('Error loading language preference:', error);
    }
  };

  const setLanguage = async (newLanguage: SupportedLanguage) => {
    try {
      setLanguageState(newLanguage);
      await AsyncStorage.setItem(LANGUAGE_STORAGE_KEY, newLanguage);
      console.log('Language changed to:', newLanguage);
    } catch (error) {
      console.error('Error saving language preference:', error);
    }
  };

  const t = (key: string, params?: Record<string, string>): string => {
    let text = translations[language][key] || key;
    
    // Replace parameters if provided
    if (params) {
      Object.keys(params).forEach(param => {
        text = text.replace(`{{${param}}}`, params[param]);
      });
    }
    
    return text;
  };

  const value: LanguageContextType = {
    language,
    setLanguage,
    t,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

export default LanguageProvider;