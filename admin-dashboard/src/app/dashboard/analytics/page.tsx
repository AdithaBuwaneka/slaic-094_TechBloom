'use client';

import { useState, useEffect } from 'react';
import { analyticsAPI } from '@/lib/api';
import { UserGrowthData, TravelModePreferences, ApiUsageData } from '@/lib/types';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from '@/components/ui/table';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  TrendingUp, Users, Route, Zap, Calendar
} from 'lucide-react';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#F97316'];

export default function AnalyticsPage() {
  const [userGrowth, setUserGrowth] = useState<UserGrowthData | null>(null);
  const [travelModes, setTravelModes] = useState<TravelModePreferences | null>(null);
  const [apiUsage, setApiUsage] = useState<ApiUsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('30');

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedPeriod]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      const period = Number(selectedPeriod);
      const [growthData, modesData, usageData] = await Promise.all([
        analyticsAPI.getUserGrowth(period),
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
          <Skeleton className="h-8 w-1/3" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80" />
          <Skeleton className="h-80" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics & Insights</h1>
          <p className="text-muted-foreground">Data insights for Sri Lankan Transit System</p>
        </div>
        <div className="flex items-center space-x-2">
          <Calendar className="h-4 w-4 text-muted-foreground" />
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">New Users</CardTitle><TrendingUp className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{userGrowth?.total_new_users || 0}</div><p className="text-xs text-muted-foreground">Last {selectedPeriod} days</p></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">Total Modes</CardTitle><Users className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{travelModes?.travel_mode_preferences?.length || 0}</div><p className="text-xs text-muted-foreground">Transport options</p></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">API Requests</CardTitle><Route className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{apiUsage?.total_travel_requests || 0}</div><p className="text-xs text-muted-foreground">Last 7 days</p></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">Growth Rate</CardTitle><Zap className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{userGrowth?.total_new_users ? Math.round((userGrowth.total_new_users / Number(selectedPeriod)) * 100) / 100 : 0}/day</div><p className="text-xs text-muted-foreground">Avg. daily signups</p></CardContent></Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>User Growth Trend</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={userGrowth?.daily_growth || []}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" tick={{ fontSize: 12 }} tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} /><YAxis tick={{ fontSize: 12 }} /><Tooltip labelFormatter={(value) => new Date(value).toLocaleDateString()} formatter={(value: any) => [value, 'New Users']} /><Legend /><Line type="monotone" dataKey="new_users" stroke="#3B82F6" strokeWidth={2} name="New Users" /></LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Travel Mode Preferences</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart><Pie data={travelModes?.travel_mode_preferences || []} cx="50%" cy="50%" labelLine={false} label={({ mode, percent }) => `${mode} (${(percent * 100).toFixed(0)}%)`} outerRadius={80} fill="#8884d8" dataKey="user_count">{travelModes?.travel_mode_preferences?.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}</Pie><Tooltip /></PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>API Usage by Transport Mode</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={apiUsage?.mode_usage || []}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="mode" tick={{ fontSize: 12 }} /><YAxis tick={{ fontSize: 12 }} /><Tooltip formatter={(value: any) => [value, 'Requests']} /><Legend /><Bar dataKey="requests" fill="#10B981" name="API Requests" /></BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Mode Usage Details</CardTitle></CardHeader>
          <CardContent>
            <Table>
              <TableHeader><TableRow><TableHead>Transport Mode</TableHead><TableHead>Users</TableHead><TableHead>Percentage</TableHead></TableRow></TableHeader>
              <TableBody>
                {travelModes?.travel_mode_preferences?.map((mode) => {
                  const total = travelModes.travel_mode_preferences.reduce((sum, m) => sum + m.user_count, 0);
                  return (<TableRow key={mode.mode}><TableCell className="font-medium capitalize">{mode.mode}</TableCell><TableCell>{mode.user_count}</TableCell><TableCell>{((mode.user_count / total) * 100).toFixed(1)}%</TableCell></TableRow>);
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}