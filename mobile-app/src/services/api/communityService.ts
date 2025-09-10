// =============================================================================
// COMMUNITY SERVICE - User Reports & Social Features
// =============================================================================

import { apiClient } from './client';
import { ENDPOINTS } from './config';
import { 
  CommunityReport,
  CommunityReportRequest,
  Location,
  APIResponse 
} from '../../types';

class CommunityService {
  // =============================================================================
  // TRAFFIC REPORTS
  // =============================================================================

  async reportTraffic(report: {
    location: string;
    location_coords: Location;
    traffic_level: 'light' | 'moderate' | 'heavy' | 'standstill';
    description?: string;
    estimated_delay_minutes?: number;
    affected_routes?: string[];
    images?: string[];
  }): Promise<APIResponse<{
    report_id: string;
    status: string;
    message: string;
    verification_status: 'pending' | 'auto_verified';
    estimated_impact: string;
  }>> {
    const trafficReport = {
      type: 'traffic' as const,
      title: `Traffic Update: ${report.traffic_level} in ${report.location}`,
      description: report.description || `${report.traffic_level} traffic reported`,
      location: report.location,
      location_coords: report.location_coords,
      severity: this.mapTrafficToSeverity(report.traffic_level),
      metadata: {
        traffic_level: report.traffic_level,
        estimated_delay_minutes: report.estimated_delay_minutes,
        affected_routes: report.affected_routes || []
      },
      images: report.images || []
    };

    return apiClient.post(ENDPOINTS.COMMUNITY.TRAFFIC, trafficReport);
  }

  async getTrafficReports(area?: string): Promise<APIResponse<{
    reports: CommunityReport[];
    active_reports_count: number;
    area_traffic_status: 'normal' | 'moderate' | 'heavy';
    last_updated: string;
  }>> {
    const endpoint = area 
      ? `${ENDPOINTS.COMMUNITY.TRAFFIC}?area=${encodeURIComponent(area)}`
      : ENDPOINTS.COMMUNITY.TRAFFIC;

    return apiClient.get(endpoint);
  }

  // =============================================================================
  // DELAY REPORTS
  // =============================================================================

  async reportDelay(report: {
    transport_type: 'bus' | 'train' | 'tuk-tuk' | 'other';
    route_number?: string;
    service_name?: string;
    location: string;
    location_coords: Location;
    delay_minutes: number;
    reason?: string;
    description?: string;
    expected_resolution?: string;
  }): Promise<APIResponse<{
    report_id: string;
    status: string;
    message: string;
    affected_users_notified: number;
    alternative_suggestions: string[];
  }>> {
    const delayReport = {
      type: 'delay' as const,
      title: `${report.transport_type.toUpperCase()} Delay: ${report.route_number || report.service_name}`,
      description: report.description || `${report.delay_minutes} min delay reported`,
      location: report.location,
      location_coords: report.location_coords,
      severity: this.mapDelayToSeverity(report.delay_minutes),
      metadata: {
        transport_type: report.transport_type,
        route_number: report.route_number,
        service_name: report.service_name,
        delay_minutes: report.delay_minutes,
        reason: report.reason,
        expected_resolution: report.expected_resolution
      }
    };

    return apiClient.post(ENDPOINTS.COMMUNITY.DELAYS, delayReport);
  }

  async getDelayReports(transportType?: string): Promise<APIResponse<{
    reports: CommunityReport[];
    total_active_delays: number;
    average_delay_minutes: number;
    most_affected_routes: string[];
    system_wide_status: 'normal' | 'minor_delays' | 'major_disruptions';
  }>> {
    const endpoint = transportType 
      ? `${ENDPOINTS.COMMUNITY.DELAYS}?transport_type=${transportType}`
      : ENDPOINTS.COMMUNITY.DELAYS;

    return apiClient.get(endpoint);
  }

  // =============================================================================
  // FARE REPORTS
  // =============================================================================

