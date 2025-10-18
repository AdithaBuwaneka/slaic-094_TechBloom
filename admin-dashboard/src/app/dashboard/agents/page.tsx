'use client';

import { useState, useEffect } from 'react';
import { agentAPI } from '../../../lib/api';
import { AgentSystemWorkflow } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge, BadgeProps } from '@/components/ui/badge';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  Clock, 
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Zap,
  Cpu
} from 'lucide-react';

export default function AgentSystemPage() {
  const [workflow, setWorkflow] = useState<AgentSystemWorkflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAgentSystemData();
  }, []);

  const loadAgentSystemData = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await agentAPI.getWorkflow();
      setWorkflow(data);
    } catch (error: unknown) {
      setError('Failed to load agent system data');
      console.error('Agent system error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusVariant = (status: string): BadgeProps['variant'] => {
    return status === 'active' || status === 'healthy' ? 'default' : 'destructive';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-1/3" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error Loading Agent System</AlertTitle>
        <AlertDescription>
          {error}
          <Button onClick={loadAgentSystemData} variant="secondary" className="mt-4">
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Agent System</h1>
        <p className="text-muted-foreground">{workflow?.workflow_description?.description}</p>
      </div>

      {/* System Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">Total Agents</CardTitle><Cpu className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{workflow?.system_stats?.total_agents || 0}</div></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">Active Agents</CardTitle><CheckCircle className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{workflow?.system_stats?.active_agents || 0}</div></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">Avg. Response Time</CardTitle><Clock className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{workflow?.system_stats?.average_workflow_time || 'N/A'}</div></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium">Success Rate</CardTitle><TrendingUp className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{workflow?.system_stats?.workflow_success_rate || 0}%</div></CardContent></Card>
      </div>

      {/* Agent Details Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
              <CardHeader><CardTitle>Agent Performance</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                  {workflow?.agent_details?.map((agent) => (
                      <div key={agent.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                              <p className="font-medium">{agent.name}</p>
                              <p className="text-xs text-muted-foreground">{agent.execution_time_avg} avg.</p>
                          </div>
                          <Badge variant={getStatusVariant(agent.status)}>{agent.status}</Badge>
                      </div>
                  ))}
              </CardContent>
          </Card>
          <Card>
              <CardHeader><CardTitle>Integrated Tools</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                   {workflow?.integrated_tools?.map((tool, index) => (
                      <div key={index} className="flex items-center justify-between">
                          <div>
                              <p className="font-medium">{tool.name}</p>
                              <p className="text-xs text-muted-foreground">{tool.usage}</p>
                          </div>
                          <Badge variant={getStatusVariant(tool.status)}>{tool.status}</Badge>
                      </div>
                  ))}
              </CardContent>
          </Card>
      </div>

      {/* Sri Lankan Optimizations */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="h-5 w-5 mr-2 text-blue-600" /> {workflow?.workflow_description?.name} - v{workflow?.workflow_description?.version}
          </CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium mb-3">Key Features</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {workflow?.workflow_description?.key_features?.map((feature, index) => (
                <li key={index} className="flex items-start"><CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5" />{feature}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-medium mb-3">Sri Lankan Optimizations</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {workflow?.workflow_description?.sri_lankan_optimizations?.map((optimization, index) => (
                <li key={index} className="flex items-start"><span className="mr-2 mt-0.5">🇱🇰</span>{optimization}</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

