// =============================================================================
// CHATBOT SERVICE - RAG-based Transit Assistant
// =============================================================================

import { apiClient } from './client';
import { ENDPOINTS } from './config';
import { 
  ChatbotRequest,
  ChatbotResponse,
  ChatMessage,
  ChatContext,
  APIResponse 
} from '../../types';

class ChatbotService {
  // =============================================================================
  // CHATBOT INTERACTION
  // =============================================================================

  async askQuestion(request: ChatbotRequest): Promise<APIResponse<ChatbotResponse>> {
    try {
      console.log('Asking chatbot question:', request.question);
      
      const chatRequest = {
        question: request.question,
        temperature: request.temperature || 0.7,
        context: request.context || {}
      };

      const response = await apiClient.post<ChatbotResponse>(
        ENDPOINTS.CHATBOT.ASK, 
        chatRequest,
        { timeout: 45000 } // 45 seconds for AI processing
      );

      if (response.success && response.data) {
        // Cache the conversation for context
        await this.cacheConversation(request.question, response.data);
      }

      return response;
    } catch (error) {
      console.error('Chatbot question error:', error);
      throw error;
    }
  }

  async getChatbotHealth(): Promise<APIResponse<{
    status: 'healthy' | 'degraded' | 'down';
    response_time_ms: number;
    rag_system: {
      vector_db_status: 'connected' | 'disconnected';
      llm_status: 'available' | 'unavailable';
      knowledge_base_updated: string;
    };
    performance: {
      avg_response_time_ms: number;
      total_queries_today: number;
      success_rate_percentage: number;
    };
  }>> {
    return apiClient.get(ENDPOINTS.CHATBOT.HEALTH);
  }

  // =============================================================================
  // CONVERSATION MANAGEMENT
  // =============================================================================

  async getConversationHistory(limit: number = 20): Promise<ChatMessage[]> {
    try {
      // TODO: Implement with AsyncStorage
      // const historyKey = 'chat_history';
      // const storedHistory = await AsyncStorage.getItem(historyKey);
      // 
      // if (storedHistory) {
      //   const messages: ChatMessage[] = JSON.parse(storedHistory);
      //   return messages.slice(-limit);
      // }
      
      return [];
    } catch (error) {
      console.error('Error getting conversation history:', error);
      return [];
    }
  }

  async saveMessage(message: ChatMessage): Promise<void> {
    try {
      // TODO: Implement with AsyncStorage
      // const historyKey = 'chat_history';
      // const existingHistory = await AsyncStorage.getItem(historyKey);
      // 
      // let messages: ChatMessage[] = [];
      // if (existingHistory) {
      //   messages = JSON.parse(existingHistory);
      // }
      // 
      // messages.push(message);
      // 
      // // Keep only last 100 messages to prevent storage bloat
      // if (messages.length > 100) {
      //   messages = messages.slice(-100);
      // }
      // 
      // await AsyncStorage.setItem(historyKey, JSON.stringify(messages));
      
      console.log('Message saved to history');
    } catch (error) {
      console.error('Error saving message:', error);
    }
  }

  async clearConversationHistory(): Promise<void> {
    try {
      // TODO: Implement with AsyncStorage
      // await AsyncStorage.removeItem('chat_history');
      // await AsyncStorage.removeItem('chat_context');
      
      console.log('Conversation history cleared');
    } catch (error) {
      console.error('Error clearing conversation history:', error);
    }
  }

  // =============================================================================
  // CONTEXT MANAGEMENT
  // =============================================================================

  async updateChatContext(context: Partial<ChatContext>): Promise<void> {
    try {
      // TODO: Implement with AsyncStorage
      // const contextKey = 'chat_context';
      // const existingContext = await AsyncStorage.getItem(contextKey);
      // 
      // let currentContext: ChatContext = {};
      // if (existingContext) {
      //   currentContext = JSON.parse(existingContext);
      // }
      // 
      // const updatedContext = { ...currentContext, ...context };
      // await AsyncStorage.setItem(contextKey, JSON.stringify(updatedContext));
      
      console.log('Chat context updated:', context);
    } catch (error) {
      console.error('Error updating chat context:', error);
    }
  }

  async getChatContext(): Promise<ChatContext | null> {
    try {
      // TODO: Implement with AsyncStorage
      // const contextKey = 'chat_context';
      // const storedContext = await AsyncStorage.getItem(contextKey);
      // return storedContext ? JSON.parse(storedContext) : null;
      
      return null;
    } catch (error) {
      console.error('Error getting chat context:', error);
      return null;
    }
  }

  // =============================================================================
  // QUICK ACTIONS & SUGGESTIONS
  // =============================================================================

  async getQuickActions(): Promise<{
    route_planning: string[];
    general_transit: string[];
    sri_lanka_specific: string[];
    emergency: string[];
  }> {
    // Predefined quick actions for better UX
    return {
      route_planning: [
        "Plan route from Colombo to Kandy",
        "Find fastest route to airport",
        "Show bus routes to Galle",
        "Plan trip with train connections"
      ],
      general_transit: [
        "What are current bus fares?",
        "Train schedule for Main Line",
        "Traffic conditions in Colombo",
        "Best time to travel to avoid rush hour"
      ],
      sri_lanka_specific: [
        "How to use CTB buses?",
        "Railway station facilities",
        "Tuk-tuk vs Uber comparison",
        "Inter-city express bus routes"
      ],
      emergency: [
        "Emergency contact numbers",
        "Hospital locations near me",
        "Police stations in Colombo",
        "Tourist helpline information"
      ]
    };
  }