  async reportFareChange(report: {
    transport_type: 'bus' | 'train' | 'tuk-tuk' | 'uber';
    route?: string;
    old_fare?: number;
    new_fare: number;
    effective_date?: string;
    source: 'official' | 'observed' | 'driver_conductor';
    description?: string;
    location?: string;
    location_coords?: Location;
  }): Promise<APIResponse<{
    report_id: string;
    status: string;
    message: string;
    verification_required: boolean;
    similar_reports_count: number;
  }>> {
    const fareReport = {
      type: 'fare' as const,
      title: `Fare Update: ${report.transport_type.toUpperCase()} ${report.route || ''}`,
      description: report.description || `New fare: Rs. ${report.new_fare}`,
      location: report.location || `${report.transport_type} system-wide`,
      location_coords: report.location_coords,
      severity: 'medium' as const,
      metadata: {
        transport_type: report.transport_type,
        route: report.route,
        old_fare: report.old_fare,
        new_fare: report.new_fare,
        effective_date: report.effective_date || new Date().toISOString(),
        source: report.source
      }
    };

    return apiClient.post(ENDPOINTS.COMMUNITY.FARES, fareReport);
  }

  async getFareReports(): Promise<APIResponse<{
    reports: CommunityReport[];
    recent_changes_count: number;
    fare_trends: {
      transport_type: string;
      trend: 'increasing' | 'decreasing' | 'stable';
      average_change_percentage: number;
    }[];
    last_updated: string;
  }>> {
    return apiClient.get(ENDPOINTS.COMMUNITY.FARES);
  }

  // =============================================================================
  // ACCESSIBILITY REPORTS
  // =============================================================================

  async reportAccessibility(report: {
    location: string;
    location_coords: Location;
    accessibility_type: 'wheelchair' | 'visual_impairment' | 'hearing_impairment' | 'mobility_aid' | 'elderly_friendly';
    issue_type: 'facility_unavailable' | 'facility_broken' | 'no_assistance' | 'access_blocked' | 'other';
    description: string;
    severity: 'low' | 'medium' | 'high';
    transport_mode?: string;
    route_number?: string;
    station_stop_name?: string;
    images?: string[];
  }): Promise<APIResponse<{
    report_id: string;
    status: string;
    message: string;
    priority_level: 'low' | 'medium' | 'high' | 'urgent';
    estimated_resolution_time: string;
  }>> {
    const accessibilityReport = {
      type: 'accessibility' as const,
      title: `Accessibility Issue: ${report.accessibility_type} - ${report.location}`,
      description: report.description,
      location: report.location,
      location_coords: report.location_coords,
      severity: report.severity,
      metadata: {
        accessibility_type: report.accessibility_type,
        issue_type: report.issue_type,
        transport_mode: report.transport_mode,
        route_number: report.route_number,
        station_stop_name: report.station_stop_name
      },
      images: report.images || []
    };

    return apiClient.post(ENDPOINTS.COMMUNITY.ACCESSIBILITY, accessibilityReport);
  }

  async getAccessibilityReports(): Promise<APIResponse<{
    reports: CommunityReport[];
    accessibility_score_by_area: {
      area: string;
      score: number; // 0-10 scale
      common_issues: string[];
    }[];
    recent_improvements: string[];
    priority_issues: CommunityReport[];
  }>> {
    return apiClient.get(ENDPOINTS.COMMUNITY.ACCESSIBILITY);
  }

  // =============================================================================
  // GENERAL COMMUNITY FEATURES
  // =============================================================================

  async submitReport(reportData: {
    type: 'traffic' | 'delay' | 'fare' | 'accessibility';
    title: string;
    description: string;
    location: string;
    severity: 'low' | 'medium' | 'high';
    user_id: string;
  }): Promise<APIResponse<{
    report_id: string;
    status: string;
    message: string;
  }>> {
    const report = {
      ...reportData,
      location_coords: {
        latitude: 6.9271, // Default to Colombo
        longitude: 79.8612
      },
      metadata: {
        submitted_via: 'mobile_app',
        app_version: '1.0.0'
      }
    };

    // Route to appropriate endpoint based on type
    const endpointMap = {
      'traffic': ENDPOINTS.COMMUNITY.TRAFFIC,
      'delay': ENDPOINTS.COMMUNITY.DELAYS,
      'fare': ENDPOINTS.COMMUNITY.FARES,
      'accessibility': ENDPOINTS.COMMUNITY.ACCESSIBILITY
    };

    return apiClient.post(endpointMap[reportData.type], report);
  }

  async getAllReports(filters?: {
    type?: CommunityReport['type'];
    severity?: CommunityReport['severity'];
    status?: CommunityReport['status'];
    location?: string;
    limit?: number;
    offset?: number;
  }): Promise<APIResponse<{
    reports: CommunityReport[];
    total_count: number;
    active_count: number;
    resolved_count: number;
    filters_applied: any;
  }>> {
    const queryParams = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }

