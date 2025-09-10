// =============================================================================
// TRAVEL SERVICE - Multi-Agent Route Planning Integration
// =============================================================================

import { apiClient } from './client';
import { ENDPOINTS } from './config';
import { 
  RouteRequest, 
  TravelResponse, 
  RouteOption, 
  DisruptionAlert,
  APIResponse,
  CommunityReport,
  UserPreferences
} from '../../types';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { webSocketService } from '../websocket/WebSocketService';

class TravelService {
  // =============================================================================
  // MULTI-AGENT ROUTE PLANNING
  // =============================================================================

  async planRoute(request: RouteRequest): Promise<APIResponse<TravelResponse>> {
    try {
      console.log('Planning route with AI agents:', request);
      
      const response = await apiClient.post<TravelResponse>(
        ENDPOINTS.TRAVEL.PLAN_ROUTE, 
        request,
        { timeout: 60000 } // 60 seconds for AI processing
      );
      
      if (response.success && response.data) {
        // Cache the route result for offline access
        await this.cacheRouteResult(response.data);
        
        // Update user preference learning
        await this.updateUserPreferenceLearning(request, response.data);
      }
      
      return response;
    } catch (error) {
      console.error('Route planning error:', error);
      throw error;
    }
  }

  async selectRoute(routeSelection: {
    user_id: string;
    route_id: string;
    source: string;
    destination: string;
    mode: string;
    selected_route_data: any;
    selection_reason?: string;
    request_id?: string;
  }): Promise<APIResponse<{
    user_id: string;
    status: string;
    message: string;
    updated_preferences: any;
    timestamp: string;
  }>> {
    try {
      const response = await apiClient.post<{
        user_id: string;
        status: string;
        message: string;
        updated_preferences: any;
        timestamp: string;
      }>(ENDPOINTS.TRAVEL.SELECT_ROUTE, routeSelection);
      
      if (response.success) {
        console.log('Route selection recorded, preferences updated');
      }
      
      return response;
    } catch (error) {
      console.error('Route selection error:', error);
      throw error;
    }
  }

  // =============================================================================
  // USER PREFERENCES
  // =============================================================================

  async getUserPreferences(userId: string): Promise<APIResponse<{
    user_id: string;
    preferences: any;
    route_history: any[];
    last_updated?: string;
    route_selection_count: number;
  }>> {
    return apiClient.get(`${ENDPOINTS.TRAVEL.USER_PREFERENCES}/${userId}`);
  }

  async updateUserPreferences(userId: string, preferences: UserPreferences): Promise<APIResponse<any>> {
    return apiClient.put(`${ENDPOINTS.TRAVEL.USER_PREFERENCES}/${userId}`, preferences);
  }

  // =============================================================================
  // DISRUPTION MONITORING
  // =============================================================================

  async reportDisruption(disruption: {
    user_id: string;
    route_id: string;
    location: string;
    disruption_type: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    description: string;
    affected_routes: string[];
  }): Promise<APIResponse<{
    disruption_id: string;
    status: string;
    message: string;
    alternative_routes: RouteOption[];
    timestamp: string;
  }>> {
    return apiClient.post(ENDPOINTS.TRAVEL.REPORT_DISRUPTION, disruption);
  }

  async getActiveDisruptions(): Promise<APIResponse<{
    active_disruptions_count: number;
    disruptions: DisruptionAlert[];
  }>> {
    return apiClient.get(ENDPOINTS.TRAVEL.ACTIVE_DISRUPTIONS);
  }

  // =============================================================================
  // SEARCH & TESTING
  // =============================================================================

  async testSearchFunctionality(): Promise<APIResponse<{
    status: string;
    message: string;
    test_queries: string[];
    results: any;
    timestamp: string;
  }>> {
    return apiClient.post(ENDPOINTS.TRAVEL.TEST_SEARCH);
  }

  async testLLMSummarizer(): Promise<APIResponse<{
    status: string;
    message: string;
    test_results: any;
    timestamp: string;
  }>> {
    return apiClient.post(ENDPOINTS.TRAVEL.TEST_LLM);
  }

  async searchRouteInformation(request: RouteRequest): Promise<APIResponse<{
    status: string;
    message: string;
    request_id: string;
    query: any;
    search_results: any;
    summary: any;
    timestamp: string;
  }>> {
    return apiClient.post(ENDPOINTS.TRAVEL.SEARCH_ROUTE_INFO, request);
  }

  // =============================================================================
  // CACHING & OFFLINE SUPPORT
  // =============================================================================

  private async cacheRouteResult(travelResponse: TravelResponse): Promise<void> {
    try {
      // TODO: Implement local caching with AsyncStorage
      // const cacheKey = `route_${travelResponse.request_id}`;
      // const cacheData = {
      //   ...travelResponse,
      //   cached_at: new Date().toISOString(),
      //   expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours
      // };
      // await AsyncStorage.setItem(cacheKey, JSON.stringify(cacheData));
      console.log('Route result cached:', travelResponse.request_id);
    } catch (error) {
      console.error('Error caching route result:', error);
    }
  }

  async getCachedRoutes(): Promise<TravelResponse[]> {
    try {
      // TODO: Implement cache retrieval
      // const keys = await AsyncStorage.getAllKeys();
      // const routeKeys = keys.filter(key => key.startsWith('route_'));
      // const cachedRoutes = await AsyncStorage.multiGet(routeKeys);
      // 
      // return cachedRoutes
      //   .map(([key, value]) => value ? JSON.parse(value) : null)
      //   .filter(route => route && new Date(route.expires_at) > new Date());
      
      return [];
    } catch (error) {
      console.error('Error getting cached routes:', error);
      return [];
    }
  }