  async getSuggestions(query: string): Promise<string[]> {
    // Generate contextual suggestions based on partial query
    const suggestions: Record<string, string[]> = {
      "route": [
        "route from Colombo to Kandy",
        "route planning options",
        "route with least transfers"
      ],
      "bus": [
        "bus schedules",
        "bus fare information",
        "bus routes in Colombo",
        "bus station locations"
      ],
      "train": [
        "train timetables",
        "train booking process",
        "railway station facilities",
        "express train services"
      ],
      "fare": [
        "current fare prices",
        "fare comparison between modes",
        "student discounts available",
        "monthly pass options"
      ],
      "traffic": [
        "current traffic conditions",
        "traffic updates for Colombo",
        "best routes to avoid traffic",
        "peak hour timings"
      ]
    };

    const lowerQuery = query.toLowerCase();
    for (const [key, values] of Object.entries(suggestions)) {
      if (lowerQuery.includes(key)) {
        return values;
      }
    }

    return [
      "How can I help you with transit?",
      "Ask me about routes and fares",
      "Get real-time transit updates"
    ];
  }

  // =============================================================================
  // SPECIALIZED QUERIES
  // =============================================================================

  async askRouteQuestion(
    source: string, 
    destination: string, 
    additionalContext?: string
  ): Promise<APIResponse<ChatbotResponse>> {
    const question = `Plan a route from ${source} to ${destination}` + 
      (additionalContext ? `. Additional requirements: ${additionalContext}` : '');

    const context: ChatContext = {
      recent_searches: [`${source} to ${destination}`]
    };

    return this.askQuestion({ question, context });
  }

  async askFareQuestion(
    mode: string, 
    route?: string
  ): Promise<APIResponse<ChatbotResponse>> {
    let question = `What are the current fares for ${mode}`;
    if (route) {
      question += ` from ${route}`;
    }
    question += '?';

    return this.askQuestion({ question });
  }

  async askTrafficQuestion(area: string): Promise<APIResponse<ChatbotResponse>> {
    const question = `What are the current traffic conditions in ${area}? Any delays or disruptions?`;
    
    const context: ChatContext = {
      user_location: {
        name: area,
        latitude: 0, // TODO: Get actual coordinates
        longitude: 0
      }
    };

    return this.askQuestion({ question, context });
  }

  async askEmergencyQuestion(): Promise<APIResponse<ChatbotResponse>> {
    const question = "I need emergency assistance. Please provide emergency contact numbers and nearby facilities.";
    return this.askQuestion({ question, temperature: 0.3 }); // Lower temperature for factual info
  }

  // =============================================================================
  // FEEDBACK & ANALYTICS
  // =============================================================================

  async submitFeedback(data: {
    message_id: string;
    rating: 1 | 2 | 3 | 4 | 5;
    feedback_text?: string;
    was_helpful: boolean;
  }): Promise<APIResponse<{
    feedback_id: string;
    status: string;
    message: string;
  }>> {
    return apiClient.post('/chatbot/feedback', data);
  }

  async reportInaccuracy(data: {
    message_id: string;
    incorrect_information: string;
    correct_information?: string;
    category: 'route' | 'fare' | 'schedule' | 'other';
  }): Promise<APIResponse<{
    report_id: string;
    status: string;
    message: string;
  }>> {
    return apiClient.post('/chatbot/report-inaccuracy', data);
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  private async cacheConversation(question: string, response: ChatbotResponse): Promise<void> {
    try {
      // Save both user message and bot response
      const userMessage: ChatMessage = {
        id: `user_${Date.now()}`,
        text: question,
        is_user: true,
        timestamp: new Date()
      };

      const botMessage: ChatMessage = {
        id: `bot_${Date.now()}`,
        text: response.answer,
        is_user: false,
        timestamp: new Date()
      };

      await this.saveMessage(userMessage);
      await this.saveMessage(botMessage);

      // Update context if provided
      if (response.context) {
        await this.updateChatContext(response.context);
      }
    } catch (error) {
      console.error('Error caching conversation:', error);
    }
  }

  formatMessageForDisplay(message: ChatMessage): any {
    return {
      id: message.id,
      text: message.text,
      isUser: message.is_user,
      timestamp: message.timestamp,
      attachments: message.attachments || []
    };
  }

  async getTypingIndicator(): Promise<ChatMessage> {
    return {
      id: `typing_${Date.now()}`,
      text: 'Transit Assistant is typing...',
      is_user: false,
      timestamp: new Date(),
      is_typing: true
    };
  }

  async removeTypingIndicator(messages: ChatMessage[]): Promise<ChatMessage[]> {
    return messages.filter(message => !message.is_typing);
  }
}

export const chatbotService = new ChatbotService();
export default chatbotService;