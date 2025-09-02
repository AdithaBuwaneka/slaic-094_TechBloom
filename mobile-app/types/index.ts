export interface User {
  id: string;
  email: string;
  phone?: string;
  full_name: string;
  profile_picture?: string;
  role: 'user' | 'admin';
  status: 'active' | 'inactive' | 'suspended';
  preferred_language: string;
  preferred_transport_modes: string[];
  accessibility_needs: string[];
  fcm_token?: string;
  last_location?: {
    latitude: number;
    longitude: number;
    timestamp: string;
  };
  created_at: string;
  updated_at: string;
  last_login?: string;
  email_verified: boolean;
  phone_verified: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Location {
  latitude: number;
  longitude: number;
  address?: string;
  accuracy?: number;
}

export interface RouteStep {
  instruction: string;
  distance: string;
  duration: string;
  transport_mode: string;
  html_instructions?: string;
}

export interface RouteOption {
  id: string;
  summary: string;
  total_duration: string;
  total_distance: string;
  total_cost?: number;
  legs: RouteStep[];
  polyline?: string;
  departure_time?: string;
  arrival_time?: string;
}

export interface JourneyRequest {
  query: string;
  user_id?: string;
  language_preference?: string;
  accessibility_needs?: string[];
  budget_preference?: number;
  passenger_type?: string;
}

// Legacy interface for direct planning
export interface DirectJourneyRequest {
  origin: string;
  destination: string;
  transport_mode?: string;
  departure_time?: string;
}

export interface AIJourneyResponse {
  route_options: RouteOption[];
  disruption_analysis: {
    severity_level: string;
    user_message: string;
    alternative_routes?: RouteOption[];
  };
  personalized_recommendations: {
    recommended_routes: string[];
    personalization_reason: string;
  };
  fare_optimization: {
    total_cost: number;
    cheapest_route: string;
    cost_breakdown: Record<string, number>;
  };
  local_insights: {
    local_tips: string[];
    crowd_levels: string;
    weather_impact?: string;
  };
  multilingual_response: {
    primary_language_response: string;
    alternative_languages?: Record<string, string>;
  };
}

export interface PushNotification {
  id: string;
  title: string;
  body: string;
  data?: Record<string, any>;
  sent_at: string;
  read_at?: string;
  notification_type: string;
}

export interface OfflineData {
  routes: RouteOption[];
  locations: Location[];
  lastSync: string;
}

export interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  currentLocation: Location | null;
  language: string;
  theme: 'light' | 'dark';
  offlineData: OfflineData | null;
  notifications: PushNotification[];
  error: string | null;
}