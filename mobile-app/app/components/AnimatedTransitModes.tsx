// =============================================================================
// ANIMATED TRANSIT MODES - Interactive Mode Switching with Animations
// =============================================================================

import React, { useRef, useEffect } from 'react';
import { View, Text, TouchableOpacity, Animated, Dimensions } from 'react-native';
import { SriLankanTravelMode } from '../../src/types';

const { width: screenWidth } = Dimensions.get('window');

interface ModeTab {
  mode: SriLankanTravelMode;
  emoji: string;
  label: string;
  color: string;
}

const modeTabs: ModeTab[] = [
  { mode: SriLankanTravelMode.BUS, emoji: '🚌', label: 'Bus', color: '#EF4444' },
  { mode: SriLankanTravelMode.TRAIN, emoji: '🚂', label: 'Train', color: '#3B82F6' },
  { mode: SriLankanTravelMode.TUK_TUK, emoji: '🛺', label: 'Tuk', color: '#F59E0B' },
  { mode: SriLankanTravelMode.UBER, emoji: '🚗', label: 'Ride', color: '#10B981' },
  { mode: SriLankanTravelMode.WALKING, emoji: '🚶', label: 'Walk', color: '#6B7280' },
];

interface Props {
  selectedMode: SriLankanTravelMode;
  onModeChange: (mode: SriLankanTravelMode) => void;
  isLoading?: boolean;
}

export default function AnimatedTransitModes({
  selectedMode,
  onModeChange,
  isLoading = false
}: Props) {
  const slideAnimation = useRef(new Animated.Value(0)).current;
  const scaleAnimations = useRef(
    modeTabs.reduce((acc, tab) => {
      acc[tab.mode] = new Animated.Value(1);
      return acc;
    }, {} as Record<SriLankanTravelMode, Animated.Value>)
  ).current;

  const selectedIndex = modeTabs.findIndex(tab => tab.mode === selectedMode);
  const tabWidth = (screenWidth - 32) / modeTabs.length; // Account for padding

  useEffect(() => {
    // Animate the selection indicator
    Animated.spring(slideAnimation, {
      toValue: selectedIndex * tabWidth,
      useNativeDriver: true,
      tension: 100,
      friction: 8,
    }).start();

    // Scale animation for selected tab
    Object.keys(scaleAnimations).forEach(mode => {
      const isSelected = mode === selectedMode;
      Animated.spring(scaleAnimations[mode as SriLankanTravelMode], {
        toValue: isSelected ? 1.1 : 1,
        useNativeDriver: true,
        tension: 150,
        friction: 8,
      }).start();
    });
  }, [selectedMode, selectedIndex, tabWidth, slideAnimation, scaleAnimations]);

  const handleModePress = (mode: SriLankanTravelMode) => {
    if (isLoading) return;

    // Quick press animation
    const pressAnimation = scaleAnimations[mode];
    Animated.sequence([
      Animated.timing(pressAnimation, {
        toValue: 0.95,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.spring(pressAnimation, {
        toValue: mode === selectedMode ? 1.1 : 1,
        useNativeDriver: true,
        tension: 150,
        friction: 8,
      })
    ]).start();

    onModeChange(mode);
  };

  return (
    <View className="mx-4 my-4">
      {/* Mode Tabs Container */}
      <View className="bg-gray-100 rounded-2xl p-2 relative overflow-hidden">
        {/* Animated Selection Indicator */}
        <Animated.View
          className="absolute top-2 bottom-2 rounded-xl"
          style={{
            width: tabWidth - 4,
            backgroundColor: modeTabs[selectedIndex]?.color || '#3B82F6',
            transform: [{ translateX: slideAnimation }],
            shadowColor: modeTabs[selectedIndex]?.color || '#3B82F6',
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: 0.3,
            shadowRadius: 4,
            elevation: 4,
          }}
        />

        {/* Mode Tabs */}
        <View className="flex-row">
          {modeTabs.map((tab, index) => {
            const isSelected = tab.mode === selectedMode;
            
            return (
              <Animated.View
                key={tab.mode}
                style={{
                  flex: 1,
                  transform: [{ scale: scaleAnimations[tab.mode] }],
                }}
              >
                <TouchableOpacity
                  className={`py-3 px-2 items-center justify-center relative z-10 ${
                    isLoading ? 'opacity-50' : ''
                  }`}
                  onPress={() => handleModePress(tab.mode)}
                  disabled={isLoading}
                  activeOpacity={0.7}
                >
                  {/* Emoji Icon */}
                  <Text
                    className="mb-1"
                    style={{
                      fontSize: isSelected ? 24 : 20,
                      opacity: isSelected ? 1 : 0.7,
                    }}
                  >
                    {tab.emoji}
                  </Text>

                  {/* Label */}
                  <Text
                    className={`text-xs font-semibold ${
                      isSelected ? 'text-white' : 'text-gray-600'
                    }`}
                    style={{
                      textShadowColor: isSelected ? 'rgba(0,0,0,0.3)' : 'transparent',
                      textShadowOffset: { width: 0, height: 1 },
                      textShadowRadius: 2,
                    }}
                  >
                    {tab.label}
                  </Text>

                  {/* Loading Indicator */}
                  {isLoading && isSelected && (
                    <View className="absolute -bottom-1 left-1/2">
                      <View 
                        className="w-1 h-1 bg-white rounded-full"
                        style={{
                          transform: [{ translateX: -2 }],
                        }}
                      />
                    </View>
                  )}
                </TouchableOpacity>
              </Animated.View>
            );
          })}
        </View>
      </View>

      {/* Selected Mode Info */}
      <Animated.View
        className="mt-3 px-2"
        style={{
          opacity: slideAnimation.interpolate({
            inputRange: [0, (modeTabs.length - 1) * tabWidth],
            outputRange: [1, 1],
            extrapolate: 'clamp',
          }),
        }}
      >
        <ModeDescription mode={selectedMode} />
      </Animated.View>
    </View>
  );
}

// =============================================================================
// MODE DESCRIPTION COMPONENT
// =============================================================================

function ModeDescription({ mode }: { mode: SriLankanTravelMode }) {
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
  }, [mode, fadeAnim]);

  const getModeDescription = () => {
    switch (mode) {
      case SriLankanTravelMode.BUS:
        return {
          title: 'Bus Service',
          subtitle: 'SLTB & Private operators',
          features: ['Affordable', 'Wide coverage', 'Frequent service'],
          color: '#EF4444'
        };
      case SriLankanTravelMode.TRAIN:
        return {
          title: 'Railway Service',
          subtitle: 'Sri Lanka Railways',
          features: ['Scenic routes', 'Comfortable', 'Reliable'],
          color: '#3B82F6'
        };
      case SriLankanTravelMode.TUK_TUK:
        return {
          title: 'Tuk-Tuk',
          subtitle: 'Three-wheeler taxi',
          features: ['Door-to-door', 'Quick trips', 'Negotiable'],
          color: '#F59E0B'
        };
      case SriLankanTravelMode.UBER:
        return {
          title: 'App-based Rides',
          subtitle: 'Uber, PickMe, etc.',
          features: ['Air conditioned', 'Fixed pricing', 'GPS tracking'],
          color: '#10B981'
        };
      case SriLankanTravelMode.WALKING:
        return {
          title: 'Walking',
          subtitle: 'Pedestrian route',
          features: ['Healthy', 'Free', 'Eco-friendly'],
          color: '#6B7280'
        };
      case SriLankanTravelMode.DRIVING:
        return {
          title: 'Personal Vehicle',
          subtitle: 'Own car/motorbike',
          features: ['Complete control', 'Privacy', 'Flexible'],
          color: '#8B5CF6'
        };
      default:
        return {
          title: 'Transit',
          subtitle: 'Mixed transport modes',
          features: ['Optimized', 'Multi-modal', 'Smart routing'],
          color: '#6B7280'
        };
    }
  };

  const modeInfo = getModeDescription();

  return (
    <Animated.View
      style={{
        opacity: fadeAnim,
        transform: [{
          translateY: fadeAnim.interpolate({
            inputRange: [0, 1],
            outputRange: [10, 0]
          })
        }]
      }}
    >
      <View className="flex-row items-center justify-between">
        <View className="flex-1">
          <Text className="text-base font-semibold text-gray-800">
            {modeInfo.title}
          </Text>
          <Text className="text-sm text-gray-600 mb-2">
            {modeInfo.subtitle}
          </Text>
        </View>
      </View>

      {/* Features */}
      <View className="flex-row flex-wrap gap-2">
        {modeInfo.features.map((feature, index) => (
          <View
            key={index}
            className="bg-gray-50 border border-gray-200 rounded-full px-3 py-1"
            style={{
              borderColor: modeInfo.color + '20',
              backgroundColor: modeInfo.color + '10',
            }}
          >
            <Text
              className="text-xs font-medium"
              style={{ color: modeInfo.color }}
            >
              {feature}
            </Text>
          </View>
        ))}
      </View>
    </Animated.View>
  );
}