    const endpoint = `/community/reports${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return apiClient.get(endpoint);
  }

  async voteOnReport(reportId: string, vote: 'helpful' | 'not_helpful'): Promise<APIResponse<{
    report_id: string;
    vote_recorded: boolean;
    new_vote_count: number;
    user_previous_vote?: string;
  }>> {
    return apiClient.post(`/community/reports/${reportId}/vote`, { vote });
  }

  async getMyReports(): Promise<APIResponse<{
    reports: CommunityReport[];
    total_reports: number;
    verified_reports: number;
    reputation_score: number;
    contribution_stats: {
      traffic_reports: number;
      delay_reports: number;
      fare_reports: number;
      accessibility_reports: number;
    };
  }>> {
    return apiClient.get('/community/my-reports');
  }

  async updateReport(reportId: string, updates: {
    status?: 'resolved' | 'still_active';
    additional_info?: string;
    images?: string[];
  }): Promise<APIResponse<{
    report_id: string;
    status: string;
    message: string;
    updated_fields: string[];
  }>> {
    return apiClient.patch(`/community/reports/${reportId}`, updates);
  }

  // =============================================================================
  // REAL-TIME COMMUNITY FEATURES
  // =============================================================================

  async getNearbyReports(location: Location, radiusKm: number = 5): Promise<APIResponse<{
    reports: CommunityReport[];
    total_nearby: number;
    urgent_issues: number;
    area_status: 'normal' | 'some_issues' | 'major_disruptions';
  }>> {
    return apiClient.get(`/community/nearby?lat=${location.latitude}&lng=${location.longitude}&radius=${radiusKm}`);
  }

  async subscribeToAreaUpdates(area: string): Promise<APIResponse<{
    subscription_id: string;
    status: string;
    message: string;
    notification_types: string[];
  }>> {
    return apiClient.post('/community/subscribe', { area });
  }

  async unsubscribeFromAreaUpdates(subscriptionId: string): Promise<APIResponse<{
    status: string;
    message: string;
  }>> {
    return apiClient.delete(`/community/subscribe/${subscriptionId}`);
  }

  // =============================================================================
  // COMMUNITY STATISTICS & INSIGHTS
  // =============================================================================

  async getCommunityStats(): Promise<APIResponse<{
    total_active_users: number;
    reports_last_24h: number;
    most_reported_issues: {
      type: string;
      count: number;
      trend: 'increasing' | 'decreasing' | 'stable';
    }[];
    top_contributors: {
      user_id: string;
      username: string;
      reports_count: number;
      reputation_score: number;
    }[];
    area_rankings: {
      area: string;
      issue_density: number;
      resolution_time_avg: number;
    }[];
  }>> {
    return apiClient.get('/community/stats');
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  private mapTrafficToSeverity(trafficLevel: string): CommunityReport['severity'] {
    switch (trafficLevel) {
      case 'light': return 'low';
      case 'moderate': return 'medium';
      case 'heavy': return 'high';
      case 'standstill': return 'high';
      default: return 'medium';
    }
  }

  private mapDelayToSeverity(delayMinutes: number): CommunityReport['severity'] {
    if (delayMinutes < 10) return 'low';
    if (delayMinutes < 30) return 'medium';
    return 'high';
  }

  formatReportForDisplay(report: CommunityReport): any {
    return {
      id: report.id,
      title: report.title,
      description: report.description,
      type: report.type,
      severity: report.severity,
      location: report.location,
      status: report.status,
      reportedAt: report.reported_at,
      votes: report.votes,
      userVoted: report.user_voted,
      verificationStatus: report.verification_status,
      hasImages: (report.images && report.images.length > 0),
      timeAgo: this.formatTimeAgo(report.reported_at)
    };
  }

  private formatTimeAgo(timestamp: string): string {
    const now = new Date();
    const reported = new Date(timestamp);
    const diffMs = now.getTime() - reported.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  }

  getSeverityColor(severity: CommunityReport['severity']): string {
    switch (severity) {
      case 'low': return '#10B981'; // Green
      case 'medium': return '#F59E0B'; // Yellow
      case 'high': return '#EF4444'; // Red
      default: return '#6B7280'; // Gray
    }
  }

  getTypeIcon(type: CommunityReport['type']): string {
    switch (type) {
      case 'traffic': return '🚦';
      case 'delay': return '⏰';
      case 'fare': return '💰';
      case 'accessibility': return '♿';
      case 'safety': return '🛡️';
      default: return '📍';
    }
  }
}

export const communityService = new CommunityService();
export default communityService;