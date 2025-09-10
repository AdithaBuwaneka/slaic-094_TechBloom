import React from 'react';
import { Stack } from "expo-router";
import { StatusBar } from 'expo-status-bar';
import { ThemeProvider } from '../src/contexts/ThemeContext';
import { AppProvider } from '../src/contexts/AppContext';
import './global.css';

export default function RootLayout() {
  return (
    <ThemeProvider>
      <AppProvider>
        <StatusBar style="auto" />
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="(onboarding)" />
          <Stack.Screen name="(main)" />
        </Stack>
      </AppProvider>
    </ThemeProvider>
  );
}