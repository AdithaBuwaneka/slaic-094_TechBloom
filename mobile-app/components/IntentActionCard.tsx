import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ChatIntent, ChatActionData } from '../src/types';

interface IntentActionCardProps {
  intent: ChatIntent;
  actionData?: ChatActionData;
  onActionPress: (intent: ChatIntent, actionData?: ChatActionData) => void;
  theme: any;
}

export default function IntentActionCard({ 
  intent, 
  actionData, 
  onActionPress, 
  theme 
}: IntentActionCardProps) {
  
  const getActionConfig = () => {
    switch (intent) {
      case ChatIntent.ROUTE_PLANNING:
        return {
          icon: 'map',
          iconColor: '#2563eb',
          title: 'Route Planned Successfully!',
          subtitle: actionData?.source && actionData?.destination 
            ? `From ${actionData.source} to ${actionData.destination}`
            : 'Your route has been planned',
          buttonText: 'View Route Details',
          buttonColor: '#2563eb',
          backgroundColor: '#eff6ff'
        };
      
      case ChatIntent.SAVED_ROUTES:
        return {
          icon: 'bookmark',
          iconColor: '#059669',
          title: 'View Your Routes',
          subtitle: 'See all your saved and recent routes',
          buttonText: 'Go to My Routes',
          buttonColor: '#059669',
          backgroundColor: '#ecfdf5'
        };
      
      case ChatIntent.DISRUPTIONS:
        return {
          icon: 'warning',
          iconColor: '#dc2626',
          title: 'Check Disruptions',
          subtitle: 'View current delays and traffic issues',
          buttonText: 'Check Disruptions',
          buttonColor: '#dc2626',
          backgroundColor: '#fef2f2'
        };
      
      default:
        return null;
    }
  };

  const config = getActionConfig();
  if (!config) return null;

  return (
    <View 
      className="mx-4 mt-3 p-4 rounded-lg shadow-sm"
      style={{ backgroundColor: config.backgroundColor }}
    >
      <View className="flex-row items-center mb-3">
        <Ionicons name={config.icon as any} size={24} color={config.iconColor} />
        <View className="ml-3 flex-1">
          <Text 
            className="text-lg font-semibold"
            style={{ color: theme.text }}
          >
            {config.title}
          </Text>
          <Text 
            className="text-sm"
            style={{ color: theme.textSecondary }}
          >
            {config.subtitle}
          </Text>
        </View>
      </View>
      
      <TouchableOpacity
        className="py-3 px-4 rounded-lg"
        style={{ backgroundColor: config.buttonColor }}
        onPress={() => onActionPress(intent, actionData)}
      >
        <Text className="text-white font-semibold text-center">
          {config.buttonText}
        </Text>
      </TouchableOpacity>
    </View>
  );
}
