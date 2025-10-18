import React, { useState, useRef, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { chatbotService } from '../../../src/services/api/chatbotService';
import { VoiceClient } from '../../../src/services/websocket/voiceClient';
import { PCMRecorder } from '../../../src/services/audio/pcmRecorder';
import { travelService } from '../../../src/services/api/travelService';
import { useTheme } from '../../../src/contexts/ThemeContext';
import { useLanguage } from '../../../src/contexts/LanguageContext';
import { useAuth, useApp } from '../../../src/contexts/AppContext';
import { ChatMessage, ChatIntent, ChatActionData } from '../../../src/types';
import IntentActionCard from '../../../components/IntentActionCard';
import MultiAgentAnimation from '../../../components/MultiAgentAnimation';
import * as FileSystem from 'expo-file-system/legacy'; // 👈 Import FileSystem legacy API
import { apiClient } from '../../../src/services/api/client'; // 👈 Import apiClient for token
import { Audio } from 'expo-av'; // 👈 Make sure Audio is imported from expo-av

// A simple WebSocket hook for managing the connection
function useVoiceSocket(onMessage: (data: any) => void) {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connect = async () => {
      const token = await apiClient.getStoredToken();
      if (!token) return;

      // Construct the WebSocket URL directly
      const wsUrl = `ws://10.0.2.2:8000/api/v1/ws/voice?token=${token}`;
      
      const socket = new WebSocket(wsUrl);
      socket.onopen = () => console.log('🎤 Voice WebSocket connected');
      socket.onmessage = (event) => onMessage(JSON.parse(event.data));
      socket.onerror = (error) => console.error('Voice WebSocket error:', error);
      socket.onclose = () => console.log('🎤 Voice WebSocket disconnected');
      ws.current = socket;
    };

    connect();

    return () => {
      ws.current?.close();
    };
  }, []);

  const sendMessage = (data: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    }
  };
  
  return sendMessage;
}

