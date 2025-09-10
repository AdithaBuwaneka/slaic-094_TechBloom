// =============================================================================
// API SERVICES - Central Export Hub
// =============================================================================

// Core API Client
export { apiClient, default as APIClient } from './client';
export * from './config';

// Service Classes
export { authService, default as AuthService } from './authService';
export { travelService, default as TravelService } from './travelService';
export { mobileService, default as MobileService } from './mobileService';
export { chatbotService, default as ChatbotService } from './chatbotService';
export { communityService, default as CommunityService } from './communityService';

// =============================================================================
// SERVICE REGISTRY - For Dependency Injection
// =============================================================================

export const services = {
  auth: authService,
  travel: travelService,
  mobile: mobileService,
  chatbot: chatbotService,
  community: communityService,
} as const;

// =============================================================================
// GLOBAL API INITIALIZATION
// =============================================================================

/**
 * Initialize API services with stored authentication token
 */
export async function initializeAPI(): Promise<void> {
  try {
    // Try to restore authentication state
    const user = await authService.attemptAutoLogin();
    if (user) {
      console.log('API initialized with authenticated user:', user.name);
    } else {
      console.log('API initialized - user not authenticated');
    }
  } catch (error) {
    console.error('API initialization error:', error);
  }
}

/**
 * Health check for all services
 */
export async function checkServicesHealth(): Promise<{
  backend: boolean;
  mobile: boolean;
  chatbot: boolean;
  overall: boolean;
}> {
  const results = {
    backend: false,
    mobile: false,
    chatbot: false,
    overall: false
  };

  try {
    // Check backend health
    const backendHealth = await apiClient.get('/health');
    results.backend = backendHealth.success;

    // Check mobile service health
    try {
      const mobileHealth = await mobileService.getHealthStatus();
      results.mobile = mobileHealth.success;
    } catch (error) {
      console.log('Mobile service health check failed:', error);
    }

    // Check chatbot health
    try {
      const chatbotHealth = await chatbotService.getChatbotHealth();
      results.chatbot = chatbotHealth.success;
    } catch (error) {
      console.log('Chatbot service health check failed:', error);
    }

    // Overall health
    results.overall = results.backend; // At minimum, backend must be healthy

    return results;
  } catch (error) {
    console.error('Services health check failed:', error);
    return results;
  }
}

/**
 * Clear all cached data and tokens
 */
export async function clearAllData(): Promise<void> {
  try {
    await Promise.all([
      authService.logout(),
      mobileService.clearCache(),
      chatbotService.clearConversationHistory(),
    ]);
    console.log('All data cleared successfully');
  } catch (error) {
    console.error('Error clearing data:', error);
  }
}

// =============================================================================
// ERROR HANDLING UTILITIES
// =============================================================================

/**
 * Check if an API error is due to authentication issues
 */
export function isAuthError(error: any): boolean {
  return error?.error?.error_code === 'UNAUTHORIZED' || 
         error?.status === 401;
}

/**
 * Check if an API error is due to network issues
 */
export function isNetworkError(error: any): boolean {
  return error?.error?.error_code === 'NETWORK_ERROR' ||
         error?.error?.error_code === 'TIMEOUT_ERROR';
}

/**
 * Check if an API error is a server error
 */
export function isServerError(error: any): boolean {
  return error?.error?.error_code === 'SERVER_ERROR' ||
         (error?.status >= 500 && error?.status < 600);
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: any): string {
  if (error?.error?.message) {
    return error.error.message;
  }

  if (isNetworkError(error)) {
    return 'Network connection failed. Please check your internet connection.';
  }

  if (isAuthError(error)) {
    return 'Authentication failed. Please log in again.';
  }

  if (isServerError(error)) {
    return 'Server error occurred. Please try again later.';
  }

  return 'An unexpected error occurred. Please try again.';
}

// =============================================================================
// ANALYTICS & TELEMETRY
// =============================================================================

/**
 * Report API usage for analytics
 */
export function reportAPIUsage(
  service: keyof typeof services,
  method: string,
  success: boolean,
  responseTimeMs?: number
): void {
  try {
    mobileService.reportPerformanceMetrics({
      screen_name: `api_${service}`,
      load_time_ms: responseTimeMs || 0,
      network_requests: 1,
      errors: success ? [] : [`${service}.${method} failed`]
    });
  } catch (error) {
    // Don't throw errors for analytics failures
    console.log('Analytics reporting failed:', error);
  }
}

// =============================================================================
// DEVELOPMENT HELPERS
// =============================================================================

if (__DEV__) {
  // Expose services globally for debugging in development
  (global as any).transitServices = services;
  (global as any).apiClient = apiClient;
  
  console.log('🔧 Development mode: API services exposed globally');
  console.log('Access via: global.transitServices.auth, global.apiClient, etc.');
}

export default services;