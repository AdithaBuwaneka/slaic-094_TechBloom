import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, TextInput, Alert, Modal } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { communityService } from '../../../src/services/api/communityService';
import { useAuth } from '../../../src/contexts/AppContext';

interface CommunityReport {
  id: string;
  type: 'traffic' | 'delay' | 'fare' | 'accessibility' | 'safety';
  title: string;
  description: string;
  location: string;
  timestamp: Date;
  votes: number;
  userVoted: boolean;
  severity: 'low' | 'medium' | 'high';
  status: 'active' | 'resolved' | 'verified';
}

export default function Community() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'reports' | 'create'>('reports');
  const [newReport, setNewReport] = useState({
    type: 'traffic' as const,
    title: '',
    description: '',
    location: '',
    severity: 'medium' as const
  });

  const reportTypes = [
    { id: 'traffic', label: 'Traffic Conditions', icon: '🚦', color: 'bg-red-100 text-red-700' },
    { id: 'delay', label: 'Transit Delays', icon: '⏰', color: 'bg-orange-100 text-orange-700' },
    { id: 'fare', label: 'Fare Updates', icon: '💰', color: 'bg-green-100 text-green-700' },
    { id: 'accessibility', label: 'Accessibility', icon: '♿', color: 'bg-blue-100 text-blue-700' },
    { id: 'safety', label: 'Safety Issues', icon: '🛡️', color: 'bg-purple-100 text-purple-700' }
  ];


  const [reports, setReports] = useState<CommunityReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<CommunityReport | null>(null);
  const [showReportModal, setShowReportModal] = useState(false);

  // Load reports from backend on component mount
  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setIsLoading(true);
      const response = await communityService.getAllReports({ limit: 20 });
      if (response.success && response.data) {
        // Convert backend format to local format if needed
        const backendReports = response.data.data?.reports || response.data.reports || [];
        
        // Map backend reports to local format
        const mappedReports = backendReports.map(report => ({
          id: report.report_id || report._id,
          type: report.type,
          title: report.title || `${report.type.charAt(0).toUpperCase() + report.type.slice(1)} Report - ${report.location}`,
          description: report.description,
          location: report.location,
          timestamp: new Date(report.reported_at || report.timestamp || new Date()),
          votes: report.votes || 0,
          userVoted: report.user_voted || false,
          severity: report.severity || 'medium',
          status: report.status || 'active'
        }));
        
        setReports(mappedReports);
      } else {
        setReports([]);
      }
    } catch (error) {
      console.error('Error loading reports:', error);
      setReports([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVote = (reportId: string) => {
    setReports(prev => prev.map(report => 
      report.id === reportId 
        ? { 
            ...report, 
            votes: report.userVoted ? report.votes - 1 : report.votes + 1,
            userVoted: !report.userVoted 
          }
        : report
    ));
  };

  const handleSubmitReport = async () => {
    if (!newReport.title || !newReport.description || !newReport.location) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (!user) {
      Alert.alert('Error', 'You must be logged in to submit reports');
      return;
    }

    setIsLoading(true);
    try {
      // Submit report to backend
      const reportData = {
        type: newReport.type,
        title: newReport.title,
        description: newReport.description,
        location: newReport.location,
        severity: newReport.severity,
        user_id: user.user_id
      };

      const response = await communityService.submitReport(reportData);
      
      if (response.success) {
        // Create local report from backend response
        const report: CommunityReport = {
          id: response.data?.report_id || Date.now().toString(),
          type: newReport.type,
          title: newReport.title,
          description: newReport.description,
          location: newReport.location,
          timestamp: new Date(),
          votes: 1,
          userVoted: true,
          severity: newReport.severity,
          status: 'active'
        };

        setReports(prev => [report, ...prev]);
        setNewReport({
          type: 'traffic',
          title: '',
          description: '',
          location: '',
          severity: 'medium'
        });
        setActiveTab('reports');
        Alert.alert('Success', 'Your report has been submitted successfully!');
      } else {
        Alert.alert('Error', response.error?.message || 'Failed to submit report');
      }
    } catch (error) {
      console.error('Error submitting report:', error);
      Alert.alert('Error', 'Failed to submit report. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-700';
      case 'medium': return 'bg-orange-100 text-orange-700';
      case 'low': return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getTimeAgo = (timestamp: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - timestamp.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffMins < 1440) {
      return `${Math.floor(diffMins / 60)}h ago`;
    } else {
      return `${Math.floor(diffMins / 1440)}d ago`;
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      {/* Header */}
      <View className="bg-white px-4 py-4 border-b border-gray-200">
        <Text className="text-2xl font-bold text-gray-800">Community Reports</Text>
        <Text className="text-sm text-gray-600">Share and discover real-time transport updates</Text>
      </View>

      {/* Tab Navigation */}
      <View className="bg-white border-b border-gray-200">
        <View className="flex-row">
          <TouchableOpacity
            className={`flex-1 py-3 px-4 ${activeTab === 'reports' ? 'border-b-2 border-blue-600' : ''}`}
            onPress={() => setActiveTab('reports')}
          >
            <Text className={`text-center font-medium ${
              activeTab === 'reports' ? 'text-blue-600' : 'text-gray-600'
            }`}>
              Latest Reports
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            className={`flex-1 py-3 px-4 ${activeTab === 'create' ? 'border-b-2 border-blue-600' : ''}`}
            onPress={() => setActiveTab('create')}
          >
            <Text className={`text-center font-medium ${
              activeTab === 'create' ? 'text-blue-600' : 'text-gray-600'
            }`}>
              Report Issue
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView className="flex-1">
        {activeTab === 'reports' ? (
          // Reports List
          <View className="p-4">
            {/* Stats */}
            <View className="bg-white p-4 rounded-lg shadow-sm mb-4">
              <Text className="text-lg font-semibold text-gray-800 mb-3">Community Impact</Text>
              <View className="flex-row justify-between">
                <View className="items-center">
                  <Text className="text-2xl font-bold text-blue-600">{reports.length}</Text>
                  <Text className="text-sm text-gray-600">Active Reports</Text>
                </View>
                <View className="items-center">
                  <Text className="text-2xl font-bold text-green-600">
                    {reports.reduce((sum, r) => sum + r.votes, 0)}
                  </Text>
                  <Text className="text-sm text-gray-600">Total Votes</Text>
                </View>
                <View className="items-center">
                  <Text className="text-2xl font-bold text-purple-600">4.2k</Text>
                  <Text className="text-sm text-gray-600">Users Helped</Text>
                </View>
              </View>
            </View>

            {/* Report Type Filter */}
            <View className="mb-4">
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View className="flex-row space-x-3">
                  <TouchableOpacity className="bg-white px-4 py-2 rounded-full border border-blue-600">
                    <Text className="text-blue-600 font-medium">All</Text>
                  </TouchableOpacity>
                  {reportTypes.map((type) => (
                    <TouchableOpacity key={type.id} className="bg-white px-4 py-2 rounded-full border border-gray-300">
                      <Text className="text-gray-700">{type.icon} {type.label}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </ScrollView>
            </View>

            {/* Reports */}
            <View className="space-y-4">
              {isLoading ? (
                <View className="bg-white rounded-lg shadow-sm p-6 items-center">
                  <Text className="text-4xl mb-2">🔄</Text>
                  <Text className="text-lg font-medium text-gray-800">Loading community reports...</Text>
                </View>
              ) : reports.length === 0 ? (
                <View className="bg-white rounded-lg shadow-sm p-6 items-center">
                  <Text className="text-4xl mb-2">📢</Text>
                  <Text className="text-lg font-medium text-gray-800 mb-2">No reports yet</Text>
                  <Text className="text-sm text-gray-600 text-center mb-4">
                    Be the first to report traffic, delays, or accessibility issues in your area
                  </Text>
                  <TouchableOpacity
                    className="bg-blue-600 px-4 py-2 rounded-lg"
                    onPress={() => setActiveTab('create')}
                  >
                    <Text className="text-white font-medium">Create Report</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                reports.map((report) => (
                <View key={report.id} className="bg-white rounded-lg shadow-sm p-4">
                  <View className="flex-row items-start justify-between mb-2">
                    <View className="flex-1">
                      <View className="flex-row items-center mb-1">
                        <Text className="text-lg mr-2">
                          {reportTypes.find(t => t.id === report.type)?.icon}
                        </Text>
                        <Text className="text-base font-semibold text-gray-800 flex-1">
                          {report.title}
                        </Text>
                      </View>
                      <View className="flex-row items-center space-x-2 mb-2">
                        <View className={`px-2 py-1 rounded-full ${getSeverityColor(report.severity)}`}>
                          <Text className="text-xs font-medium capitalize">{report.severity}</Text>
                        </View>
                        <Text className="text-xs text-gray-500">{getTimeAgo(report.timestamp)}</Text>
                      </View>
                    </View>
                  </View>

                  <Text className="text-sm text-gray-700 mb-2">{report.description}</Text>
                  
                  <View className="flex-row items-center text-xs text-gray-500 mb-3">
                    <Ionicons name="location" size={12} color="#6b7280" />
                    <Text className="ml-1">{report.location}</Text>
                  </View>

                  <View className="flex-row items-center justify-between">
                    <TouchableOpacity
                      className="flex-row items-center"
                      onPress={() => handleVote(report.id)}
                    >
                      <Ionicons 
                        name={report.userVoted ? "thumbs-up" : "thumbs-up-outline"} 
                        size={16} 
                        color={report.userVoted ? "#2563eb" : "#6b7280"} 
                      />
                      <Text className={`ml-1 text-sm ${
                        report.userVoted ? 'text-blue-600' : 'text-gray-600'
                      }`}>
                        {report.votes} helpful
                      </Text>
                    </TouchableOpacity>
                    
                    <View className="flex-row items-center space-x-3">
                      <TouchableOpacity
                        className="bg-blue-100 px-3 py-1 rounded-full"
                        onPress={() => {
                          setSelectedReport(report);
                          setShowReportModal(true);
                        }}
                      >
                        <Text className="text-blue-700 text-xs font-medium">View Details</Text>
                      </TouchableOpacity>
                      <TouchableOpacity>
                        <Ionicons name="share-outline" size={16} color="#6b7280" />
                      </TouchableOpacity>
                      <TouchableOpacity>
                        <Ionicons name="flag-outline" size={16} color="#6b7280" />
                      </TouchableOpacity>
                    </View>
                  </View>
                </View>
              ))
              )}
            </View>
          </View>
        ) : (
          // Create Report Form
          <View className="p-4">
            <View className="bg-white rounded-lg shadow-sm p-4">
              <Text className="text-lg font-semibold text-gray-800 mb-4">Report a Transport Issue</Text>

              {/* Report Type */}
              <View className="mb-4">
                <Text className="text-sm font-medium text-gray-700 mb-2">Issue Type</Text>
                <View className="flex-row flex-wrap gap-2">
                  {reportTypes.map((type) => (
                    <TouchableOpacity
                      key={type.id}
                      className={`flex-row items-center px-3 py-2 rounded-lg border ${
                        newReport.type === type.id
                          ? 'bg-blue-50 border-blue-300'
                          : 'bg-gray-50 border-gray-300'
                      }`}
                      onPress={() => setNewReport(prev => ({ ...prev, type: type.id as any }))}
                    >
                      <Text className="mr-2">{type.icon}</Text>
                      <Text className={`text-sm ${
                        newReport.type === type.id ? 'text-blue-700' : 'text-gray-700'
                      }`}>
                        {type.label}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              {/* Title */}
              <View className="mb-4">
                <Text className="text-sm font-medium text-gray-700 mb-2">Title</Text>
                <TextInput
                  className="border border-gray-300 rounded-lg px-3 py-2 text-base"
                  placeholder="Brief description of the issue"
                  value={newReport.title}
                  onChangeText={(value) => setNewReport(prev => ({ ...prev, title: value }))}
                />
              </View>

              {/* Location */}
              <View className="mb-4">
                <Text className="text-sm font-medium text-gray-700 mb-2">Location</Text>
                <TextInput
                  className="border border-gray-300 rounded-lg px-3 py-2 text-base"
                  placeholder="Where is this happening?"
                  value={newReport.location}
                  onChangeText={(value) => setNewReport(prev => ({ ...prev, location: value }))}
                />
              </View>

              {/* Description */}
              <View className="mb-4">
                <Text className="text-sm font-medium text-gray-700 mb-2">Description</Text>
                <TextInput
                  className="border border-gray-300 rounded-lg px-3 py-2 text-base"
                  placeholder="Provide more details about the issue"
                  value={newReport.description}
                  onChangeText={(value) => setNewReport(prev => ({ ...prev, description: value }))}
                  multiline
                  numberOfLines={4}
                  textAlignVertical="top"
                />
              </View>

              {/* Severity */}
              <View className="mb-6">
                <Text className="text-sm font-medium text-gray-700 mb-2">Severity</Text>
                <View className="flex-row space-x-3">
                  {['low', 'medium', 'high'].map((severity) => (
                    <TouchableOpacity
                      key={severity}
                      className={`flex-1 py-2 px-3 rounded-lg border ${
                        newReport.severity === severity
                          ? getSeverityColor(severity).replace('text-', 'border-').split(' ')[0]
                          : 'border-gray-300'
                      }`}
                      onPress={() => setNewReport(prev => ({ ...prev, severity: severity as any }))}
                    >
                      <Text className={`text-center text-sm capitalize ${
                        newReport.severity === severity 
                          ? getSeverityColor(severity).split(' ')[1]
                          : 'text-gray-700'
                      }`}>
                        {severity}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              {/* Submit Button */}
              <TouchableOpacity
                className={`bg-blue-600 rounded-lg py-3 ${isLoading ? 'opacity-70' : ''}`}
                onPress={handleSubmitReport}
                disabled={isLoading}
              >
                <Text className="text-white text-center text-lg font-semibold">
                  {isLoading ? 'Submitting...' : 'Submit Report'}
                </Text>
              </TouchableOpacity>

              <Text className="text-xs text-gray-500 text-center mt-3">
                Your report will help other commuters and improve the transit system
              </Text>
            </View>
          </View>
        )}
      </ScrollView>

      {/* Community Report Details Modal */}
      <Modal
        visible={showReportModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView className="flex-1 bg-gray-50">
          <View className="flex-row items-center justify-between p-4 bg-white border-b border-gray-200">
            <Text className="text-xl font-bold text-gray-800">Report Details</Text>
            <TouchableOpacity onPress={() => setShowReportModal(false)}>
              <Ionicons name="close" size={24} color="#6b7280" />
            </TouchableOpacity>
          </View>
          
          <ScrollView className="flex-1">
            {selectedReport && (
              <View className="p-4">
                {/* Report Header */}
                <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                  <View className="flex-row items-start mb-3">
                    <Text className="text-3xl mr-3">
                      {reportTypes.find(t => t.id === selectedReport.type)?.icon}
                    </Text>
                    <View className="flex-1">
                      <Text className="text-xl font-bold text-gray-800 mb-1">
                        {selectedReport.title}
                      </Text>
                      <View className="flex-row items-center space-x-2">
                        <View className={`px-3 py-1 rounded-full ${getSeverityColor(selectedReport.severity)}`}>
                          <Text className="text-sm font-semibold capitalize">{selectedReport.severity}</Text>
                        </View>
                        <View className="bg-gray-100 px-3 py-1 rounded-full">
                          <Text className="text-sm font-medium text-gray-700 capitalize">{selectedReport.status}</Text>
                        </View>
                      </View>
                    </View>
                  </View>
                </View>

                {/* Report Details */}
                <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                  <Text className="text-lg font-semibold text-gray-800 mb-3">📝 Report Details</Text>
                  
                  <View className="space-y-4">
                    <View>
                      <Text className="text-base font-medium text-gray-700 mb-1">Description</Text>
                      <Text className="text-base text-gray-800 leading-6">{selectedReport.description}</Text>
                    </View>
                    
                    <View>
                      <Text className="text-base font-medium text-gray-700 mb-1">Location</Text>
                      <View className="flex-row items-center">
                        <Ionicons name="location" size={16} color="#6b7280" />
                        <Text className="text-base text-gray-800 ml-2">{selectedReport.location}</Text>
                      </View>
                    </View>
                    
                    <View>
                      <Text className="text-base font-medium text-gray-700 mb-1">Category</Text>
                      <View className="flex-row items-center">
                        <Text className="text-lg mr-2">
                          {reportTypes.find(t => t.id === selectedReport.type)?.icon}
                        </Text>
                        <Text className="text-base text-gray-800">
                          {reportTypes.find(t => t.id === selectedReport.type)?.label}
                        </Text>
                      </View>
                    </View>
                    
                    <View>
                      <Text className="text-base font-medium text-gray-700 mb-1">Reported</Text>
                      <View className="flex-row items-center">
                        <Ionicons name="time" size={16} color="#6b7280" />
                        <Text className="text-base text-gray-800 ml-2">
                          {getTimeAgo(selectedReport.timestamp)} • {selectedReport.timestamp.toLocaleDateString()}
                        </Text>
                      </View>
                    </View>
                  </View>
                </View>

                {/* Community Impact */}
                <View className="bg-white rounded-lg p-4 mb-4 shadow-sm">
                  <Text className="text-lg font-semibold text-gray-800 mb-3">👥 Community Impact</Text>
                  
                  <View className="flex-row justify-between items-center">
                    <View className="flex-row items-center">
                      <Ionicons 
                        name={selectedReport.userVoted ? "thumbs-up" : "thumbs-up-outline"} 
                        size={20} 
                        color={selectedReport.userVoted ? "#2563eb" : "#6b7280"} 
                      />
                      <Text className={`ml-2 text-base font-medium ${
                        selectedReport.userVoted ? 'text-blue-600' : 'text-gray-700'
                      }`}>
                        {selectedReport.votes} people found this helpful
                      </Text>
                    </View>
                    
                    <TouchableOpacity
                      className={`px-4 py-2 rounded-lg ${
                        selectedReport.userVoted ? 'bg-blue-600' : 'bg-gray-200'
                      }`}
                      onPress={() => {
                        handleVote(selectedReport.id);
                        setSelectedReport(prev => prev ? {
                          ...prev,
                          votes: prev.userVoted ? prev.votes - 1 : prev.votes + 1,
                          userVoted: !prev.userVoted
                        } : null);
                      }}
                    >
                      <Text className={`font-medium ${
                        selectedReport.userVoted ? 'text-white' : 'text-gray-700'
                      }`}>
                        {selectedReport.userVoted ? 'Helpful ✓' : 'Mark Helpful'}
                      </Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Safety Tips or Related Info */}
                {selectedReport.type === 'safety' && (
                  <View className="bg-red-50 rounded-lg p-4 mb-4">
                    <Text className="text-lg font-semibold text-red-800 mb-2">🛡️ Safety Tips</Text>
                    <View className="space-y-1">
                      <Text className="text-sm text-red-700">• Report serious safety issues to authorities immediately</Text>
                      <Text className="text-sm text-red-700">• Avoid the area if possible until resolved</Text>
                      <Text className="text-sm text-red-700">• Consider alternative routes</Text>
                    </View>
                  </View>
                )}

                {selectedReport.type === 'traffic' && (
                  <View className="bg-orange-50 rounded-lg p-4 mb-4">
                    <Text className="text-lg font-semibold text-orange-800 mb-2">🚦 Traffic Info</Text>
                    <Text className="text-sm text-orange-700">
                      Consider using alternative routes or public transport to avoid delays. 
                      Check real-time traffic updates before traveling.
                    </Text>
                  </View>
                )}

                {selectedReport.type === 'accessibility' && (
                  <View className="bg-blue-50 rounded-lg p-4 mb-4">
                    <Text className="text-lg font-semibold text-blue-800 mb-2">♿ Accessibility</Text>
                    <Text className="text-sm text-blue-700">
                      This report helps improve accessibility for everyone. Contact transport authorities 
                      if you need immediate assistance with accessibility features.
                    </Text>
                  </View>
                )}

                {/* Actions */}
                <View className="flex-row space-x-3 mt-4">
                  <TouchableOpacity className="flex-1 bg-blue-600 py-3 rounded-lg">
                    <View className="flex-row items-center justify-center">
                      <Ionicons name="share-outline" size={18} color="white" />
                      <Text className="text-white font-semibold text-base ml-2">Share Report</Text>
                    </View>
                  </TouchableOpacity>
                  <TouchableOpacity className="flex-1 bg-gray-200 py-3 rounded-lg">
                    <View className="flex-row items-center justify-center">
                      <Ionicons name="flag-outline" size={18} color="#6b7280" />
                      <Text className="text-gray-700 font-semibold text-base ml-2">Report Issue</Text>
                    </View>
                  </TouchableOpacity>
                </View>

                {/* Close Button */}
                <TouchableOpacity
                  className="bg-gray-100 py-3 rounded-lg mt-3"
                  onPress={() => setShowReportModal(false)}
                >
                  <Text className="text-gray-700 text-center font-semibold text-base">Close</Text>
                </TouchableOpacity>
              </View>
            )}
          </ScrollView>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}