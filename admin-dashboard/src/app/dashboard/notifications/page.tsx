'use client';

import { useState } from 'react';
import { notificationAPI } from '@/lib/api';
import { 
  Bell, 
  Send, 
  MessageSquare,
  CheckCircle,
  AlertTriangle
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
      setError('Please fill in both title and message fields');
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
      setNotification({
        title: '',
        body: '',
        data: {},
        userIds: []
      });
    } catch (error: unknown) {
      interface ErrorResponse {
        response?: {
          data?: {
            detail?: string;
          };
        };
        message?: string;
      }
      const errorObj = error as ErrorResponse;
      const errorMessage = error instanceof Error ? error.message : 'Failed to send notification';
      const response = errorObj.response?.data?.detail || errorMessage;
      setError(response);
    } finally {
      setSending(false);
    }
  };

  const predefinedMessages = [
    {
      title: 'System Maintenance',
      body: 'The Sri Lankan Transit system will undergo maintenance on Sunday, 2 AM - 4 AM. Some features may be temporarily unavailable.',
      data: { type: 'maintenance' }
    },
    {
      title: 'Weather Alert',
      body: 'Heavy rainfall expected in Colombo region. Plan your commute accordingly and stay safe!',
      data: { type: 'weather', region: 'colombo' }
    },
    {
      title: 'New Feature Available',
      body: 'Check out our new fare optimization feature! Save more on your daily commute.',
      data: { type: 'feature', feature: 'fare_optimization' }
    },
    {
      title: 'Traffic Update',
      body: 'Major traffic congestion reported on Galle Road. Consider alternative routes.',
      data: { type: 'traffic', location: 'galle_road' }
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Push Notifications</h1>
          <p className="text-gray-600">Send notifications to app users</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Bell className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Active Users</p>
              <p className="text-lg font-bold text-gray-900">9</p>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Users who can receive notifications
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Send className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Delivery Rate</p>
              <p className="text-lg font-bold text-gray-900">98.5%</p>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Successful notification delivery
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <MessageSquare className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Engagement</p>
              <p className="text-lg font-bold text-gray-900">12.3%</p>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Average open rate
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Send Notification Form */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 flex items-center">
              <Send className="h-5 w-5 mr-2" />
              Send Notification
            </h2>
          </div>
          
          <form onSubmit={handleSendNotification} className="p-6 space-y-4">
            {success && (
              <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-md text-sm flex items-center">
                <CheckCircle className="h-4 w-4 mr-2" />
                {success}
              </div>
            )}
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm flex items-center">
                <AlertTriangle className="h-4 w-4 mr-2" />
                {error}
              </div>
            )}

            {/* Notification Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Send to
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="type"
                    value="all"
                    checked={notificationType === 'all'}
                    onChange={(e) => setNotificationType(e.target.value as 'all' | 'specific')}
                    className="mr-2"
                  />
                  All Users
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="type"
                    value="specific"
                    checked={notificationType === 'specific'}
                    onChange={(e) => setNotificationType(e.target.value as 'all' | 'specific')}
                    className="mr-2"
                  />
                  Specific Users
                </label>
              </div>
            </div>

            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Title *
              </label>
              <input
                type="text"
                id="title"
                required
                value={notification.title}
                onChange={(e) => setNotification(prev => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter notification title"
              />
            </div>

            {/* Message */}
            <div>
              <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-2">
                Message *
              </label>
              <textarea
                id="body"
                required
                rows={4}
                value={notification.body}
                onChange={(e) => setNotification(prev => ({ ...prev, body: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter notification message"
              />
              <p className="text-xs text-gray-500 mt-1">
                Keep it concise and actionable
              </p>
            </div>

            {/* Send Button */}
            <button
              type="submit"
              disabled={sending}
              className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {sending ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Sending...
                </div>
              ) : (
                <div className="flex items-center">
                  <Send className="h-4 w-4 mr-2" />
                  Send Notification
                </div>
              )}
            </button>
          </form>
        </div>

        {/* Predefined Messages */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 flex items-center">
              <MessageSquare className="h-5 w-5 mr-2" />
              Quick Templates
            </h2>
          </div>
          
          <div className="p-6">
            <div className="space-y-4">
              {predefinedMessages.map((template, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                     onClick={() => setNotification({
                       title: template.title,
                       body: template.body,
                       data: template.data,
                       userIds: []
                     })}>
                  <h3 className="font-medium text-gray-900 mb-2">{template.title}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">{template.body}</p>
                  <div className="mt-2">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {template.data.type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Best Practices */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <div className="h-5 w-5 mr-2">💡</div>
          Notification Best Practices
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">✅ Do&apos;s</h3>
            <ul className="space-y-1 text-sm text-gray-700">
              <li>• Keep titles under 50 characters</li>
              <li>• Make messages actionable and clear</li>
              <li>• Send during appropriate hours (6 AM - 10 PM)</li>
              <li>• Personalize when possible</li>
              <li>• Test before sending to all users</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-900 mb-2">❌ Don&apos;ts</h3>
            <ul className="space-y-1 text-sm text-gray-700">
              <li>• Send too many notifications per day</li>
              <li>• Use ALL CAPS or excessive punctuation</li>
              <li>• Send promotional content frequently</li>
              <li>• Ignore user notification preferences</li>
              <li>• Send notifications during night hours</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}