// =============================================================================
// FLOATING MODE SWITCHER
// =============================================================================

interface FloatingModeSwitcherProps {
  selectedMode: SriLankanTravelMode;
  onModeChange: (mode: SriLankanTravelMode) => void;
  position: 'top' | 'bottom';
}

export function FloatingModeSwitcher({
  selectedMode,
  onModeChange,
  position = 'bottom'
}: FloatingModeSwitcherProps) {
  const slideAnimation = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.spring(slideAnimation, {
      toValue: 1,
      useNativeDriver: true,
      tension: 100,
      friction: 8,
    }).start();
  }, [slideAnimation]);

  return (
    <Animated.View
      className={`absolute left-4 right-4 ${
        position === 'top' ? 'top-4' : 'bottom-4'
      } z-50`}
      style={{
        transform: [{
          translateY: slideAnimation.interpolate({
            inputRange: [0, 1],
            outputRange: [position === 'top' ? -50 : 50, 0]
          })
        }],
        opacity: slideAnimation,
      }}
    >
      <View className="bg-white rounded-2xl shadow-lg border border-gray-100 p-2">
        <View className="flex-row justify-around">
          {modeTabs.slice(0, 4).map((tab) => {
            const isSelected = tab.mode === selectedMode;
            
            return (
              <TouchableOpacity
                key={tab.mode}
                className={`w-12 h-12 rounded-xl items-center justify-center ${
                  isSelected ? 'shadow-md' : ''
                }`}
                style={{
                  backgroundColor: isSelected ? tab.color : 'transparent',
                }}
                onPress={() => onModeChange(tab.mode)}
              >
                <Text
                  className="text-lg"
                  style={{
                    opacity: isSelected ? 1 : 0.6,
                  }}
                >
                  {tab.emoji}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    </Animated.View>
  );
}