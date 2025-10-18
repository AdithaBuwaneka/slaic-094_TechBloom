'use client';

import { useState, useEffect } from 'react';
import { settingsAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  Save, RefreshCw, AlertTriangle, Loader2, Server, Bell, Shield, Sliders
} from 'lucide-react';

// Interface remains the same
interface AdminSettings {
  system: { maintenance_mode: boolean; api_rate_limit: number; session_timeout: number; max_concurrent_users: number; };
  notifications: { email_notifications: boolean; push_notifications: boolean; system_alerts: boolean; user_registration_alerts: boolean; };
  security: { password_min_length: number; require_email_verification: boolean; enable_two_factor: boolean; max_login_attempts: number; };
  features: { user_registration: boolean; community_reports: boolean; agent_system: boolean; analytics_tracking: boolean; };
}

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState<AdminSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'default' | 'destructive'>('default');

  useEffect(() => { loadSettings(); }, []);

  const loadSettings = async () => {
    try { setLoading(true); const data = await settingsAPI.getSettings(); setSettings(data); } 
    catch (error) { console.error('Error loading settings:', error); } 
    finally { setLoading(false); }
  };

  const saveSettings = async () => {
    if (!settings) return;
    try {
      setSaving(true); setMessage('');
      await settingsAPI.updateSettings(settings);
      setMessageType('default'); setMessage('Settings saved successfully!');
    } catch {
      setMessageType('destructive'); setMessage('Error saving settings. Please try again.');
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const resetSettings = async () => {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
      try {
        setSaving(true); const data = await settingsAPI.resetSettings();
        setSettings(data.settings);
        setMessageType('default'); setMessage('Settings reset to defaults successfully!');
      } catch {
        setMessageType('destructive'); setMessage('Error resetting settings.');
      } finally {
        setSaving(false);
        setTimeout(() => setMessage(''), 3000);
      }
    }
  };

  const updateSetting = (section: keyof AdminSettings, key: string, value: string | number | boolean) => {
    setSettings(prev => prev ? { ...prev, [section]: { ...prev[section], [key]: value } } : null);
  };

  if (loading || !settings) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Settings</h1>
          <p className="text-muted-foreground">Configure system settings and preferences.</p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={resetSettings} disabled={saving}><RefreshCw className="h-4 w-4 mr-2" /> Reset</Button>
          <Button onClick={saveSettings} disabled={saving}>
            {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />} Save Changes
          </Button>
        </div>
      </div>
      
      {message && <Alert variant={messageType}><AlertTriangle className="h-4 w-4" /><AlertTitle>{messageType === 'default' ? 'Success' : 'Error'}</AlertTitle><AlertDescription>{message}</AlertDescription></Alert>}

      <Tabs defaultValue="system" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="system"><Server className="h-4 w-4 mr-2"/>System</TabsTrigger>
          <TabsTrigger value="notifications"><Bell className="h-4 w-4 mr-2"/>Notifications</TabsTrigger>
          <TabsTrigger value="security"><Shield className="h-4 w-4 mr-2"/>Security</TabsTrigger>
          <TabsTrigger value="features"><Sliders className="h-4 w-4 mr-2"/>Features</TabsTrigger>
        </TabsList>

        <Card className="mt-4">
          <CardContent className="pt-6">
            <TabsContent value="system" className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2"><Label>API Rate Limit (reqs/min)</Label><Input type="number" value={settings.system.api_rate_limit} onChange={(e) => updateSetting('system', 'api_rate_limit', parseInt(e.target.value))} /></div>
                <div className="space-y-2"><Label>Session Timeout (seconds)</Label><Input type="number" value={settings.system.session_timeout} onChange={(e) => updateSetting('system', 'session_timeout', parseInt(e.target.value))} /></div>
                <div className="flex items-center space-x-2"><Switch id="maintenance" checked={settings.system.maintenance_mode} onCheckedChange={(c) => updateSetting('system', 'maintenance_mode', c)} /><Label htmlFor="maintenance">Enable Maintenance Mode</Label></div>
              </div>
            </TabsContent>
            
            <TabsContent value="notifications" className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border p-4"><Label>Email Notifications</Label><Switch checked={settings.notifications.email_notifications} onCheckedChange={(c) => updateSetting('notifications', 'email_notifications', c)} /></div>
              <div className="flex items-center justify-between rounded-lg border p-4"><Label>Push Notifications</Label><Switch checked={settings.notifications.push_notifications} onCheckedChange={(c) => updateSetting('notifications', 'push_notifications', c)} /></div>
              <div className="flex items-center justify-between rounded-lg border p-4"><Label>System Alerts</Label><Switch checked={settings.notifications.system_alerts} onCheckedChange={(c) => updateSetting('notifications', 'system_alerts', c)} /></div>
              <div className="flex items-center justify-between rounded-lg border p-4"><Label>User Registration Alerts</Label><Switch checked={settings.notifications.user_registration_alerts} onCheckedChange={(c) => updateSetting('notifications', 'user_registration_alerts', c)} /></div>
            </TabsContent>
            
            <TabsContent value="security" className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2"><Label>Min. Password Length</Label><Input type="number" value={settings.security.password_min_length} onChange={(e) => updateSetting('security', 'password_min_length', parseInt(e.target.value))} /></div>
                <div className="space-y-2"><Label>Max Login Attempts</Label><Input type="number" value={settings.security.max_login_attempts} onChange={(e) => updateSetting('security', 'max_login_attempts', parseInt(e.target.value))} /></div>
              </div>
              <div className="flex items-center space-x-2"><Checkbox id="email-verify" checked={settings.security.require_email_verification} onCheckedChange={(c) => updateSetting('security', 'require_email_verification', !!c)} /><Label htmlFor="email-verify">Require Email Verification</Label></div>
              <div className="flex items-center space-x-2"><Checkbox id="2fa" checked={settings.security.enable_two_factor} onCheckedChange={(c) => updateSetting('security', 'enable_two_factor', !!c)} disabled /><Label htmlFor="2fa" className="text-muted-foreground">Enable Two-Factor Authentication (Coming Soon)</Label></div>
            </TabsContent>
            
            <TabsContent value="features" className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border p-4"><Label>User Registration</Label><Switch checked={settings.features.user_registration} onCheckedChange={(c) => updateSetting('features', 'user_registration', c)} /></div>
              <div className="flex items-center justify-between rounded-lg border p-4"><Label>Community Reports</Label><Switch checked={settings.features.community_reports} onCheckedChange={(c) => updateSetting('features', 'community_reports', c)} /></div>
              <div className="flex items-center justify-between rounded-lg border p-4"><Label>Multi-Agent System</Label><Switch checked={settings.features.agent_system} onCheckedChange={(c) => updateSetting('features', 'agent_system', c)} /></div>
              <div className="flex items-center justify-between rounded-lg border p-4"><Label>Analytics Tracking</Label><Switch checked={settings.features.analytics_tracking} onCheckedChange={(c) => updateSetting('features', 'analytics_tracking', c)} /></div>
            </TabsContent>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  );
}