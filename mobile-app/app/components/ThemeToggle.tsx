// =============================================================================
// THEME TOGGLE - Dark/Light Mode Switch Component
// =============================================================================

import React, { useRef, useEffect } from 'react';
import { View, Text, TouchableOpacity, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme, ThemeMode } from '../../src/contexts/ThemeContext';

interface Props {
  variant?: 'switch' | 'button' | 'segmented';
  showLabel?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export default function ThemeToggle({ 
  variant = 'switch', 
  showLabel = true, 
  size = 'medium' 
}: Props) {
  const { theme, mode, isDark, setTheme, toggleTheme } = useTheme();
  
  if (variant === 'segmented') {
    return <SegmentedThemeControl />;
  }
  
  if (variant === 'button') {
    return <ButtonThemeToggle showLabel={showLabel} size={size} />;
  }
  
  return <SwitchThemeToggle showLabel={showLabel} size={size} />;
}

// =============================================================================
// SWITCH STYLE TOGGLE
// =============================================================================

function SwitchThemeToggle({ showLabel, size }: Pick<Props, 'showLabel' | 'size'>) {
  const { theme, isDark, toggleTheme } = useTheme();
  const slideAnimation = useRef(new Animated.Value(isDark ? 1 : 0)).current;
  
  const switchWidth = size === 'small' ? 48 : size === 'large' ? 64 : 56;
  const switchHeight = size === 'small' ? 24 : size === 'large' ? 32 : 28;
  const knobSize = size === 'small' ? 20 : size === 'large' ? 28 : 24;
  
  useEffect(() => {
    Animated.spring(slideAnimation, {
      toValue: isDark ? 1 : 0,
      useNativeDriver: true,
      tension: 100,
      friction: 8,
    }).start();
  }, [isDark, slideAnimation]);

  const handleToggle = () => {
    toggleTheme();
  };

  return (
    <View className="flex-row items-center space-x-3">
      {showLabel && (
        <Text
          className="text-sm font-medium"
          style={{ color: theme.textSecondary }}
        >
          Dark mode
        </Text>
      )}
      
      <TouchableOpacity
        className="relative rounded-full p-1"
        style={{
          width: switchWidth,
          height: switchHeight,
          backgroundColor: isDark ? theme.primary : theme.border,
        }}
        onPress={handleToggle}
        activeOpacity={0.8}
      >
        {/* Track */}
        <View 
          className="absolute inset-1 rounded-full"
          style={{
            backgroundColor: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)',
          }}
        />
        
        {/* Sliding knob */}
        <Animated.View
          className="absolute top-1 rounded-full shadow-md flex items-center justify-center"
          style={{
            width: knobSize,
            height: knobSize,
            backgroundColor: theme.surface,
            transform: [{
              translateX: slideAnimation.interpolate({
                inputRange: [0, 1],
                outputRange: [0, switchWidth - knobSize - 4],
              })
            }],
            shadowColor: theme.text,
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: 0.2,
            shadowRadius: 4,
            elevation: 4,
          }}
        >
          {/* Icon inside knob */}
          <Ionicons
            name={isDark ? 'moon' : 'sunny'}
            size={size === 'small' ? 10 : size === 'large' ? 14 : 12}
            color={isDark ? theme.primary : theme.warning}
          />
        </Animated.View>
      </TouchableOpacity>
    </View>
  );
}

// =============================================================================
// BUTTON STYLE TOGGLE
// =============================================================================

function ButtonThemeToggle({ showLabel, size }: Pick<Props, 'showLabel' | 'size'>) {
  const { theme, isDark, toggleTheme } = useTheme();
  const scaleAnimation = useRef(new Animated.Value(1)).current;
  
  const buttonSize = size === 'small' ? 36 : size === 'large' ? 52 : 44;
  const iconSize = size === 'small' ? 20 : size === 'large' ? 28 : 24;

  const handlePress = () => {
    // Quick scale animation
    Animated.sequence([
      Animated.timing(scaleAnimation, {
        toValue: 0.9,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnimation, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      })
    ]).start();
    
    toggleTheme();
  };

  return (
    <View className="items-center">
      <Animated.View
        style={{
          transform: [{ scale: scaleAnimation }],
        }}
      >
        <TouchableOpacity
          className="rounded-full items-center justify-center"
          style={{
            width: buttonSize,
            height: buttonSize,
            backgroundColor: theme.surface,
            borderColor: theme.border,
            borderWidth: 1,
            shadowColor: theme.text,
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: 0.1,
            shadowRadius: 4,
            elevation: 3,
          }}
          onPress={handlePress}
          activeOpacity={0.8}
        >
          <Ionicons
            name={isDark ? 'sunny' : 'moon'}
            size={iconSize}
            color={isDark ? theme.warning : theme.primary}
          />
        </TouchableOpacity>
      </Animated.View>
      
      {showLabel && (
        <Text
          className="text-xs mt-1 text-center"
          style={{ color: theme.textTertiary }}
        >
          {isDark ? 'Light' : 'Dark'}
        </Text>
      )}
    </View>
  );
}

