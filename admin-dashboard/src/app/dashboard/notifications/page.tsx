'use client';

import { useState } from 'react';
import { notificationAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { 
  Bell, 
  Send, 
  MessageSquare,
  CheckCircle,
  AlertTriangle,
  Loader2,
  Lightbulb
} from 'lucide-react';

export default function NotificationsPage() {
  const [notification, setNotification] = useState({
    title: '',
    body: '',
    data: {},
    userIds: [] as string[]
  });
  const [sending, setSending] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [notificationType, setNotificationType] = useState<'all' | 'specific'>('all');

  const handleSendNotification = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!notification.title || !notification.body) {
      setError('Please fill in both title and message fields.');
      return;
    }
    setSending(true);
    setError('');
    setSuccess('');
    try {
      await notificationAPI.sendBroadcast(
        notification.title,
        notification.body,
        notification.data,
        notificationType === 'specific' ? notification.userIds : undefined
      );
      setSuccess('Notification sent successfully!');
      setNotification({ title: '', body: '', data: {}, userIds: [] });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send notification');
    } finally {
      setSending(false);
    }
  };

  const predefinedMessages = [
    { title: 'System Maintenance', body: 'The system will undergo maintenance soon. Some features may be temporarily unavailable.', data: { type: 'maintenance' } },
    { title: 'Weather Alert', body: 'Heavy rainfall is expected. Plan your commute accordingly and stay safe!', data: { type: 'weather' } },
    { title: 'New Feature Available', body: 'Check out our new fare optimization feature to save more on your commute.', data: { type: 'feature' } }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Push Notifications</h1>
        <p className="text-muted-foreground">Send notifications to all or specific app users.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">Active Users</CardTitle><Bell className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">9</div><p className="text-xs text-muted-foreground">Users who can receive notifications</p></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">Delivery Rate</CardTitle><Send className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">98.5%</div><p className="text-xs text-muted-foreground">Successful notification delivery</p></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">Engagement</CardTitle><MessageSquare className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">12.3%</div><p className="text-xs text-muted-foreground">Average open rate</p></CardContent></Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Compose Notification</CardTitle>
            <CardDescription>Craft and send a message to your users.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSendNotification} className="space-y-6">
              {success && <Alert><CheckCircle className="h-4 w-4" /><AlertTitle>Success!</AlertTitle><AlertDescription>{success}</AlertDescription></Alert>}
              {error && <Alert variant="destructive"><AlertTriangle className="h-4 w-4" /><AlertTitle>Error</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>}
              
              <div className="space-y-2">
                <Label>Send to</Label>
                <RadioGroup defaultValue="all" value={notificationType} onValueChange={(value: 'all' | 'specific') => setNotificationType(value)} className="flex items-center gap-4">
                  <div className="flex items-center space-x-2"><RadioGroupItem value="all" id="r1" /><Label htmlFor="r1">All Users</Label></div>
                  <div className="flex items-center space-x-2"><RadioGroupItem value="specific" id="r2" disabled /><Label htmlFor="r2" className="text-muted-foreground">Specific Users (Coming Soon)</Label></div>
                </RadioGroup>
              </div>
              <div className="space-y-2"><Label htmlFor="title">Title *</Label><Input id="title" required value={notification.title} onChange={(e) => setNotification(p => ({ ...p, title: e.target.value }))} placeholder="Enter notification title" /></div>
              <div className="space-y-2"><Label htmlFor="body">Message *</Label><Textarea id="body" required rows={4} value={notification.body} onChange={(e) => setNotification(p => ({ ...p, body: e.target.value }))} placeholder="Enter notification message" /><p className="text-xs text-muted-foreground">Keep it concise and actionable.</p></div>
              <Button type="submit" disabled={sending} className="w-full">
                {sending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sending...</> : <><Send className="mr-2 h-4 w-4" /> Send Notification</>}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Templates</CardTitle>
            <CardDescription>Use a predefined template to send messages faster.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {predefinedMessages.map((template, index) => (
              <div key={index} className="border rounded-lg p-4 hover:bg-muted cursor-pointer" onClick={() => setNotification({ title: template.title, body: template.body, data: template.data, userIds: [] })}>
                <h3 className="font-medium mb-1">{template.title}</h3>
                <p className="text-sm text-muted-foreground line-clamp-2">{template.body}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
      
      <Alert>
        <Lightbulb className="h-4 w-4" />
        <AlertTitle>Notification Best Practices</AlertTitle>
        <AlertDescription>
          Keep titles under 50 characters and messages clear. Avoid sending too many notifications or sending during late hours.
        </AlertDescription>
      </Alert>
    </div>
  );
}