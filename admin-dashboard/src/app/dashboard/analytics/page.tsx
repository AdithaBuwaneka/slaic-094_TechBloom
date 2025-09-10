'use client';

import { useState, useEffect } from 'react';
import { analyticsAPI } from '@/lib/api';
import { UserGrowthData, TravelModePreferences, ApiUsageData } from '@/lib/types';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer
} from 'recharts';
import { 
  TrendingUp, 
  Users, 
  Route,
  BarChart3,
  Calendar,
  Zap
} from 'lucide-react';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#F97316'];

export default function AnalyticsPage() {
  const [userGrowth, setUserGrowth] = useState<UserGrowthData | null>(null);
  const [travelModes, setTravelModes] = useState<TravelModePreferences | null>(null);
  const [apiUsage, setApiUsage] = useState<ApiUsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedPeriod]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      const [growthData, modesData, usageData] = await Promise.all([
        analyticsAPI.getUserGrowth(selectedPeriod),
        analyticsAPI.getTravelModes(),
        analyticsAPI.getApiUsage(7)
      ]);
      
      setUserGrowth(growthData);
      setTravelModes(modesData);
      setApiUsage(usageData);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Analytics & Insights</h1>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics & Insights</h1>
          <p className="text-gray-600">Data insights for Sri Lankan Transit System</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Calendar className="h-4 w-4 text-gray-400" />
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">New Users</p>
              <p className="text-lg font-bold text-gray-900">{userGrowth?.total_new_users || 0}</p>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Last {selectedPeriod} days
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Modes</p>
              <p className="text-lg font-bold text-gray-900">
                {travelModes?.travel_mode_preferences?.length || 0}
              </p>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Transport options
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Route className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">API Requests</p>
              <p className="text-lg font-bold text-gray-900">
                {apiUsage?.total_travel_requests || 0}
              </p>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Last 7 days
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Zap className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Growth Rate</p>
              <p className="text-lg font-bold text-gray-900">
                {userGrowth?.daily_growth ? 
                  Math.round((userGrowth.total_new_users / selectedPeriod) * 100) / 100 
                  : 0}/day
              </p>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Average daily signups
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Growth Chart */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              User Growth Trend
            </h2>
          </div>
          <div className="p-6">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={userGrowth?.daily_growth || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value: any) => [value, 'New Users']}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="new_users" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  dot={{ fill: '#3B82F6', strokeWidth: 2 }}
                  name="New Users"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Travel Mode Preferences */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Travel Mode Preferences
            </h2>
          </div>
          <div className="p-6">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={travelModes?.travel_mode_preferences || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ mode, percent }) => `${mode} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="user_count"
                >
                  {travelModes?.travel_mode_preferences?.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* API Usage by Mode */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 flex items-center">
              <Route className="h-5 w-5 mr-2" />
              API Usage by Transport Mode
            </h2>
          </div>
          <div className="p-6">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={apiUsage?.mode_usage || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mode" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value: any) => [value, 'Requests']} />
                <Legend />
                <Bar dataKey="requests" fill="#10B981" name="API Requests" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Travel Mode Details Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 flex items-center">
              <Users className="h-5 w-5 mr-2" />
              Mode Usage Details
            </h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Transport Mode
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Users
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Percentage
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {travelModes?.travel_mode_preferences?.map((mode, index) => {
                    const total = travelModes.travel_mode_preferences.reduce((sum, m) => sum + m.user_count, 0);
                    const percentage = ((mode.user_count / total) * 100).toFixed(1);
                    
                    return (
                      <tr key={mode.mode} className="hover:bg-gray-50">
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex items-center">
                            <div 
                              className="h-3 w-3 rounded-full mr-3"
                              style={{ backgroundColor: COLORS[index % COLORS.length] }}
                            ></div>
                            <span className="text-sm font-medium text-gray-900 capitalize">
                              {mode.mode}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {mode.user_count}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {percentage}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Sri Lankan Context Insights */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <span className="mr-2">🇱🇰</span>
          Sri Lankan Transit Insights
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Most Popular Mode</h3>
            <p className="text-2xl font-bold text-blue-600">
              {travelModes?.travel_mode_preferences?.[0]?.mode.toUpperCase() || 'BUS'}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {travelModes?.travel_mode_preferences?.[0]?.user_count || 0} users prefer this mode
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Growth Trend</h3>
            <p className="text-2xl font-bold text-green-600">
              {userGrowth?.total_new_users ? '+' + userGrowth.total_new_users : '0'}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              new users in last {selectedPeriod} days
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">API Activity</h3>
            <p className="text-2xl font-bold text-purple-600">
              {apiUsage?.total_travel_requests || 0}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              route requests this week
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}