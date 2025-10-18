// app.config.js - Expo configuration with environment variable support
require('dotenv').config();

module.exports = {
  expo: {
    name: 'transit-companion-mobile',
    slug: 'transit-companion-mobile',
    version: '1.0.0',
    orientation: 'portrait',
    icon: './assets/images/icon.png',
    scheme: 'transitcompanion',
    userInterfaceStyle: 'automatic',
    splash: {
      image: './assets/images/splash.png',
      resizeMode: 'contain',
      backgroundColor: '#ffffff'
    },
    assetBundlePatterns: [
      '**/*'
    ],
    ios: {
      supportsTablet: true,
      bundleIdentifier: 'com.transitcompanion.mobile'
    },
    android: {
      adaptiveIcon: {
        foregroundImage: './assets/images/adaptive-icon.png',
        backgroundColor: '#ffffff'
      },
      package: 'com.transitcompanion.mobile'
    },
    web: {
      bundler: 'metro',
      output: 'static',
      favicon: './assets/images/favicon.png'
    },
    plugins: [
      'expo-router'
    ],
    experiments: {
      typedRoutes: true
    },
    // Expose environment variables to the app
    extra: {
      EXPO_PUBLIC_API_HOST: process.env.EXPO_PUBLIC_API_HOST || '10.0.2.2',
      EXPO_PUBLIC_API_PORT: process.env.EXPO_PUBLIC_API_PORT || '8000',
      EXPO_PUBLIC_API_PROTOCOL: process.env.EXPO_PUBLIC_API_PROTOCOL || 'http',
      EXPO_PUBLIC_WS_PROTOCOL: process.env.EXPO_PUBLIC_WS_PROTOCOL || 'ws',
      EXPO_PUBLIC_PRODUCTION_API_URL: process.env.EXPO_PUBLIC_PRODUCTION_API_URL || 'https://your-production-domain.com',
    }
  }
};
