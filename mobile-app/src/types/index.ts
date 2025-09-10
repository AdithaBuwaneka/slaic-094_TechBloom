// =============================================================================
// CORE TYPES - Transit Companion Mobile App
// =============================================================================

export interface User {
  user_id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';
  is_active: boolean;
  created_at: string;
  profile: UserProfile;
  travel_preferences: TravelPreferences;
  usage_stats: UsageStats;
}

export interface UserProfile {
  avatar_url?: string;
  phone?: string;
  date_of_birth?: string;
  preferred_language: 'en' | 'si' | 'ta';
  notification_preferences: NotificationPreferences;
}

export interface NotificationPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
}

export interface TravelPreferences {
  preferred_transit_modes: string[];
  max_walking_distance: number;
  budget_preference: 'low' | 'medium' | 'high';
  time_vs_cost_weight: number;
  comfort_preference: number;
  accessibility_needs: string[];
  avoid_preferences: string[];
  default_departure_buffer: number;
}

// Alias for backward compatibility
export type UserPreferences = TravelPreferences;

export interface UsageStats {
  total_trips_planned: number;
  favorite_destinations: string[];
  most_used_mode?: string;
  total_distance_traveled: number;
  total_fare_saved: number;
}

// =============================================================================
// AUTHENTICATION TYPES
// =============================================================================

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  phone?: string;
  preferred_language?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  is_new_user?: boolean;
  requires_preferences_setup?: boolean;
}

// =============================================================================
// ROUTE PLANNING TYPES (Backend Integration)
// =============================================================================

export interface RouteRequest {
  user_id: string;
  source: string;
  destination: string;
  mode: SriLankanTravelMode;
  preferred_transit?: string;
  departure_time?: string;
}

export interface TravelResponse {
  request_id: string;
  status: string;
  response: TravelResponseData;
  processing_time: number;
  agents_used: string[];
  trace_id?: string;
}

export interface TravelResponseData {
  request_id: string;
  recommended_routes: RouteOption[];
  agent_summary: AgentSummary;
  disruption_alerts: DisruptionAlert[];
  fare_optimization: FareOptimization;
  local_insights: LocalInsight[];
  
  // Backend response structure properties
  best_route?: RouteOption;
  all_routes?: RouteOption[];
  total_routes_found?: number;
}

export interface RouteOption {
  route_id: string;
  summary: RouteSummary;
  steps: RouteStep[];
  fare_breakdown: FareBreakdown;
  agent_analysis: AgentAnalysis;
  disruptions: string[]; // Simplified for UI display
  alternatives: AlternativeOption[];
  
  // Display properties for UI compatibility
  id: string;
  title: string;
  duration: string;
  fare: string;
  modes: string[];
  carbonFootprint: string;
  aiRecommendation: string;
  agentsUsed: string[];
}

export interface RouteSummary {
  duration_minutes: number;
  distance_km: number;
  estimated_fare: number;
  transit_modes: string[];
  transfers: number;
  walking_distance: number;
  carbon_footprint: number;
}

export interface RouteStep {
  step_id: string;
  type: 'walking' | 'transit' | 'waiting';
  mode: string;
  instruction: string;
  duration_minutes: number;
  distance_km?: number;
  fare?: number;
  start_location: Location;
  end_location: Location;
  polyline?: string;
}

export interface Location {
  name: string;
  latitude: number;
  longitude: number;
  address?: string;
}

export interface FareBreakdown {
  total_fare: number;
  currency: string;
  breakdown: FareComponent[];
  savings_vs_alternatives: number;
  optimization_applied: boolean;
}

export interface FareComponent {
  mode: string;
  description: string;
  amount: number;
  discount_applied?: boolean;
}

// =============================================================================
// AI AGENT TYPES
// =============================================================================

export interface AgentSummary {
  total_agents_used: number;
  processing_time_seconds: number;
  agents_completed: string[];
  optimization_level: 'basic' | 'standard' | 'maximum';
}

export interface AgentAnalysis {
  user_preference_score: number;
  fare_optimization_score: number;
  disruption_risk_score: number;
  comfort_score: number;
  recommendations: string[];
}

export interface AgentStatus {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  result?: string;
  processing_time?: number;
}

// =============================================================================
// SRI LANKAN TRANSIT TYPES
// =============================================================================

export enum SriLankanTravelMode {
  DRIVING = 'driving',
  TWO_WHEELER = 'two_wheeler',
  TRANSIT = 'transit',
  TRAIN = 'train',
  BUS = 'bus',
  TUK_TUK = 'tuk-tuk',
  UBER = 'uber',
  WALKING = 'walking'
}

export interface SriLankanTransitData {
  railways: RailwayData;
  buses: BusData;
  tuk_tuks: TukTukData;
}

export interface RailwayData {
  lines: RailwayLine[];
  real_time_updates: TrainUpdate[];
}

export interface RailwayLine {
  line_id: string;
  name: string;
  stations: Station[];
  schedule: TrainSchedule[];
}

export interface Station {
  station_id: string;
  name: string;
  location: Location;
  facilities: string[];
}

export interface TrainSchedule {
  train_id: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  fare_classes: FareClass[];
}

export interface FareClass {
  class_name: string;
  fare: number;
  amenities: string[];
}

export interface TrainUpdate {
  train_id: string;
  status: 'on_time' | 'delayed' | 'cancelled';
  delay_minutes?: number;
  current_location?: string;
  next_station?: string;
}

export interface BusData {
  routes: BusRoute[];
  real_time_updates: BusUpdate[];
}

export interface BusRoute {
  route_id: string;
  route_number: string;
  operator: string;
  origin: string;
  destination: string;
  stops: BusStop[];
  schedule: BusSchedule[];
  fare: number;
}

