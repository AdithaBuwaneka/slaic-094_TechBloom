import React, { useState, useRef, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { chatbotService } from '../../../src/services/api/chatbotService';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  isTyping?: boolean;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I'm your AI travel assistant for Sri Lankan transport. I can help you with:\n\n🚌 Bus schedules and routes\n🚂 Train information\n🛺 Tuk-tuk options\n💰 Fare calculations\n🗺️ Route planning\n\nWhat would you like to know?",
      isUser: false,
      timestamp: new Date(),
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  const quickQuestions = [
    "How do I get to Kandy from Colombo?",
    "What's the fare to the airport?",
    "Are there any delays today?",
    "Show me bus routes to Galle",
    "Train schedule to Anuradhapura"
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  const sendMessage = async (text: string = inputText) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      // Call the actual backend chatbot service
      const response = await chatbotService.askQuestion({
        question: text.trim(),
        temperature: 0.7
      });

      let responseText = '';
      if (response.success && response.data) {
        responseText = response.data.answer;
      } else {
        responseText = response.error?.message || 'Sorry, I encountered an error. Please try again.';
      }
      
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I'm having trouble connecting to the AI service. Please check your internet connection and try again.",
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
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
    <SafeAreaView className="flex-1 bg-white">
      <KeyboardAvoidingView 
        className="flex-1" 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
      >
        {/* Header */}
        <View className="bg-blue-600 px-4 py-3 border-b border-blue-700">
          <View className="flex-row items-center">
            <View className="w-10 h-10 bg-blue-500 rounded-full items-center justify-center mr-3">
              <Text className="text-white text-lg">🤖</Text>
            </View>
            <View className="flex-1">
              <Text className="text-white text-lg font-semibold">AI Travel Assistant</Text>
              <Text className="text-blue-100 text-sm">
                {isTyping ? 'AI is thinking...' : 'Online • RAG-Enhanced AI Assistant'}
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
          showsVerticalScrollIndicator={false}
        >
          {messages.map((message) => (
            <View
              key={message.id}
              className={`mb-4 ${message.isUser ? 'items-end' : 'items-start'}`}
            >
              <View
                className={`max-w-[80%] px-4 py-3 rounded-xl ${
                  message.isUser
                    ? 'bg-blue-600 rounded-br-md'
                    : 'bg-gray-100 rounded-bl-md'
                }`}
              >
                <Text
                  className={`text-base ${
                    message.isUser ? 'text-white' : 'text-gray-800'
                  }`}
                >
                  {message.text}
                </Text>
              </View>
              <Text className="text-xs text-gray-500 mt-1 px-2">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </Text>
            </View>
          ))}

          {isTyping && (
            <View className="items-start mb-4">
              <View className="bg-gray-100 px-4 py-3 rounded-xl rounded-bl-md">
                <View className="flex-row items-center">
                  <View className="flex-row space-x-1">
                    <View className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
                    <View className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
                    <View className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
                  </View>
                  <Text className="text-gray-500 text-sm ml-2">AI thinking...</Text>
                </View>
              </View>
            </View>
          )}
        </ScrollView>

        {/* Quick Questions */}
        {messages.length <= 1 && (
          <View className="px-4 pb-2">
            <Text className="text-sm font-medium text-gray-600 mb-2">Quick questions:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View className="flex-row space-x-2">
                {quickQuestions.map((question, index) => (
                  <TouchableOpacity
                    key={index}
                    className="bg-blue-50 border border-blue-200 px-3 py-2 rounded-lg"
                    onPress={() => sendMessage(question)}
                  >
                    <Text className="text-blue-700 text-sm">{question}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>
          </View>
        )}

        {/* Input Area */}
        <View className="border-t border-gray-200 px-4 py-3">
          <View className="flex-row items-center space-x-3">
            <View className="flex-1 flex-row items-center bg-gray-100 rounded-full px-4 py-2">
              <TextInput
                className="flex-1 text-base"
                placeholder="Ask about routes, fares, schedules..."
                value={inputText}
                onChangeText={setInputText}
                multiline={false}
                onSubmitEditing={() => sendMessage()}
              />
              {inputText.length > 0 && (
                <TouchableOpacity
                  onPress={() => setInputText('')}
                  className="ml-2"
                >
                  <Ionicons name="close-circle" size={20} color="#6b7280" />
                </TouchableOpacity>
              )}
            </View>
            <TouchableOpacity
              className={`w-10 h-10 rounded-full items-center justify-center ${
                inputText.trim() ? 'bg-blue-600' : 'bg-gray-300'
              }`}
              onPress={() => sendMessage()}
              disabled={!inputText.trim() || isTyping}
            >
              <Ionicons 
                name="send" 
                size={18} 
                color={inputText.trim() ? 'white' : '#6b7280'} 
              />
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}