// =============================================================================
// TYPE DEFINITIONS - Admin Dashboard
// =============================================================================

// Dashboard Overview
export interface DashboardOverview {
  total_users: number;
  active_users: number;
  total_trips_planned: number;
  route_history_count: number;
  total_community_reports: number;
  system_health: SystemHealth;
  recent_activity: RecentActivity[];
}

export interface SystemHealth {
  database: string;
  api_services: string;
  last_check: string;
}

export interface RecentActivity {
  type: string;
  description: string;
  timestamp: string;
  user_email: string;
  role: string;
}

// User Management
export interface User {
  user_id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login: string | null;
  email_verified: boolean;
  profile: UserProfile;
  travel_preferences: TravelPreferences;
  usage_stats: UsageStats;
  preferences_setup_completed?: boolean;
  preferences_setup_date?: string;
}

export interface UserProfile {
  avatar_url: string | null;
  phone: string | null;
  date_of_birth: string | null;
  preferred_language: string;
  notification_preferences: NotificationPreferences;
}

export interface NotificationPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  delay_alerts?: boolean;
  fare_alerts?: boolean;
  reminder_notifications?: boolean;
}

export interface TravelPreferences {
  preferred_transit_modes: string[];
  max_walking_distance: number;
  budget_preference: string;
  time_vs_cost_weight: number;
  comfort_preference: number;
  accessibility_needs: string[];
  avoid_preferences: string[];
  default_departure_buffer: number;
}

export interface UsageStats {
  total_trips_planned: number;
  favorite_destinations: string[];
  most_used_mode: string | null;
  total_distance_traveled: number;
  total_fare_saved: number;
}

// Community Reports
export interface CommunityReport {
  _id: string;
  report_id: string;
  type: 'traffic' | 'delay' | 'fare_update' | 'accessibility';
  location: string;
  severity?: string;
  description: string;
  user_id: string | null;
  reported_at: string;
  status: 'active' | 'resolved' | 'verified';
  votes: number;
  reliability_score: number;
  verified: boolean;
  // Delay-specific fields
  route?: string;
  mode?: string;
  delay_minutes?: number;
  estimated_clearance?: string;
}

// Analytics
export interface UserGrowthData {
  period_days: number;
  total_new_users: number;
  daily_growth: DailyGrowth[];
}

export interface DailyGrowth {
  date: string;
  new_users: number;
}

export interface TravelModePreferences {
  travel_mode_preferences: TravelModeData[];
}

export interface TravelModeData {
  mode: string;
  user_count: number;
}

export interface ApiUsageData {
  period_days: number;
  total_travel_requests: number;
  mode_usage: ModeUsage[];
}

export interface ModeUsage {
  mode: string;
  requests: number;
}

// Agent System
export interface AgentSystemWorkflow {
  mermaid_diagram: string;
  agent_details: AgentDetail[];
  system_stats: AgentSystemStats;
  integrated_tools: IntegratedTool[];
  workflow_description: WorkflowDescription;
}

export interface AgentDetail {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive';
  execution_time_avg: string;
  success_rate: number;
}

export interface AgentSystemStats {
  total_agents: number;
  active_agents: number;
  average_workflow_time: string;
  workflow_success_rate: number;
  total_requests_processed: number;
  requests_last_24h: number;
  most_used_path: string;
  multi_agent_usage_rate: number;
}

export interface IntegratedTool {
  name: string;
  status: 'healthy' | 'unhealthy';
  usage: string;
}

export interface WorkflowDescription {
  name: string;
  version: string;
  description: string;
  key_features: string[];
  sri_lankan_optimizations: string[];
}

// Auth
export interface AdminLoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// API Response wrapper
export interface ApiResponse<T = Record<string, unknown>> {
  success?: boolean;
  data?: T;
  error?: {
    message: string;
    code?: string;
  };
  message?: string;
}