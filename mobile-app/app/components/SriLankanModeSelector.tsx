// =============================================================================
// SRI LANKAN MODE SELECTOR - Animated Transit Mode Selection
// =============================================================================

import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Animated, Dimensions } from 'react-native';
import { SriLankanTravelMode } from '../../src/types';

const { width: screenWidth } = Dimensions.get('window');

interface SriLankanMode {
  mode: SriLankanTravelMode;
  name: string;
  sinhala: string;
  tamil: string;
  emoji: string;
  color: string;
  description: string;
  features: string[];
}

const sriLankanModes: SriLankanMode[] = [
  {
    mode: SriLankanTravelMode.BUS,
    name: 'Bus',
    sinhala: 'බස්',
    tamil: 'பேருந்து',
    emoji: '🚌',
    color: '#EF4444',
    description: 'SLTB & Private buses',
    features: ['Affordable', 'Wide coverage', 'Frequent service']
  },
  {
    mode: SriLankanTravelMode.TRAIN,
    name: 'Train',
    sinhala: 'කෝච්චිය',
    tamil: 'ரயில்',
    emoji: '🚂',
    color: '#3B82F6',
    description: 'Sri Lanka Railways',
    features: ['Scenic routes', 'Comfortable', 'Reliable']
  },
  {
    mode: SriLankanTravelMode.TUK_TUK,
    name: 'Tuk Tuk',
    sinhala: 'තුන් රෝදය',
    tamil: 'ஆட்டோ',
    emoji: '🛺',
    color: '#F59E0B',
    description: 'Three-wheeler taxi',
    features: ['Door-to-door', 'Quick', 'Negotiable fare']
  },
  {
    mode: SriLankanTravelMode.UBER,
    name: 'Uber/PickMe',
    sinhala: 'කාර් රයිඩ්',
    tamil: 'கார் பயணம்',
    emoji: '🚗',
    color: '#10B981',
    description: 'App-based rides',
    features: ['Air conditioned', 'Fixed pricing', 'GPS tracking']
  },
  {
    mode: SriLankanTravelMode.DRIVING,
    name: 'Own Vehicle',
    sinhala: 'පුද්ගලික වාහනය',
    tamil: 'சொந்த வாகனம்',
    emoji: '🚙',
    color: '#8B5CF6',
    description: 'Personal car/bike',
    features: ['Complete control', 'Privacy', 'Flexible timing']
  },
  {
    mode: SriLankanTravelMode.TWO_WHEELER,
    name: 'Motorbike',
    sinhala: 'පැදි පැදි',
    tamil: 'மோட்டார் பைக்',
    emoji: '🏍️',
    color: '#F97316',
    description: 'Motorcycle/Scooter',
    features: ['Beat traffic', 'Fuel efficient', 'Easy parking']
  },
  {
    mode: SriLankanTravelMode.WALKING,
    name: 'Walking',
    sinhala: 'ඇවිදීම',
    tamil: 'நடைபயணம்',
    emoji: '🚶',
    color: '#6B7280',
    description: 'On foot',
    features: ['Healthy', 'Free', 'Eco-friendly']
  }
];

interface Props {
  selectedMode: SriLankanTravelMode | null;
  onModeSelect: (mode: SriLankanTravelMode) => void;
  language: 'en' | 'si' | 'ta';
  isLoading?: boolean;
  showDescriptions?: boolean;
}

