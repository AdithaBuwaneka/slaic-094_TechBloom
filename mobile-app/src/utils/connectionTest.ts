// =============================================================================
// CONNECTION TEST UTILITY - Backend Connectivity Validation
// =============================================================================

import { 
  apiClient, 
  chatbotService, 
  mobileService, 
  travelService,
  communityService
} from '../services/api';
import { authService } from '../services/api/authService';
import { webSocketService } from '../services/websocket/WebSocketService';
import { notificationService } from '../services/notifications/NotificationService';

export interface ConnectionTestResult {
  service: string;
  status: 'success' | 'error' | 'warning';
  message: string;
  responseTime?: number;
  details?: any;
}

export interface ConnectionTestSuite {
  overall: 'pass' | 'fail' | 'partial';
  results: ConnectionTestResult[];
  timestamp: string;
}

/**
 * Test all backend connections and services
 */
export async function testAllConnections(): Promise<ConnectionTestSuite> {
  const results: ConnectionTestResult[] = [];
  const startTime = Date.now();

  console.log('🔍 Starting comprehensive backend connection test...');

  // Test 1: Basic API connectivity
  results.push(await testAPIConnectivity());

  // Test 2: Authentication endpoints
  results.push(await testAuthEndpoints());

  // Test 3: Chatbot service
  results.push(await testChatbotService());

  // Test 4: Mobile services
  results.push(await testMobileServices());

  // Test 5: Travel service
  results.push(await testTravelService());

  // Test 6: Community service
  results.push(await testCommunityService());

  // Test 7: WebSocket connectivity
  results.push(await testWebSocketService());

  // Test 8: Notification service
  results.push(await testNotificationService());

  const totalTime = Date.now() - startTime;
  console.log(`✅ Backend connection test completed in ${totalTime}ms`);

  // Determine overall status
  const errorCount = results.filter(r => r.status === 'error').length;
  const warningCount = results.filter(r => r.status === 'warning').length;
  
  let overall: 'pass' | 'fail' | 'partial' = 'pass';
  if (errorCount > 0) {
    overall = errorCount >= results.length / 2 ? 'fail' : 'partial';
  } else if (warningCount > 0) {
    overall = 'partial';
  }

  return {
    overall,
    results,
    timestamp: new Date().toISOString()
  };
}

/**
 * Test basic API connectivity
 */
async function testAPIConnectivity(): Promise<ConnectionTestResult> {
  const startTime = Date.now();
  
  try {
    const response = await apiClient.get('/health');
    const responseTime = Date.now() - startTime;

    if (response.success) {
      return {
        service: 'API Base',
        status: 'success',
        message: 'API server is reachable and responding',
        responseTime,
        details: response.data
      };
    } else {
      return {
        service: 'API Base',
        status: 'error',
        message: response.error?.message || 'API health check failed',
        responseTime,
        details: response.error
      };
    }
  } catch (error) {
    return {
      service: 'API Base',
      status: 'error',
      message: 'Cannot reach API server',
      responseTime: Date.now() - startTime,
      details: error
    };
  }
}

/**
 * Test authentication endpoints
 */
async function testAuthEndpoints(): Promise<ConnectionTestResult> {
  const startTime = Date.now();
  
  try {
    // Test token verification endpoint (should fail without token, but should be reachable)
    const response = await authService.verifyToken();
    const responseTime = Date.now() - startTime;

    // We expect this to fail with 401 if not authenticated, which means the endpoint is working
    if (response.error?.error_code === 'UNAUTHORIZED') {
      return {
        service: 'Authentication',
        status: 'success',
        message: 'Auth endpoints are reachable (not authenticated)',
        responseTime
      };
    } else if (response.success) {
      return {
        service: 'Authentication',
        status: 'success',
        message: 'Auth endpoints working (user authenticated)',
        responseTime,
        details: response.data
      };
    } else {
      return {
        service: 'Authentication',
        status: 'warning',
        message: 'Auth endpoint responded unexpectedly',
        responseTime,
        details: response
      };
    }
  } catch (error) {
    return {
      service: 'Authentication',
      status: 'error',
      message: 'Cannot reach authentication endpoints',
      responseTime: Date.now() - startTime,
      details: error
    };
  }
}

/**
 * Test chatbot service
 */
async function testChatbotService(): Promise<ConnectionTestResult> {
  const startTime = Date.now();
  
  try {
    const healthResponse = await chatbotService.getChatbotHealth();
    const responseTime = Date.now() - startTime;

    if (healthResponse.success) {
      return {
        service: 'Chatbot (RAG)',
        status: 'success',
        message: 'Chatbot service is healthy',
        responseTime,
        details: healthResponse.data
      };
    } else {
      return {
        service: 'Chatbot (RAG)',
        status: 'error',
        message: healthResponse.error?.message || 'Chatbot health check failed',
        responseTime,
        details: healthResponse.error
      };
    }
  } catch (error) {
    return {
      service: 'Chatbot (RAG)',
      status: 'error',
      message: 'Cannot reach chatbot service',
      responseTime: Date.now() - startTime,
      details: error
    };
  }
}

/**
 * Test mobile services
 */
async function testMobileServices(): Promise<ConnectionTestResult> {
  const startTime = Date.now();
  
  try {
    const healthResponse = await mobileService.getHealthStatus();
    const responseTime = Date.now() - startTime;

    if (healthResponse.success) {
      return {
        service: 'Mobile Services',
        status: 'success',
        message: 'Mobile services are healthy',
        responseTime,
        details: healthResponse.data
      };
    } else {
      return {
        service: 'Mobile Services',
        status: 'warning',
        message: healthResponse.error?.message || 'Mobile service health check failed',
        responseTime,
        details: healthResponse.error
      };
    }
  } catch (error) {
    return {
      service: 'Mobile Services',
      status: 'error',
      message: 'Cannot reach mobile services',
      responseTime: Date.now() - startTime,
      details: error
    };
  }
}

