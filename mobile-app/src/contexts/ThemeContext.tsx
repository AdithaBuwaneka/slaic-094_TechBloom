// =============================================================================
// THEME CONTEXT - Dark/Light Mode Management
// =============================================================================

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Appearance, ColorSchemeName } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type ThemeMode = 'light' | 'dark' | 'auto';

interface ThemeColors {
  // Background colors
  background: string;
  surface: string;
  card: string;
  
  // Text colors
  text: string;
  textSecondary: string;
  textTertiary: string;
  
  // Primary colors
  primary: string;
  primaryLight: string;
  primaryDark: string;
  
  // Status colors
  success: string;
  warning: string;
  error: string;
  info: string;
  
  // Border and divider colors
  border: string;
  divider: string;
  
  // Interactive colors
  ripple: string;
  overlay: string;
  
  // Transit mode specific colors
  bus: string;
  train: string;
  tukTuk: string;
  uber: string;
  walking: string;
  driving: string;
}

const lightTheme: ThemeColors = {
  background: '#F9FAFB',
  surface: '#FFFFFF',
  card: '#FFFFFF',
  
  text: '#111827',
  textSecondary: '#4B5563',
  textTertiary: '#9CA3AF',
  
  primary: '#2563EB',
  primaryLight: '#3B82F6',
  primaryDark: '#1D4ED8',
  
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#06B6D4',
  
  border: '#E5E7EB',
  divider: '#F3F4F6',
  
  ripple: '#E5E7EB',
  overlay: 'rgba(0,0,0,0.5)',
  
  bus: '#EF4444',
  train: '#3B82F6',
  tukTuk: '#F59E0B',
  uber: '#10B981',
  walking: '#6B7280',
  driving: '#8B5CF6',
};

const darkTheme: ThemeColors = {
  background: '#0F172A',
  surface: '#1E293B',
  card: '#334155',
  
  text: '#F8FAFC',
  textSecondary: '#CBD5E1',
  textTertiary: '#64748B',
  
  primary: '#3B82F6',
  primaryLight: '#60A5FA',
  primaryDark: '#2563EB',
  
  success: '#34D399',
  warning: '#FBBF24',
  error: '#F87171',
  info: '#22D3EE',
  
  border: '#475569',
  divider: '#334155',
  
  ripple: '#475569',
  overlay: 'rgba(0,0,0,0.7)',
  
  bus: '#F87171',
  train: '#60A5FA',
  tukTuk: '#FBBF24',
  uber: '#34D399',
  walking: '#94A3B8',
  driving: '#A78BFA',
};

interface ThemeContextType {
  theme: ThemeColors;
  mode: ThemeMode;
  isDark: boolean;
  setTheme: (mode: ThemeMode) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = '@transit_companion_theme';

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [mode, setMode] = useState<ThemeMode>('light');
  const [systemColorScheme, setSystemColorScheme] = useState<ColorSchemeName>(
    Appearance.getColorScheme()
  );

  // Force light mode only - no dark mode
  const isDark = false;
  const theme = lightTheme;

  // Load saved theme preference on app start
  useEffect(() => {
    loadThemePreference();
    
    // Listen for system theme changes
    const subscription = Appearance.addChangeListener(({ colorScheme }) => {
      setSystemColorScheme(colorScheme);
    });

    return () => subscription?.remove();
  }, []);

  const loadThemePreference = async () => {
    try {
      const savedTheme = await AsyncStorage.getItem(THEME_STORAGE_KEY);
      if (savedTheme && ['light', 'dark', 'auto'].includes(savedTheme)) {
        setMode(savedTheme as ThemeMode);
      }
    } catch (error) {
      console.error('Error loading theme preference:', error);
    }
  };

  const setTheme = async (newMode: ThemeMode) => {
    try {
      setMode(newMode);
      await AsyncStorage.setItem(THEME_STORAGE_KEY, newMode);
    } catch (error) {
      console.error('Error saving theme preference:', error);
    }
  };

  const toggleTheme = () => {
    const newMode = isDark ? 'light' : 'dark';
    setTheme(newMode);
  };

  const value: ThemeContextType = {
    theme,
    mode,
    isDark,
    setTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// =============================================================================
// THEME UTILITY FUNCTIONS
// =============================================================================

export const getThemedStyle = (isDark: boolean, lightStyle: any, darkStyle: any) => {
  return isDark ? darkStyle : lightStyle;
};

export const getThemedColor = (theme: ThemeColors, colorName: keyof ThemeColors) => {
  return theme[colorName];
};

// =============================================================================
// PREDEFINED STYLE OBJECTS
// =============================================================================

export const createThemedStyles = (theme: ThemeColors) => ({
  container: {
    backgroundColor: theme.background,
  },
  
  card: {
    backgroundColor: theme.surface,
    borderColor: theme.border,
  },
  
  text: {
    color: theme.text,
  },
  
  textSecondary: {
    color: theme.textSecondary,
  },
  
  textTertiary: {
    color: theme.textTertiary,
  },
  
  button: {
    backgroundColor: theme.primary,
  },
  
  buttonSecondary: {
    backgroundColor: theme.surface,
    borderColor: theme.border,
  },
  
  input: {
    backgroundColor: theme.surface,
    borderColor: theme.border,
    color: theme.text,
  },
  
  separator: {
    backgroundColor: theme.divider,
  },
  
  shadow: {
    shadowColor: theme.text,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
});

// =============================================================================
// TRANSIT MODE THEMED COLORS
// =============================================================================

export const getTransitModeColor = (theme: ThemeColors, mode: string): string => {
  switch (mode.toLowerCase()) {
    case 'bus':
      return theme.bus;
    case 'train':
      return theme.train;
    case 'tuk_tuk':
    case 'tuk-tuk':
      return theme.tukTuk;
    case 'uber':
    case 'ride':
      return theme.uber;
    case 'walking':
    case 'walk':
      return theme.walking;
    case 'driving':
    case 'car':
      return theme.driving;
    default:
      return theme.primary;
  }
};

// =============================================================================
// STATUS BAR CONFIGURATION
// =============================================================================

export const getStatusBarStyle = (isDark: boolean) => ({
  style: isDark ? 'light-content' : 'dark-content',
  backgroundColor: isDark ? darkTheme.surface : lightTheme.surface,
});

// =============================================================================
// THEMED TAILWIND CLASSES (for NativeWind)
// =============================================================================

export const getThemedTailwindClasses = (isDark: boolean) => ({
  // Backgrounds
  bgPrimary: isDark ? 'bg-blue-500' : 'bg-blue-600',
  bgSecondary: isDark ? 'bg-slate-700' : 'bg-gray-100',
  bgSurface: isDark ? 'bg-slate-800' : 'bg-white',
  bgCard: isDark ? 'bg-slate-700' : 'bg-white',
  
  // Text
  textPrimary: isDark ? 'text-slate-100' : 'text-gray-900',
  textSecondary: isDark ? 'text-slate-300' : 'text-gray-600',
  textTertiary: isDark ? 'text-slate-400' : 'text-gray-400',
  
  // Borders
  border: isDark ? 'border-slate-600' : 'border-gray-300',
  borderLight: isDark ? 'border-slate-700' : 'border-gray-200',
  
  // Status colors remain consistent
  success: 'text-green-500',
  warning: 'text-yellow-500',
  error: 'text-red-500',
  info: 'text-blue-500',
});

export default ThemeProvider;