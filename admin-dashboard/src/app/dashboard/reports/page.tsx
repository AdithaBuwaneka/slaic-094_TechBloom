'use client';

import { useState, useEffect } from 'react';
import { communityAPI } from '@/lib/api';
import { CommunityReport } from '@/lib/types';
import { 
  MessageSquare, 
  AlertTriangle, 
  Clock, 
  MapPin,
  CheckCircle,
  XCircle,
  Filter,
  Eye,
  Calendar
} from 'lucide-react';

export default function CommunityReportsPage() {
  const [reports, setReports] = useState<CommunityReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<CommunityReport | null>(null);
  const [filterType, setFilterType] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalReports, setTotalReports] = useState(0);
  const reportsPerPage = 10;

  useEffect(() => {
    loadReports();
  }, [currentPage, filterType]);

  const loadReports = async () => {
    try {
      setLoading(true);
      const response = await communityAPI.getReports({
        skip: (currentPage - 1) * reportsPerPage,
        limit: reportsPerPage,
        report_type: filterType || undefined
      });
      
      setReports(response.reports || []);
      setTotalReports(response.total_reports || 0);
    } catch (error) {
      console.error('Error loading reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const getReportTypeIcon = (type: string) => {
    switch (type) {
      case 'traffic': return '🚦';
      case 'delay': return '⏰';
      case 'fare_update': return '💰';
      case 'accessibility': return '♿';
      default: return '📍';
    }
  };

  const getReportTypeColor = (type: string) => {
    switch (type) {
      case 'traffic': return 'bg-red-100 text-red-800';
      case 'delay': return 'bg-orange-100 text-orange-800';
      case 'fare_update': return 'bg-green-100 text-green-800';
      case 'accessibility': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'heavy': return 'bg-red-100 text-red-800';
      case 'moderate': return 'bg-orange-100 text-orange-800';
      case 'light': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-orange-100 text-orange-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const totalPages = Math.ceil(totalReports / reportsPerPage);

  if (loading && reports.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Community Reports</h1>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="animate-pulse space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="border-b pb-4">
                <div className="flex items-start space-x-4">
                  <div className="h-10 w-10 bg-gray-200 rounded-lg"></div>
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Community Reports</h1>
          <p className="text-gray-600">Monitor and manage user-submitted reports</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <MessageSquare className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Reports</p>
              <p className="text-lg font-bold text-gray-900">{totalReports}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Traffic Reports</p>
              <p className="text-lg font-bold text-gray-900">
                {reports.filter(r => r.type === 'traffic').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Delay Reports</p>
              <p className="text-lg font-bold text-gray-900">
                {reports.filter(r => r.type === 'delay').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Active Reports</p>
              <p className="text-lg font-bold text-gray-900">
                {reports.filter(r => r.status === 'active').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <span className="text-sm font-medium text-gray-700">Filter by type:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilterType('')}
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                filterType === '' 
                  ? 'bg-blue-100 text-blue-800' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            {['traffic', 'delay', 'fare_update', 'accessibility'].map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  filterType === type 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {getReportTypeIcon(type)} {type.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="bg-white rounded-lg shadow">
        {reports.length === 0 ? (
          <div className="p-12 text-center">
            <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Reports Found</h3>
            <p className="text-gray-500">No community reports match your current filters.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {reports.map((report) => (
              <div key={report._id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    <div className="flex-shrink-0">
                      <div className="h-12 w-12 rounded-lg bg-gray-100 flex items-center justify-center text-2xl">
                        {getReportTypeIcon(report.type)}
                      </div>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getReportTypeColor(report.type)}`}>
                          {report.type.replace('_', ' ')}
                        </span>
                        {report.severity && (
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(report.severity)}`}>
                            {report.severity}
                          </span>
                        )}
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          report.status === 'active' 
                            ? 'bg-green-100 text-green-800' 
                            : report.status === 'verified'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {report.status}
                        </span>
                      </div>
                      
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {report.type === 'delay' && report.route 
                          ? `${report.route} - ${report.mode} Delay`
                          : `${report.type.charAt(0).toUpperCase() + report.type.slice(1)} Report`
                        }
                      </h3>
                      
                      <p className="text-gray-600 mb-3 line-clamp-2">
                        {report.description}
                      </p>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-1" />
                          {report.location}
                        </div>
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {new Date(report.reported_at).toLocaleDateString()}
                        </div>
                        {report.delay_minutes && (
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {report.delay_minutes} min delay
                          </div>
                        )}
                        <div className="flex items-center">
                          <span>👍 {report.votes} votes</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setSelectedReport(report)}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
                      title="View Details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Showing {((currentPage - 1) * reportsPerPage) + 1} to {Math.min(currentPage * reportsPerPage, totalReports)} of {totalReports} reports
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Previous
              </button>
              <span className="px-3 py-2 bg-blue-100 text-blue-800 rounded-md text-sm">
                {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Report Details Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-gray-900">Report Details</h3>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">Basic Information</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm text-gray-500">Report ID</label>
                      <p className="font-mono text-sm">{selectedReport.report_id}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Type</label>
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{getReportTypeIcon(selectedReport.type)}</span>
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getReportTypeColor(selectedReport.type)}`}>
                          {selectedReport.type.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Location</label>
                      <p className="font-medium">{selectedReport.location}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Status</label>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        selectedReport.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : selectedReport.status === 'verified'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {selectedReport.status}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">Report Metrics</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm text-gray-500">Reported At</label>
                      <p className="font-medium">{new Date(selectedReport.reported_at).toLocaleString()}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Community Votes</label>
                      <p className="font-medium">👍 {selectedReport.votes} helpful votes</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Reliability Score</label>
                      <p className="font-medium">{(selectedReport.reliability_score * 100).toFixed(1)}%</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Verified</label>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        selectedReport.verified 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {selectedReport.verified ? 'Verified' : 'Unverified'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <h4 className="font-semibold text-gray-900 mb-3">Description</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-800">{selectedReport.description}</p>
                </div>
              </div>
              
              {selectedReport.type === 'delay' && (
                <div className="mt-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Delay Details</h4>
                  <div className="bg-orange-50 rounded-lg p-4 grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm text-gray-600">Route</label>
                      <p className="font-medium">{selectedReport.route}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Mode</label>
                      <p className="font-medium capitalize">{selectedReport.mode}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-600">Delay Duration</label>
                      <p className="font-medium">{selectedReport.delay_minutes} minutes</p>
                    </div>
                    {selectedReport.estimated_clearance && (
                      <div>
                        <label className="text-sm text-gray-600">Est. Clearance</label>
                        <p className="font-medium">{new Date(selectedReport.estimated_clearance).toLocaleTimeString()}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}