/**
 * Test travel service (multi-agent system)
 */
async function testTravelService(): Promise<ConnectionTestResult> {
  const startTime = Date.now();
  
  try {
    // Test the search functionality endpoint
    const testResponse = await travelService.testSearchFunctionality();
    const responseTime = Date.now() - startTime;

    if (testResponse.success) {
      return {
        service: 'Travel Service (AI Agents)',
        status: 'success',
        message: 'Multi-agent travel service is operational',
        responseTime,
        details: testResponse.data
      };
    } else {
      return {
        service: 'Travel Service (AI Agents)',
        status: 'error',
        message: testResponse.error?.message || 'Travel service test failed',
        responseTime,
        details: testResponse.error
      };
    }
  } catch (error) {
    return {
      service: 'Travel Service (AI Agents)',
      status: 'error',
      message: 'Cannot reach travel service',
      responseTime: Date.now() - startTime,
      details: error
    };
  }
}

/**
 * Test community service
 */
async function testCommunityService(): Promise<ConnectionTestResult> {
  const startTime = Date.now();
  
  try {
    const statsResponse = await communityService.getCommunityStats();
    const responseTime = Date.now() - startTime;

    if (statsResponse.success) {
      return {
        service: 'Community Service',
        status: 'success',
        message: 'Community service is operational',
        responseTime,
        details: statsResponse.data
      };
    } else {
      return {
        service: 'Community Service',
        status: 'warning',
        message: statsResponse.error?.message || 'Community service test failed',
        responseTime,
        details: statsResponse.error
      };
    }
  } catch (error) {
    return {
      service: 'Community Service',
      status: 'error',
      message: 'Cannot reach community service',
      responseTime: Date.now() - startTime,
      details: error
    };
  }
}

/**
 * Test WebSocket service
 */
async function testWebSocketService(): Promise<ConnectionTestResult> {
  const startTime = Date.now();
  
  try {
    const isConnected = webSocketService.isConnected();
    
    if (isConnected) {
      return {
        service: 'WebSocket',
        status: 'success',
        message: 'WebSocket connection active',
        responseTime: Date.now() - startTime
      };
    } else {
      // Try to connect
      try {
        const connected = await webSocketService.connect();
        if (connected) {
          return {
            service: 'WebSocket',
            status: 'success',
            message: 'WebSocket connection established',
            responseTime: Date.now() - startTime
          };
        } else {
          return {
            service: 'WebSocket',
            status: 'warning',
            message: 'WebSocket connection failed',
            responseTime: Date.now() - startTime
          };
        }
      } catch (error) {
        return {
          service: 'WebSocket',
          status: 'error',
          message: 'Cannot establish WebSocket connection',
          responseTime: Date.now() - startTime,
          details: error
        };
      }
    }
  } catch (error) {
    return {
      service: 'WebSocket',
      status: 'error',
      message: 'WebSocket service error',
      responseTime: Date.now() - startTime,
      details: error
    };
  }
}

/**
 * Test notification service
 */
async function testNotificationService(): Promise<ConnectionTestResult> {
  const startTime = Date.now();
  
  try {
    const isInitialized = notificationService.isInitialized();
    const responseTime = Date.now() - startTime;

    if (isInitialized) {
      return {
        service: 'Push Notifications',
        status: 'success',
        message: 'Notification service initialized',
        responseTime,
        details: { 
          pushToken: notificationService.getPushToken() !== null 
        }
      };
    } else {
      return {
        service: 'Push Notifications',
        status: 'warning',
        message: 'Notification service not initialized (may require permissions)',
        responseTime
      };
    }
  } catch (error) {
    return {
      service: 'Push Notifications',
      status: 'error',
      message: 'Notification service error',
      responseTime: Date.now() - startTime,
      details: error
    };
  }
}

/**
 * Quick connectivity test for essential services only
 */
export async function quickConnectivityTest(): Promise<{
  api: boolean;
  chatbot: boolean;
  travel: boolean;
}> {
  const results = await Promise.allSettled([
    testAPIConnectivity(),
    testChatbotService(),
    testTravelService()
  ]);

  return {
    api: results[0].status === 'fulfilled' && results[0].value.status === 'success',
    chatbot: results[1].status === 'fulfilled' && results[1].value.status === 'success',
    travel: results[2].status === 'fulfilled' && results[2].value.status === 'success'
  };
}

/**
 * Format test results for display
 */
export function formatTestResults(testSuite: ConnectionTestSuite): string {
  const { overall, results, timestamp } = testSuite;
  
  let output = `\n🔍 Backend Connection Test Results (${timestamp})\n`;
  output += `Overall Status: ${overall === 'pass' ? '✅ PASS' : overall === 'partial' ? '⚠️ PARTIAL' : '❌ FAIL'}\n\n`;
  
  results.forEach(result => {
    const icon = result.status === 'success' ? '✅' : result.status === 'warning' ? '⚠️' : '❌';
    const time = result.responseTime ? ` (${result.responseTime}ms)` : '';
    output += `${icon} ${result.service}${time}: ${result.message}\n`;
  });
  
  return output;
}

/**
 * Log test results to console with proper formatting
 */
export function logTestResults(testSuite: ConnectionTestSuite): void {
  console.log(formatTestResults(testSuite));
  
  // Log detailed errors
  const errors = testSuite.results.filter(r => r.status === 'error' && r.details);
  if (errors.length > 0) {
    console.group('❌ Detailed Error Information:');
    errors.forEach(error => {
      console.error(`${error.service}:`, error.details);
    });
    console.groupEnd();
  }
}

export default testAllConnections;