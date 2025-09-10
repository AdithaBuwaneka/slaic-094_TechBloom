// =============================================================================
// API CLIENT - Backend Integration
// =============================================================================

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Admin authentication
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post('/auth/login', { email, password });
    return response.data;
  },
  
  verifyToken: async () => {
    const response = await apiClient.get('/auth/verify-token');
    return response.data;
  }
};

// Dashboard data
export const dashboardAPI = {
  getOverview: async () => {
    const response = await apiClient.get('/admin/dashboard');
    return response.data;
  },
  
  getSystemHealth: async () => {
    const response = await apiClient.get('/admin/system-health');
    return response.data;
  }
};

// User management
export const userAPI = {
  getUsers: async (params?: { skip?: number; limit?: number; search?: string }) => {
    const response = await apiClient.get('/admin/users', { params });
    return response.data;
  },
  
  getUserDetails: async (userId: string) => {
    const response = await apiClient.get(`/admin/users/${userId}`);
    return response.data;
  },
  
  updateUserStatus: async (userId: string, isActive: boolean, reason?: string) => {
    const response = await apiClient.put(`/admin/users/${userId}/status`, {
      user_id: userId,
      is_active: isActive,
      reason
    });
    return response.data;
  }
};

// Community reports
export const communityAPI = {
  getReports: async (params?: { skip?: number; limit?: number; report_type?: string }) => {
    const response = await apiClient.get('/admin/community/reports', { params });
    return response.data;
  }
};

// Analytics
export const analyticsAPI = {
  getUserGrowth: async (days: number = 30) => {
    const response = await apiClient.get(`/admin/analytics/user-growth?days=${days}`);
    return response.data;
  },
  
  getTravelModes: async () => {
    const response = await apiClient.get('/admin/analytics/travel-modes');
    return response.data;
  },
  
  getApiUsage: async (days: number = 7) => {
    const response = await apiClient.get(`/admin/analytics/api-usage?days=${days}`);
    return response.data;
  }
};

// Agent system
export const agentAPI = {
  getWorkflow: async () => {
    const response = await apiClient.get('/admin/agent-system/workflow');
    return response.data;
  }
};

// Notifications
export const notificationAPI = {
  sendBroadcast: async (title: string, body: string, data?: any, userIds?: string[]) => {
    const response = await apiClient.post('/admin/notifications/broadcast', {
      title,
      body,
      data,
      user_ids: userIds
    });
    return response.data;
  }
};

// Admin settings
export const settingsAPI = {
  getSettings: async () => {
    const response = await apiClient.get('/admin/settings');
    return response.data;
  },
  
  updateSettings: async (settings: any) => {
    const response = await apiClient.put('/admin/settings', settings);
    return response.data;
  },
  
  resetSettings: async () => {
    const response = await apiClient.post('/admin/settings/reset');
    return response.data;
  }
};

export default apiClient;