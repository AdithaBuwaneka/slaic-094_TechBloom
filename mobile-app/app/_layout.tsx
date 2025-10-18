import 'react-native-reanimated';
import 'react-native-gesture-handler';
import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { ThemeProvider } from '../src/contexts/ThemeContext';
import { AppProvider } from '../src/contexts/AppContext';
import { LanguageProvider } from '../src/contexts/LanguageContext';
import './global.css';

export default function RootLayout() {
  return (
    <LanguageProvider>
      <ThemeProvider>
        <AppProvider>
          <StatusBar style="light" />
          <Stack screenOptions={{ headerShown: false }}>
            <Stack.Screen name="index" />
            <Stack.Screen name="(auth)" />
            <Stack.Screen name="(onboarding)" />
            <Stack.Screen name="(main)" />
          </Stack>
        </AppProvider>
      </ThemeProvider>
    </LanguageProvider>
  );
}