// =============================================================================
// SEGMENTED CONTROL STYLE
// =============================================================================

function SegmentedThemeControl() {
  const { theme, mode, setTheme } = useTheme();
  const slideAnimation = useRef(new Animated.Value(0)).current;

  const modes: { key: ThemeMode; label: string; icon: string }[] = [
    { key: 'light', label: 'Light', icon: 'sunny' },
    { key: 'auto', label: 'Auto', icon: 'phone-portrait' },
    { key: 'dark', label: 'Dark', icon: 'moon' },
  ];

  const selectedIndex = modes.findIndex(m => m.key === mode);

  useEffect(() => {
    Animated.spring(slideAnimation, {
      toValue: selectedIndex,
      useNativeDriver: true,
      tension: 100,
      friction: 8,
    }).start();
  }, [selectedIndex, slideAnimation]);

  const handleModeSelect = (newMode: ThemeMode) => {
    setTheme(newMode);
  };

  const segmentWidth = 80;

  return (
    <View 
      className="flex-row rounded-xl p-1 relative"
      style={{
        backgroundColor: theme.surface,
        borderColor: theme.border,
        borderWidth: 1,
      }}
    >
      {/* Sliding indicator */}
      <Animated.View
        className="absolute top-1 bottom-1 rounded-lg"
        style={{
          width: segmentWidth,
          backgroundColor: theme.primary,
          transform: [{
            translateX: slideAnimation.interpolate({
              inputRange: [0, 1, 2],
              outputRange: [0, segmentWidth, segmentWidth * 2],
              extrapolate: 'clamp',
            })
          }],
          shadowColor: theme.primary,
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.3,
          shadowRadius: 4,
          elevation: 4,
        }}
      />

      {/* Mode options */}
      {modes.map((modeOption, index) => {
        const isSelected = mode === modeOption.key;
        
        return (
          <TouchableOpacity
            key={modeOption.key}
            className="items-center justify-center py-2 relative z-10"
            style={{ width: segmentWidth }}
            onPress={() => handleModeSelect(modeOption.key)}
            activeOpacity={0.7}
          >
            <Ionicons
              name={modeOption.icon as any}
              size={16}
              color={isSelected ? '#FFFFFF' : theme.textSecondary}
              style={{ marginBottom: 2 }}
            />
            <Text
              className="text-xs font-medium"
              style={{
                color: isSelected ? '#FFFFFF' : theme.textSecondary,
              }}
            >
              {modeOption.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

// =============================================================================
// THEME PREVIEW COMPONENT
// =============================================================================

interface ThemePreviewProps {
  mode: ThemeMode;
  isSelected: boolean;
  onSelect: () => void;
}

export function ThemePreview({ mode, isSelected, onSelect }: ThemePreviewProps) {
  const { theme } = useTheme();
  
  const previewTheme = mode === 'dark' ? 'dark' : 
                      mode === 'light' ? 'light' : 
                      'auto';

  return (
    <TouchableOpacity
      className={`p-4 rounded-xl border-2 ${
        isSelected ? 'border-blue-500' : 'border-gray-200'
      }`}
      style={{
        backgroundColor: theme.surface,
        minHeight: 120,
      }}
      onPress={onSelect}
      activeOpacity={0.8}
    >
      {/* Preview header */}
      <View className="flex-row items-center justify-between mb-3">
        <Text
          className="font-semibold text-base"
          style={{ color: theme.text }}
        >
          {mode === 'light' ? 'Light Mode' : 
           mode === 'dark' ? 'Dark Mode' : 
           'Auto Mode'}
        </Text>
        <Ionicons
          name={mode === 'light' ? 'sunny' : 
                mode === 'dark' ? 'moon' : 
                'phone-portrait'}
          size={20}
          color={theme.primary}
        />
      </View>

      {/* Mini preview */}
      <View className="flex-1 justify-center">
        <View 
          className="h-6 rounded mb-2"
          style={{
            backgroundColor: previewTheme === 'dark' ? '#1E293B' : '#F9FAFB',
          }}
        />
        <View className="flex-row space-x-2">
          <View 
            className="flex-1 h-4 rounded"
            style={{
              backgroundColor: previewTheme === 'dark' ? '#334155' : '#E5E7EB',
            }}
          />
          <View 
            className="flex-1 h-4 rounded"
            style={{
              backgroundColor: previewTheme === 'dark' ? '#475569' : '#D1D5DB',
            }}
          />
        </View>
      </View>

      {/* Selection indicator */}
      {isSelected && (
        <View className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full items-center justify-center">
          <Ionicons name="checkmark" size={16} color="#FFFFFF" />
        </View>
      )}
    </TouchableOpacity>
  );
}