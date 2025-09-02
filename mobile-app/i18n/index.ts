import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { storageService } from '@/services/storage';

// Import translations
import en from './locales/en.json';
import si from './locales/si.json';
import ta from './locales/ta.json';

const resources = {
  en: { translation: en },
  si: { translation: si },
  ta: { translation: ta },
};

const initI18n = async () => {
  const savedLanguage = await storageService.getLanguage();
  
  i18n
    .use(initReactI18next)
    .init({
      resources,
      lng: savedLanguage,
      fallbackLng: 'en',
      debug: __DEV__,
      
      interpolation: {
        escapeValue: false, // React already escapes values
      },
      
      react: {
        useSuspense: false, // Important for React Native
      },
    });
};

// Initialize i18n
initI18n();

export default i18n;