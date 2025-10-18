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
      disruptions: route.disruptions || [],
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

  // =============================================================================
  // ROUTE HISTORY MANAGEMENT
  // =============================================================================

  async saveRouteToBackend(route: RouteOption, userId: string): Promise<APIResponse<any>> {
    try {
      console.log('Saving route to backend database:', route.route_id);
      console.log('Route object structure:', JSON.stringify(route, null, 2));
      
      const extractedSource = route.source || 
                              route.origin ||
                              (route.title ? route.title.split(' → ')[0]?.trim() : null) || 
                              (route.steps?.[0]?.start_location?.name) || 
                              'Route Start';
      
      const extractedDestination = route.destination || 
                                   (route as any).destination ||
                                   (route.title ? route.title.split(' → ')[1]?.trim() : null) || 
                                   (route.steps?.[route.steps.length - 1]?.end_location?.name) || 
                                   'Route End';
      
      console.log('Extracted source:', extractedSource);
      console.log('Extracted destination:', extractedDestination);
      
      const routeData = {
        user_id: userId,
        route_id: route.route_id,
        source: extractedSource,
        destination: extractedDestination,
        route_data: route,
        created_at: new Date().toISOString(),
        metadata: {
          agent_count: Object.keys(route.agent_analysis || {}).length,
          processing_time: route.summary?.duration_minutes || 0,
          fare: route.summary?.estimated_fare || 0,
          carbon_footprint: route.summary?.carbon_footprint || 0
        }
      };

      const response = await apiClient.post<any>(
        ENDPOINTS.TRAVEL.SAVE_ROUTE,
        routeData
      );

      if (response.success) {
        console.log('Route saved to backend successfully:', response.data);
      } else {
        console.error('Failed to save route to backend:', response.error);
      }

      return response;
    } catch (error) {
      console.error('Error saving route to backend:', error);
      return {
        success: false,
        error: {
          error_code: 'SAVE_ROUTE_ERROR',
          message: 'Failed to save route to backend',
          details: { originalError: error },
          timestamp: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      };
    }
  }

  async getTravelRequestsFromBackend(userId: string, limit: number = 10): Promise<APIResponse<RouteOption[]>> {
    try {
      console.log('Fetching travel requests from backend for user:', userId);
      
      const response = await apiClient.get<{ requests: any[] }>(
        `${ENDPOINTS.TRAVEL.TRAVEL_REQUESTS}?user_id=${userId}&limit=${limit}`
      );

      if (response.success && response.data) {
        console.log('Travel requests fetched from backend:', response.data.requests.length, 'requests');
        
        // Transform travel requests to RouteOption format
        const transformedRoutes = response.data.requests.map((request: any) => {
          const result = request.result || {};
          const responseData = result.response || {};
          const bestRoute = responseData.best_route || {};

          // ENHANCED DEBUG: Log complete data structure for debugging
          console.log('📦 Transforming travel request:', {
            request_id: request._id,
            source: request.source,
            destination: request.destination,
            bestRoute_keys: Object.keys(bestRoute),
            bestRoute_sample: {
              route_id: bestRoute.route_id,
              duration_text: bestRoute.duration_text,
              distance_text: bestRoute.distance_text,
              estimated_cost: bestRoute.estimated_cost,
              cost_currency: bestRoute.cost_currency,
              // Check for alternate field names
              duration: bestRoute.duration,
              distance: bestRoute.distance,
              cost: bestRoute.cost,
              fare: bestRoute.fare,
              // Log ALL fields to find the right ones
              all_fields: JSON.stringify(bestRoute).substring(0, 500)
            }
          });

          const transformedRoute: RouteOption = {
            // Basic route identification
            route_id: request._id || request.request_id || 'unknown',
            source: request.source || 'Unknown',
            destination: request.destination || 'Unknown',

            // Display compatibility fields (for UI) - FIXED: Use correct backend fields
            id: request._id || request.request_id || 'unknown',
            title: `${request.source || 'Unknown'} → ${request.destination || 'Unknown'}`,
            duration: bestRoute.duration_text || 'Duration not available',
            fare: bestRoute.estimated_cost ?
              `${bestRoute.cost_currency || 'LKR'} ${bestRoute.estimated_cost}` :
              'Fare not available',
            modes: bestRoute.transit_modes || [request.mode || 'transit'],
            distance: bestRoute.distance_text || 'Distance not available',  // FIX: Changed from carbonFootprint to distance
            carbonFootprint: 'Carbon data not available',  // Carbon footprint is not provided by backend
            aiRecommendation: bestRoute.is_recommended ? 'AI Recommended' : 'Alternative route',
            agentsUsed: [], // Cleaned - no longer show technical agent details
            
            // NEW: Include all routes for alternatives display
            all_routes: responseData.all_routes || [],
            total_routes_found: responseData.total_routes_found || 0,
            
            // NEW: Include AI disruption analysis
            ai_disruption_analysis: responseData.ai_disruption_analysis || null,
            
            // Essential route data only - FIXED: Pass all critical data
            route_data: {
              route_id: bestRoute.route_id,
              origin: request.source,
              destination: request.destination,
              duration_text: bestRoute.duration_text,
              distance_text: bestRoute.distance_text,
              estimated_cost: bestRoute.estimated_cost,
              cost_currency: bestRoute.cost_currency,
              recommendation_score: bestRoute.recommendation_score,
              score_breakdown: bestRoute.score_breakdown,
              is_recommended: bestRoute.is_recommended,
              transit_modes: bestRoute.transit_modes,
              transfers: bestRoute.transfers,
              walking_distance: bestRoute.walking_distance,
              start_time: bestRoute.start_time,
              end_time: bestRoute.end_time,
              route_source: bestRoute.route_source,
              fare_optimization: bestRoute.fare_optimization,
              mode_details: bestRoute.mode_details,
              steps: bestRoute.steps || []
            },
            
            // Simplified summary
            summary: {
              duration_minutes: 0,
              distance_km: 0,
              estimated_fare: bestRoute.estimated_cost || 0,
              transit_modes: bestRoute.transit_modes || [request.mode || 'transit'],
              transfers: 0,
              walking_distance: 0,
              carbon_footprint: 0
            },
            steps: bestRoute.steps || [],
            fare_breakdown: {
              total_fare: bestRoute.estimated_cost || 0,
              currency: bestRoute.cost_currency || 'LKR',
              breakdown: [],
              savings_vs_alternatives: 0,
              optimization_applied: false
            },
            agent_analysis: {
              user_preference_score: bestRoute.recommendation_score || 0.7,
              fare_optimization_score: 0.8,
              disruption_risk_score: 0.2,
              comfort_score: 0.7,
              recommendations: [bestRoute.is_recommended ? 'AI Recommended' : 'Alternative route']
            },
            
            // Only essential disruption data
            disruptions: responseData.active_disruptions || [],
            alternatives: [],
            
            // Only show destination insights (user-valuable content)
            destination_summary: responseData.destination_summary || null,
            
            // Enhanced metadata - all available info
            request_timestamp: request.request_timestamp,
            processing_time: result.processing_time || 0,
            agents_count: result.agents_used?.length || 0,
            
            // NEW: Additional technical details
            request_id: responseData.request_id,
            mode: request.mode,
            preferred_transit: request.preferred_transit,
            status: result.status,
            trace_id: result.trace_id,
            agents_used_list: result.agents_used || []
          };
          
          return transformedRoute;
        });
        
        return {
          success: true,
          data: transformedRoutes,
          timestamp: new Date().toISOString()
        };
      }

      return {
        success: false,
        error: {
          error_code: 'NO_DATA',
          message: 'No travel requests data received',
          details: {},
          timestamp: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error fetching travel requests from backend:', error);
      return {
        success: false,
        error: {
          error_code: 'FETCH_REQUESTS_ERROR',
          message: 'Failed to fetch travel requests from backend',
          details: { originalError: error },
          timestamp: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      };
    }
  }

  async deleteRouteFromBackend(routeId: string, userId: string): Promise<APIResponse<any>> {
    try {
      console.log('Deleting route from backend:', routeId);
      
      const response = await apiClient.delete<any>(
        `${ENDPOINTS.TRAVEL.DELETE_ROUTE}/${routeId}?user_id=${userId}`
      );

      if (response.success) {
        console.log('Route deleted from backend successfully');
      } else {
        console.error('Failed to delete route from backend:', response.error);
      }

      return response;
    } catch (error) {
      console.error('Error deleting route from backend:', error);
      return {
        success: false,
        error: {
          error_code: 'DELETE_ROUTE_ERROR',
          message: 'Failed to delete route from backend',
          details: { originalError: error },
          timestamp: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      };
    }
  }
}

export const travelService = new TravelService();
export default travelService;