  async clearExpiredCache(): Promise<void> {
    try {
      // TODO: Implement cache cleanup
      console.log('Cache cleanup completed');
    } catch (error) {
      console.error('Error clearing expired cache:', error);
    }
  }

  // =============================================================================
  // PREFERENCE LEARNING
  // =============================================================================

  private async updateUserPreferenceLearning(
    request: RouteRequest, 
    response: TravelResponse
  ): Promise<void> {
    try {
      // Extract learning signals from the route planning session
      const learningData = {
        user_id: request.user_id,
        search_context: {
          source: request.source,
          destination: request.destination,
          mode: request.mode,
          preferred_transit: request.preferred_transit,
          time_of_request: new Date().toISOString()
        },
        route_options_presented: response.response.recommended_routes?.length || 0,
        agents_used: response.agents_used,
        processing_time: response.processing_time,
        success: response.status === 'success'
      };

      // TODO: Send learning data to backend analytics
      console.log('User preference learning data:', learningData);
    } catch (error) {
      console.error('Error updating preference learning:', error);
    }
  }

  // =============================================================================
  // ROUTE OPTIMIZATION INSIGHTS
  // =============================================================================

  async getRouteOptimizationInsights(routeId: string): Promise<APIResponse<{
    route_id: string;
    optimization_applied: string[];
    savings: {
      time_saved_minutes: number;
      cost_saved: number;
      carbon_reduced_kg: number;
    };
    alternatives_considered: number;
    user_preference_match: number; // 0-1 score
  }>> {
    // This would be a custom endpoint for detailed optimization insights
    return apiClient.get(`/travel/route-insights/${routeId}`);
  }

  // =============================================================================
  // BATCH OPERATIONS
  // =============================================================================

  async planMultipleRoutes(requests: RouteRequest[]): Promise<APIResponse<TravelResponse[]>> {
    try {
      // Plan multiple routes in parallel for comparison
      const responses = await Promise.all(
        requests.map(request => this.planRoute(request))
      );

      return {
        data: responses.filter(r => r.success).map(r => r.data!),
        success: responses.some(r => r.success),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error planning multiple routes:', error);
      throw error;
    }
  }

  // =============================================================================
  // REAL-TIME UPDATES
  // =============================================================================

  async subscribeToRouteUpdates(routeId: string, callback: (update: any) => void): Promise<void> {
    try {
      // Subscribe to route-specific updates via WebSocket
      const subscriptionId = webSocketService.subscribeToRouteUpdates(routeId, callback);
      
      // Store subscription for cleanup
      await AsyncStorage.setItem(`route_subscription_${routeId}`, subscriptionId);
      
      console.log('Subscribed to route updates:', routeId, 'subscription:', subscriptionId);
    } catch (error) {
      console.error('Error subscribing to route updates:', error);
      throw error;
    }
  }

  async unsubscribeFromRouteUpdates(routeId: string): Promise<void> {
    try {
      // Get stored subscription ID
      const subscriptionId = await AsyncStorage.getItem(`route_subscription_${routeId}`);
      
      if (subscriptionId) {
        // Unsubscribe from WebSocket
        webSocketService.unsubscribe(subscriptionId);
        
        // Remove stored subscription
        await AsyncStorage.removeItem(`route_subscription_${routeId}`);
        
        console.log('Unsubscribed from route updates:', routeId, 'subscription:', subscriptionId);
      }
    } catch (error) {
      console.error('Error unsubscribing from route updates:', error);
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  formatRouteForDisplay(route: RouteOption): any {
    return {
      id: route.route_id,
      title: `${route.steps[0]?.start_location.name} → ${route.steps[route.steps.length - 1]?.end_location.name}`,
      duration: `${Math.round(route.summary.duration_minutes / 60)}h ${route.summary.duration_minutes % 60}m`,
      fare: `Rs. ${route.summary.estimated_fare}`,
      modes: route.summary.transit_modes,
      transfers: route.summary.transfers,
      walking: `${route.summary.walking_distance.toFixed(1)} km`,
      carbon: `${route.summary.carbon_footprint.toFixed(1)} kg CO₂`,
      agentRecommendation: route.agent_analysis.recommendations[0] || 'Optimized route',
      disruptions: route.disruptions.map(d => d.description),
      agentsUsed: Object.keys(route.agent_analysis).length
    };
  }

  calculateRouteSavings(route: RouteOption, alternatives: RouteOption[]): {
    time_saved: number;
    cost_saved: number;
    carbon_saved: number;
  } {
    if (alternatives.length === 0) {
      return { time_saved: 0, cost_saved: 0, carbon_saved: 0 };
    }

    const avgAlternative = {
      duration: alternatives.reduce((sum, alt) => sum + alt.summary.duration_minutes, 0) / alternatives.length,
      fare: alternatives.reduce((sum, alt) => sum + alt.summary.estimated_fare, 0) / alternatives.length,
      carbon: alternatives.reduce((sum, alt) => sum + alt.summary.carbon_footprint, 0) / alternatives.length,
    };

    return {
      time_saved: Math.max(0, avgAlternative.duration - route.summary.duration_minutes),
      cost_saved: Math.max(0, avgAlternative.fare - route.summary.estimated_fare),
      carbon_saved: Math.max(0, avgAlternative.carbon - route.summary.carbon_footprint),
    };
  }
}

export const travelService = new TravelService();
export default travelService;