export default function SriLankanModeSelector({
  selectedMode,
  onModeSelect,
  language = 'en',
  isLoading = false,
  showDescriptions = true
}: Props) {
  const [animatedValues] = useState(() => 
    sriLankanModes.reduce((acc, mode) => {
      acc[mode.mode] = new Animated.Value(1);
      return acc;
    }, {} as Record<SriLankanTravelMode, Animated.Value>)
  );

  const handleModePress = (mode: SriLankanMode) => {
    if (isLoading) return;

    // Animate the pressed mode
    const animation = Animated.sequence([
      Animated.timing(animatedValues[mode.mode], {
        toValue: 0.8,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(animatedValues[mode.mode], {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      })
    ]);

    animation.start();
    onModeSelect(mode.mode);
  };

  const getModeName = (mode: SriLankanMode): string => {
    switch (language) {
      case 'si': return mode.sinhala;
      case 'ta': return mode.tamil;
      default: return mode.name;
    }
  };

  const isSelected = (mode: SriLankanTravelMode): boolean => {
    return selectedMode === mode;
  };

  return (
    <View className="px-4">
      {/* Header */}
      <View className="mb-6">
        <Text className="text-2xl font-bold text-gray-900 text-center mb-2">
          {language === 'si' ? 'ගමන් මාර්ගය තෝරන්න' :
           language === 'ta' ? 'பயண முறையைத் தேர்ந்தெடுக்கவும்' :
           'Choose Your Mode'}
        </Text>
        <Text className="text-gray-600 text-center">
          {language === 'si' ? 'ශ්‍රී ලංකාවේ ප්‍රවාහන විකල්ප' :
           language === 'ta' ? 'இலங்கையின் போக்குவரத்து விருப்பங்கள்' :
           'Sri Lankan Transport Options'}
        </Text>
      </View>

      {/* Mode Grid */}
      <View className="flex-row flex-wrap justify-between">
        {sriLankanModes.map((mode) => (
          <Animated.View
            key={mode.mode}
            style={{
              transform: [{ scale: animatedValues[mode.mode] }],
              width: screenWidth / 2 - 24, // Two columns with padding
              marginBottom: 16,
            }}
          >
            <TouchableOpacity
              onPress={() => handleModePress(mode)}
              disabled={isLoading}
              className={`
                p-4 rounded-2xl border-2 min-h-[120px]
                ${isSelected(mode.mode) 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 bg-white'
                }
                ${isLoading ? 'opacity-50' : ''}
              `}
              style={{
                shadowColor: isSelected(mode.mode) ? mode.color : '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: isSelected(mode.mode) ? 0.3 : 0.1,
                shadowRadius: isSelected(mode.mode) ? 8 : 3,
                elevation: isSelected(mode.mode) ? 8 : 3,
              }}
            >
              {/* Emoji Icon */}
              <View className="items-center mb-2">
                <Text 
                  className="text-3xl"
                  style={{ 
                    fontSize: isSelected(mode.mode) ? 36 : 32 
                  }}
                >
                  {mode.emoji}
                </Text>
              </View>

              {/* Mode Name */}
              <Text 
                className={`
                  text-center font-semibold mb-1
                  ${isSelected(mode.mode) ? 'text-blue-700' : 'text-gray-900'}
                `}
                style={{ fontSize: 14 }}
              >
                {getModeName(mode)}
              </Text>

              {/* Description */}
              {showDescriptions && (
                <Text 
                  className={`
                    text-xs text-center
                    ${isSelected(mode.mode) ? 'text-blue-600' : 'text-gray-500'}
                  `}
                >
                  {mode.description}
                </Text>
              )}

              {/* Selection Indicator */}
              {isSelected(mode.mode) && (
                <View 
                  className="absolute -top-2 -right-2 w-6 h-6 rounded-full items-center justify-center"
                  style={{ backgroundColor: mode.color }}
                >
                  <Text className="text-white text-xs font-bold">✓</Text>
                </View>
              )}

              {/* Color Accent Bar */}
              <View 
                className="absolute bottom-0 left-0 right-0 h-1 rounded-b-xl"
                style={{ 
                  backgroundColor: isSelected(mode.mode) ? mode.color : 'transparent' 
                }}
              />
            </TouchableOpacity>
          </Animated.View>
        ))}
      </View>

      {/* Selected Mode Details */}
      {selectedMode && (
        <Animated.View
          className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200"
          style={{
            transform: [{
              translateY: new Animated.Value(20)
            }]
          }}
        >
          {(() => {
            const selectedModeData = sriLankanModes.find(m => m.mode === selectedMode);
            if (!selectedModeData) return null;

            // Animate the details panel
            const detailsAnimation = new Animated.Value(0);
            Animated.timing(detailsAnimation, {
              toValue: 1,
              duration: 300,
              useNativeDriver: true,
            }).start();

            return (
              <Animated.View
                style={{
                  opacity: detailsAnimation,
                  transform: [{
                    translateY: detailsAnimation.interpolate({
                      inputRange: [0, 1],
                      outputRange: [20, 0]
                    })
                  }]
                }}
              >
                <View className="flex-row items-center mb-3">
                  <Text className="text-2xl mr-3">{selectedModeData.emoji}</Text>
                  <View className="flex-1">
                    <Text className="text-lg font-bold text-blue-900">
                      {getModeName(selectedModeData)}
                    </Text>
                    <Text className="text-blue-700 text-sm">
                      {selectedModeData.description}
                    </Text>
                  </View>
                </View>

                {/* Features */}
                <View>
                  <Text className="text-sm font-semibold text-blue-800 mb-2">
                    {language === 'si' ? 'විශේෂාංග:' :
                     language === 'ta' ? 'அம்சங்கள்:' :
                     'Features:'}
                  </Text>
                  <View className="flex-row flex-wrap">
                    {selectedModeData.features.map((feature, index) => (
                      <View
                        key={index}
                        className="bg-white border border-blue-300 rounded-full px-3 py-1 mr-2 mb-2"
                      >
                        <Text className="text-xs text-blue-700">{feature}</Text>
                      </View>
                    ))}
                  </View>
                </View>
              </Animated.View>
            );
          })()}
        </Animated.View>
      )}

      {/* Loading State */}
      {isLoading && (
        <View className="absolute inset-0 bg-white bg-opacity-80 items-center justify-center rounded-2xl">
          <View className="flex-row items-center">
            <View className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mr-3" />
            <Text className="text-blue-700 font-medium">
              {language === 'si' ? 'ප්‍රසාරණය...' :
               language === 'ta' ? 'செயல்படுத்துகிறது...' :
               'Processing...'}
            </Text>
          </View>
        </View>
      )}
    </View>
  );
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

export const getSriLankanModeInfo = (mode: SriLankanTravelMode) => {
  return sriLankanModes.find(m => m.mode === mode);
};

export const getAllSriLankanModes = () => {
  return sriLankanModes;
};

export const getModesByCategory = () => {
  return {
    public_transport: [
      SriLankanTravelMode.BUS,
      SriLankanTravelMode.TRAIN
    ],
    private_hired: [
      SriLankanTravelMode.TUK_TUK,
      SriLankanTravelMode.UBER
    ],
    personal: [
      SriLankanTravelMode.DRIVING,
      SriLankanTravelMode.TWO_WHEELER,
      SriLankanTravelMode.WALKING
    ]
  };
};