export interface BusStop {
  stop_id: string;
  name: string;
  location: Location;
  facilities: string[];
}

export interface BusSchedule {
  departure_time: string;
  frequency_minutes: number;
  duration_minutes: number;
}

export interface BusUpdate {
  route_id: string;
  bus_number: string;
  status: 'running' | 'delayed' | 'breakdown';
  current_location?: string;
  delay_minutes?: number;
}

export interface TukTukData {
  availability: TukTukAvailability[];
  fare_estimates: TukTukFare[];
}

export interface TukTukAvailability {
  location: Location;
  available_count: number;
  estimated_wait_minutes: number;
}

export interface TukTukFare {
  distance_km: number;
  estimated_fare: number;
  surge_multiplier?: number;
}

// =============================================================================
// DISRUPTION & ALERT TYPES
// =============================================================================

export interface DisruptionAlert {
  disruption_id: string;
  type: 'traffic' | 'weather' | 'construction' | 'strike' | 'accident' | 'technical';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  affected_routes: string[];
  affected_area: Location;
  start_time: string;
  estimated_end_time?: string;
  alternative_suggestions: string[];
  source: 'official' | 'community' | 'ai_detected';
}

export interface DisruptionInfo {
  disruption_id: string;
  location: string;
  type: string;
  severity: string;
  reported_by: string;
  timestamp: string;
  affected_routes: string[];
  description: string;
  status: 'active' | 'resolved';
}

// =============================================================================
// COMMUNITY FEATURES TYPES
// =============================================================================

export interface CommunityReport {
  id: string;
  type: 'traffic' | 'delay' | 'fare' | 'accessibility' | 'safety';
  title: string;
  description: string;
  location: string;
  location_coords: Location;
  severity: 'low' | 'medium' | 'high';
  status: 'active' | 'resolved' | 'verified';
  reported_by: string;
  reported_at: string;
  votes: number;
  user_voted: boolean;
  images?: string[];
  verification_status: 'pending' | 'verified' | 'disputed';
}

export interface CommunityReportRequest {
  type: CommunityReport['type'];
  title: string;
  description: string;
  location: string;
  severity: CommunityReport['severity'];
  images?: string[];
}

// =============================================================================
// CHATBOT & RAG TYPES
// =============================================================================

export interface ChatMessage {
  id: string;
  text: string;
  is_user: boolean;
  timestamp: Date;
  is_typing?: boolean;
  attachments?: ChatAttachment[];
}

export interface ChatAttachment {
  type: 'route' | 'location' | 'fare' | 'image';
  data: any;
}

export interface ChatbotRequest {
  question: string;
  temperature?: number;
  context?: ChatContext;
}

export interface ChatbotResponse {
  question: string;
  answer: string;
  context?: ChatContext;
  suggestions?: string[];
}

export interface ChatContext {
  user_location?: Location;
  recent_searches?: string[];
  current_route?: RouteOption;
}

// =============================================================================
// MOBILE APP SPECIFIC TYPES
// =============================================================================

export interface DeviceRegistration {
  device_token: string;
  platform: 'ios' | 'android';
  app_version: string;
  device_info: DeviceInfo;
}

export interface DeviceInfo {
  model: string;
  os_version: string;
  app_build?: string;
}

export interface PushNotification {
  id: string;
  title: string;
  body: string;
  data?: Record<string, any>;
  type: 'route_update' | 'disruption' | 'fare_deal' | 'reminder' | 'community';
  priority: 'low' | 'normal' | 'high';
  scheduled_time?: string;
}

export interface OfflineData {
  routes: RouteOption[];
  user_preferences: TravelPreferences;
  frequent_locations: Location[];
  cached_at: string;
  expires_at: string;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

export interface APIError {
  error_code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface APIResponse<T> {
  data?: T;
  error?: APIError;
  success: boolean;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

// =============================================================================
// OPTIMIZATION & INSIGHTS TYPES
// =============================================================================

export interface FareOptimization {
  cheapest_option: RouteOption;
  savings_amount: number;
  optimization_techniques: string[];
  alternative_payments: PaymentOption[];
}

export interface PaymentOption {
  method: string;
  discount_percentage: number;
  description: string;
  conditions?: string[];
}

export interface LocalInsight {
  type: 'tip' | 'warning' | 'attraction' | 'food' | 'weather';
  title: string;
  description: string;
  location?: Location;
  relevance_score: number;
  source: string;
}

export interface AlternativeOption {
  option_id: string;
  description: string;
  estimated_savings: number;
  trade_offs: string[];
}

// =============================================================================
// ANALYTICS & TRACKING TYPES
// =============================================================================

export interface UserAnalytics {
  total_app_sessions: number;
  total_routes_planned: number;
  favorite_travel_mode: string;
  average_trip_distance: number;
  total_money_saved: number;
  carbon_footprint_reduced: number;
  most_visited_destinations: string[];
  app_usage_patterns: UsagePattern[];
}

export interface UsagePattern {
  day_of_week: string;
  peak_hours: number[];
  common_routes: string[];
  preferred_features: string[];
}

// =============================================================================
// MULTILINGUAL SUPPORT TYPES
// =============================================================================

export interface TranslationKey {
  en: string;
  si: string;
  ta: string;
}

export interface MultilingualContent {
  title: TranslationKey;
  description: TranslationKey;
  instructions?: TranslationKey;
}

export type SupportedLanguage = 'en' | 'si' | 'ta';

// =============================================================================
// EXPORT ALL TYPES
// =============================================================================

// All types are already exported above - no need to self-reference