export default function Chat() {
  const { theme, isDark } = useTheme();
  const { t } = useLanguage();
  const { user } = useAuth();
  const { addToRouteHistory, setCurrentRoute } = useApp();
  const router = useRouter();
  
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: "Hi! I'm your AI travel assistant for Sri Lankan transport. I can help you with:\n\n🚌 Bus schedules and routes\n🚂 Train information\n🛺 Tuk-tuk options\n💰 Fare calculations\n🗺️ Route planning\n\nWhat would you like to know?",
      is_user: false,
      timestamp: new Date(),
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isProcessingRoute, setIsProcessingRoute] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');
  const voiceClientRef = useRef<VoiceClient | null>(null);
  const recorderRef = useRef<PCMRecorder | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);

  const quickQuestions = [
    "How do I get to Kandy from Colombo?",
    "What's the fare to the airport?",
    "Are there any delays today?",
    "Show me bus routes to Galle",
    "Train schedule to Anuradhapura"
  ];

  // Handle incoming WebSocket messages
  const handleSocketMessage = (data: any) => {
    if (data.type === 'final') {
      // Send the transcript to the chatbot for an answer (this will add the user message)
      sendMessage(data.text);
    } else if (data.type === 'error') {
      console.error('Received error from voice service:', data.message);
    }
  };

  const sendSocketMessage = useVoiceSocket(handleSocketMessage);

  useEffect(() => {
    recorderRef.current = new PCMRecorder();
    recorderRef.current.init();
  }, []);

  const startVoice = async () => {
    if (isRecording || !recorderRef.current) return;
    try {
      setInterimTranscript('Listening...');
      await recorderRef.current.start();
      setIsRecording(true);
    } catch (e) {
      console.warn('Failed to start voice recording', e);
      setInterimTranscript('');
    }
  };

  const stopVoice = async () => {
    if (!isRecording || !recorderRef.current) return;
    
    try {
      const audioUri = await recorderRef.current.stop();
      setIsRecording(false);
      setInterimTranscript('Processing...');

      if (audioUri) {
        console.log('Reading audio file from:', audioUri);
        // Read the audio file as a Base64 string
        const audioBase64 = await FileSystem.readAsStringAsync(audioUri, {
          encoding: 'base64',
        });

        // Send the audio data to the backend
        sendSocketMessage({
          type: 'audio_chunk',
          data: audioBase64,
        });
        
        setInterimTranscript(''); // Clear transcript after sending
      } else {
        console.warn('No audio file was created.');
        setInterimTranscript('');
      }
    } catch (e) {
      console.error('Failed to process voice recording:', e);
      setIsRecording(false);
      setInterimTranscript('');
    }
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  const sendMessage = async (text: string = inputText) => {
    if (!text.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: text.trim(),
      is_user: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      // Call the actual backend chatbot service with user_id for intent detection
      const response = await chatbotService.askQuestion({
        question: text.trim(),
        temperature: 0.7,
        user_id: user?.user_id || undefined
      });

      let responseText = '';
      let intent: ChatIntent | undefined;
      let actionData: ChatActionData | undefined;
      let requiresAction = false;
      
      if (response.success && response.data) {
        responseText = response.data.answer;
        intent = response.data.intent_type as ChatIntent;
        actionData = response.data.action_data;
        requiresAction = response.data.requires_action;
        
        console.log('Chatbot response data:', JSON.stringify(response.data, null, 2));
        console.log('Intent detected:', intent);
        console.log('Action data:', actionData);
        console.log('Requires action:', requiresAction);
        
        // If it's route planning, show the processing animation
        if (intent === ChatIntent.ROUTE_PLANNING && requiresAction) {
          setIsProcessingRoute(true);
        }
      } else {
        responseText = response.error?.message || 'Sorry, I encountered an error. Please try again.';
        console.log('Chatbot response error:', response.error);
      }
      
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        is_user: false,
        timestamp: new Date(),
        intent,
        action_data: actionData,
        requires_action: requiresAction,
      };

      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I'm having trouble connecting to the AI service. Please check your internet connection and try again.",
        is_user: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setIsProcessingRoute(false);
    }
  };

  const handleActionPress = async (intent: ChatIntent, actionData?: ChatActionData) => {
    switch (intent) {
      // New, corrected section
      case ChatIntent.ROUTE_PLANNING:
        // 1. Look for 'result' instead of 'route_result'
        if (actionData?.result) {
          const routeData = actionData.result;
          const responseData = routeData.response ?? routeData;

          let routes: any[] = [];
          if (responseData?.recommended_routes) {
            routes = responseData.recommended_routes;
          } else if (responseData?.all_routes) {
            routes = responseData.all_routes;
          } else if (responseData?.routes) {
            routes = responseData.routes;
          }

          if (routes.length > 0) {
            const routeForDisplay = routes[0];
            setCurrentRoute(routeForDisplay);

            // 2. Add the correctly structured object to the history state
            // The routeForDisplay object is a full RouteOption.
            await addToRouteHistory(routeForDisplay);

            // The saveRouteToBackend call might be redundant, but if needed,
            // it should also save the properly structured 'routeForDisplay'.
            if (user?.user_id) {
              // await travelService.saveRouteToBackend(routeForDisplay, user.user_id);
            }
            
            router.push('/(main)/(tabs)/routes');
            console.log('Route added to local history with consistent structure.');
          } else {
            // If no routes found, create a fallback route entry
            console.log('No routes found, creating fallback route');
            const fallbackRoute = {
              route_id: `fallback-${Date.now()}`,
              id: `fallback-${Date.now()}`,
              title: `${actionData.source || 'Unknown'} → ${actionData.destination || 'Unknown'}`,
              source: actionData.source || 'Unknown',
              destination: actionData.destination || 'Unknown',
              mode: actionData.mode || 'transit',
              modes: [actionData.mode || 'transit'],
              duration: 'Route not found',
              fare: 'N/A',
              carbonFootprint: 'N/A',
              aiRecommendation: 'Route planning completed but no specific routes found. Please try different travel modes or check the Routes tab for alternative options.',
              agentsUsed: ['route_planner'],
              summary: {
                duration_minutes: 0,
                distance_km: 0,
                estimated_fare: 0,
                transit_modes: ['transit'],
                transfers: 0,
                walking_distance: 0,
                carbon_footprint: 0
              },
              steps: [],
              fare_breakdown: { total_fare: 0, currency: 'LKR', breakdown: [], savings_vs_alternatives: 0, optimization_applied: false },
              agent_analysis: { user_preference_score: 0, fare_optimization_score: 0, disruption_risk_score: 0, comfort_score: 0, recommendations: [] },
              disruptions: [],
              alternatives: []
            };
            console.log('Created fallback route:', fallbackRoute);
            setCurrentRoute(fallbackRoute);
            console.log('Adding fallback route to history...');
            await addToRouteHistory(fallbackRoute);
            console.log('Fallback route added to history successfully');
          }
        } else {
          // If no route_result at all, still create a basic route entry
          console.log('No route_result in actionData, creating basic route');
          const basicRoute = {
            route_id: `basic-${Date.now()}`,
            id: `basic-${Date.now()}`,
            title: `${actionData?.source || 'Colombo'} → ${actionData?.destination || 'Badulla'}`,
            source: actionData?.source || 'Colombo',
            destination: actionData?.destination || 'Badulla',
            mode: actionData?.mode || 'transit',
            modes: [actionData?.mode || 'transit'],
            duration: 'Processing...',
            fare: 'Calculating...',
            carbonFootprint: 'Calculating...',
            aiRecommendation: 'Route planning is being processed. Check back in a moment.',
            agentsUsed: ['route_planner'],
            summary: {
              duration_minutes: 0,
              distance_km: 0,
              estimated_fare: 0,
              transit_modes: ['transit'],
              transfers: 0,
              walking_distance: 0,
              carbon_footprint: 0
            },
            steps: [],
            fare_breakdown: { total_fare: 0, currency: 'LKR', breakdown: [], savings_vs_alternatives: 0, optimization_applied: false },
            agent_analysis: { user_preference_score: 0, fare_optimization_score: 0, disruption_risk_score: 0, comfort_score: 0, recommendations: [] },
            disruptions: [],
            alternatives: []
          };
          console.log('Created basic route:', basicRoute);
          setCurrentRoute(basicRoute);
          console.log('Adding basic route to history...');
          await addToRouteHistory(basicRoute);
          console.log('Basic route added to history successfully');
        }
        // Small delay to ensure route is saved before navigation
        setTimeout(() => {
          router.push('/(main)/(tabs)/routes');
        }, 500);
        break;
        
      case ChatIntent.SAVED_ROUTES:
        router.push('/(main)/(tabs)/routes');
        break;
        
      case ChatIntent.DISRUPTIONS:
        router.push('/(main)/(tabs)/community');
        break;
        
      default:
        break;
    }
  };

  const getSimulatedResponse = (question: string): string => {
    const lowerQ = question.toLowerCase();
    
    if (lowerQ.includes('kandy') || lowerQ.includes('colombo')) {
      return "🚂 **Colombo to Kandy Route Options:**\n\n**By Train:**\n• Express trains: 2.5-3 hours\n• Fare: Rs. 100-300 depending on class\n• Departures: 5:55 AM, 8:30 AM, 2:35 PM\n\n**By Bus:**\n• Express buses: 3-4 hours\n• Fare: Rs. 200-400\n• Frequent departures from Bastian Mawatha\n\n**AI Recommendation:** Take the 8:30 AM train for scenic mountain views! 🏔️";
    }
    
    if (lowerQ.includes('airport') || lowerQ.includes('fare')) {
      return "✈️ **Routes to Bandaranaike Airport:**\n\n**From Colombo Fort:**\n• Airport Express Bus: Rs. 110, 45 mins\n• Taxi/Uber: Rs. 2000-3000, 30-45 mins\n• Train to Negombo + Bus: Rs. 150 total\n\n**From Kandy:**\n• Direct Airport Bus: Rs. 400, 3 hours\n• Via Colombo: Rs. 300 total, 4 hours\n\n💡 **Cost-saving tip:** Book Airport Express in advance for discounts!";
    }
    
    if (lowerQ.includes('delay') || lowerQ.includes('disruption')) {
      return "🚨 **Current Service Status:**\n\n✅ **No major disruptions** reported right now\n\n**Recent updates:**\n• All train lines operating normally\n• Minor delays on A1 highway due to construction\n• Galle bus services running 15 mins behind schedule\n\n🔔 Enable notifications to get real-time alerts about delays and disruptions!";
    }
    
    if (lowerQ.includes('galle') || lowerQ.includes('bus')) {
      return "🚌 **Bus Routes to Galle:**\n\n**Express Services:**\n• Route 2: Colombo Fort → Galle (Direct)\n• Fare: Rs. 280-320\n• Duration: 2-2.5 hours\n• Departures every 30 minutes\n\n**Highway Bus:**\n• Route 2: Via Southern Expressway\n• Fare: Rs. 350\n• Duration: 1.5 hours\n• Premium comfort\n\n🏖️ **Perfect for:** Beach trips and exploring the historic fort!";
    }
    
    if (lowerQ.includes('anuradhapura') || lowerQ.includes('train')) {
      return "🚂 **Train to Anuradhapura:**\n\n**Intercity Express:**\n• Departure: 7:10 AM from Colombo Fort\n• Duration: 4 hours\n• Fare: Rs. 180 (2nd class), Rs. 320 (1st class)\n\n**Night Mail:**\n• Departure: 9:45 PM\n• Duration: 5.5 hours\n• Sleeping berths available\n\n🏛️ **Cultural tip:** Perfect for visiting ancient temples and archaeological sites!";
    }
    
    return "I can help you with travel information for Sri Lanka! Try asking me about:\n\n• Routes between cities\n• Bus and train schedules\n• Fare information\n• Real-time delays\n• Best travel options\n\nWhat specific journey are you planning? 🗺️";
  };

  return (
    <SafeAreaView className="flex-1" style={{ backgroundColor: theme.background }}>
      <KeyboardAvoidingView 
        className="flex-1" 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
      >
        {/* Header */}
        <View className="px-4 py-3 border-b" style={{ backgroundColor: theme.primary, borderColor: theme.primaryDark }}>
          <View className="flex-row items-center">
            <View className="w-10 h-10 rounded-full items-center justify-center mr-3" style={{ backgroundColor: theme.primaryLight }}>
              <Text className="text-white text-lg">🤖</Text>
            </View>
            <View className="flex-1">
              <Text className="text-white text-lg font-semibold">{t('chat.title')}</Text>
              <Text className="text-blue-100 text-sm">
                {isTyping ? t('chat.thinking') : t('chat.subtitle')}
              </Text>
            </View>
            <TouchableOpacity className="p-2">
              <Ionicons name="information-circle-outline" size={24} color="white" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Messages */}
        <ScrollView 
          ref={scrollViewRef}
          className="flex-1 px-4 py-4"
          style={{ backgroundColor: theme.background }}
          showsVerticalScrollIndicator={false}
        >
          {messages.map((message) => (
            <View key={message.id}>
              <View
                className={`mb-4 ${message.is_user ? 'items-end' : 'items-start'}`}
              >
                <View
                  className={`max-w-[80%] px-4 py-3 rounded-xl ${
                    message.is_user
                      ? 'rounded-br-md'
                      : 'rounded-bl-md'
                  }`}
                  style={{
                    backgroundColor: message.is_user ? theme.primary : theme.surface
                  }}
                >
                  <Text
                    className="text-base"
                    style={{
                      color: message.is_user ? 'white' : theme.text
                    }}
                  >
                    {message.text}
                  </Text>
                </View>
                <Text className="text-xs mt-1 px-2" style={{ color: theme.textSecondary }}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Text>
              </View>
              
              {/* Show action card if message requires action */}
              {!message.is_user && message.requires_action && message.intent && (
                <IntentActionCard
                  intent={message.intent}
                  actionData={message.action_data}
                  onActionPress={handleActionPress}
                  theme={theme}
                />
              )}
            </View>
          ))}

          {isTyping && (
            <View className="items-start mb-4">
              {isProcessingRoute ? (
                // Show multi-agent animation for route planning
                <View className="px-4 py-3 rounded-xl rounded-bl-md w-full" style={{ backgroundColor: theme.surface }}>
                  <MultiAgentAnimation 
                    visible={true}
                    onComplete={() => {}}
                    onClose={() => {}}
                    requestData={{ source: '', destination: '', mode: 'transit' }}
                  />
                  <Text className="text-sm mt-2 text-center" style={{ color: theme.textSecondary }}>
                    AI agents are planning your route...
                  </Text>
                </View>
              ) : (
                // Regular typing indicator
                <View className="px-4 py-3 rounded-xl rounded-bl-md" style={{ backgroundColor: theme.surface }}>
                  <View className="flex-row items-center">
                    <View className="flex-row space-x-1">
                      <View className="w-2 h-2 rounded-full" style={{ backgroundColor: theme.textSecondary, opacity: 0.6 }} />
                      <View className="w-2 h-2 rounded-full" style={{ backgroundColor: theme.textSecondary, opacity: 0.4 }} />
                      <View className="w-2 h-2 rounded-full" style={{ backgroundColor: theme.textSecondary, opacity: 0.6 }} />
                    </View>
                    <Text className="text-sm ml-2" style={{ color: theme.textSecondary }}>{t('chat.thinking')}</Text>
                  </View>
                </View>
              )}
            </View>
          )}
        </ScrollView>

        {/* Quick Questions */}
        {messages.length <= 1 && (
          <View className="px-4 pb-2">
            <Text className="text-sm font-medium mb-2" style={{ color: theme.textSecondary }}>Quick questions:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View className="flex-row space-x-2">
                {quickQuestions.map((question, index) => (
                  <TouchableOpacity
                    key={index}
                    className="border px-3 py-2 rounded-lg"
                    style={{
                      backgroundColor: isDark ? theme.primary + '20' : '#EBF8FF',
                      borderColor: theme.primary
                    }}
                    onPress={() => sendMessage(question)}
                  >
                    <Text className="text-sm" style={{ color: theme.primary }}>{question}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>
          </View>
        )}

        {/* Input Area */}
        <View className="border-t px-4 py-3" style={{ borderColor: theme.border, backgroundColor: theme.surface }}>
          <View className="flex-row items-center space-x-3">
            <TouchableOpacity
              className="w-10 h-10 rounded-full items-center justify-center"
              style={{ backgroundColor: isRecording ? '#ef4444' : theme.primary }}
              onPress={async () => (isRecording ? await stopVoice() : await startVoice())}
            >
              <Ionicons name={isRecording ? 'stop' : 'mic'} size={18} color={'white'} />
            </TouchableOpacity>
            <View className="flex-1 flex-row items-center rounded-full px-4 py-2" style={{ backgroundColor: theme.background }}>
              <TextInput
                className="flex-1 text-base"
                style={{ color: theme.text }}
                placeholder={t('chat.placeholder')}
                placeholderTextColor={theme.textSecondary}
                value={inputText}
                onChangeText={setInputText}
                multiline={false}
                onSubmitEditing={() => sendMessage()}
              />
              {interimTranscript.length > 0 && (
                <Text className="text-xs ml-2" style={{ color: theme.textSecondary }}>
                  {interimTranscript}
                </Text>
              )}
              {inputText.length > 0 && (
                <TouchableOpacity
                  onPress={() => setInputText('')}
                  className="ml-2"
                >
                  <Ionicons name="close-circle" size={20} color={theme.textSecondary} />
                </TouchableOpacity>
              )}
            </View>
            <TouchableOpacity
              className="w-10 h-10 rounded-full items-center justify-center"
              style={{
                backgroundColor: inputText.trim() ? theme.primary : theme.textTertiary
              }}
              onPress={() => sendMessage()}
              disabled={!inputText.trim() || isTyping}
            >
              <Ionicons 
                name="send" 
                size={18} 
                color={inputText.trim() ? 'white' : theme.textSecondary} 
              />
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}