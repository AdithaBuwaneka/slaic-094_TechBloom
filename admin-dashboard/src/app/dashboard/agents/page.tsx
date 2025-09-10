'use client';

import { useState, useEffect, useRef } from 'react';
import { agentAPI } from '@/lib/api';
import { AgentSystemWorkflow } from '@/lib/types';
import { 
  GitBranch, 
  Activity, 
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
  const mermaidRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadAgentSystemData();
  }, []);

  useEffect(() => {
    if (workflow?.mermaid_diagram && mermaidRef.current) {
      renderMermaidDiagram();
    }
  }, [workflow]);

  const loadAgentSystemData = async () => {
    try {
      setLoading(true);
      const data = await agentAPI.getWorkflow();
      setWorkflow(data);
    } catch (error: any) {
      setError('Failed to load agent system data');
      console.error('Agent system error:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderMermaidDiagram = async () => {
    try {
      const mermaid = (await import('mermaid')).default;
      
      mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'Arial, sans-serif',
        fontSize: 14,
        flowchart: {
          htmlLabels: false,
          curve: 'basis',
          padding: 10,
        },
      });

      if (mermaidRef.current && workflow?.mermaid_diagram) {
        // Clear previous content
        mermaidRef.current.innerHTML = '';
        
        // Create a unique ID for this diagram
        const diagramId = `mermaid-diagram-${Date.now()}`;
        
        // Render the diagram
        const { svg } = await mermaid.render(diagramId, workflow.mermaid_diagram.trim());
        mermaidRef.current.innerHTML = svg;
      }
    } catch (error) {
      console.error('Error rendering mermaid diagram:', error);
      if (mermaidRef.current) {
        mermaidRef.current.innerHTML = `
          <div class="text-center text-gray-500 py-8">
            <p class="mb-2">Unable to render workflow diagram</p>
            <p class="text-sm">Please check the diagram syntax</p>
          </div>
        `;
      }
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'active' ? 'text-green-600' : 'text-red-600';
  };

  const getStatusBadge = (status: string) => {
    return status === 'active' 
      ? 'bg-green-100 text-green-800' 
      : 'bg-red-100 text-red-800';
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 95) return 'text-green-600';
    if (rate >= 90) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Agent System Workflow</h1>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
          <div className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-12 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
          <h3 className="text-red-800 font-medium">Error Loading Agent System</h3>
        </div>
        <p className="text-red-700 mt-2">{error}</p>
        <button
          onClick={loadAgentSystemData}
          className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agent System Workflow</h1>
          <p className="text-gray-600">{workflow?.workflow_description?.description}</p>
        </div>
      </div>

      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Cpu className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Agents</p>
              <p className="text-lg font-bold text-gray-900">{workflow?.system_stats?.total_agents || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Active Agents</p>
              <p className="text-lg font-bold text-gray-900">{workflow?.system_stats?.active_agents || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
              <p className="text-lg font-bold text-gray-900">{workflow?.system_stats?.average_workflow_time || 'N/A'}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-lg font-bold text-gray-900">{workflow?.system_stats?.workflow_success_rate || 0}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Workflow Diagram */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900 flex items-center">
            <GitBranch className="h-5 w-5 mr-2" />
            Multi-Agent Workflow Diagram
          </h2>
        </div>
        <div className="p-6">
          <div 
            ref={mermaidRef} 
            className="flex justify-center items-center min-h-[400px] bg-gray-50 rounded-lg p-4 overflow-auto"
          >
            {/* Mermaid diagram will be rendered here */}
            {!workflow?.mermaid_diagram && (
              <p className="text-gray-500">Loading workflow diagram...</p>
            )}
          </div>
        </div>
      </div>

      {/* Agent Details */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Agent Performance Details</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {workflow?.agent_details?.map((agent, index) => (
              <div key={agent.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{agent.name}</h3>
                    <p className="text-sm text-gray-600">{agent.description}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(agent.status)}`}>
                    {agent.status}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div>
                    <p className="text-xs text-gray-500">Execution Time</p>
                    <p className="font-medium flex items-center">
                      <Clock className="h-4 w-4 mr-1 text-gray-400" />
                      {agent.execution_time_avg}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Success Rate</p>
                    <p className={`font-medium flex items-center ${getSuccessRateColor(agent.success_rate)}`}>
                      <Activity className="h-4 w-4 mr-1" />
                      {agent.success_rate.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">System Statistics</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total Requests Processed</span>
                <span className="font-medium">{workflow?.system_stats?.total_requests_processed?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Requests Last 24h</span>
                <span className="font-medium">{workflow?.system_stats?.requests_last_24h || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Multi-Agent Usage Rate</span>
                <span className="font-medium">{workflow?.system_stats?.multi_agent_usage_rate || 0}%</span>
              </div>
              <div className="pt-4 border-t border-gray-200">
                <span className="text-sm text-gray-600">Most Used Path</span>
                <p className="text-sm font-medium text-blue-600 mt-1">
                  {workflow?.system_stats?.most_used_path || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Integrated Tools</h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {workflow?.integrated_tools?.map((tool, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{tool.name}</p>
                    <p className="text-sm text-gray-600">{tool.usage}</p>
                  </div>
                  <div className="flex items-center">
                    <div className={`h-2 w-2 rounded-full mr-2 ${
                      tool.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <span className={`text-sm font-medium ${getStatusColor(tool.status)}`}>
                      {tool.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Sri Lankan Optimizations */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Zap className="h-6 w-6 text-blue-600 mr-2" />
          <h2 className="text-lg font-medium text-gray-900">
            {workflow?.workflow_description?.name} - {workflow?.workflow_description?.version}
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-900 mb-3">Key Features</h3>
            <ul className="space-y-2">
              {workflow?.workflow_description?.key_features?.map((feature, index) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-900 mb-3">Sri Lankan Optimizations</h3>
            <ul className="space-y-2">
              {workflow?.workflow_description?.sri_lankan_optimizations?.map((optimization, index) => (
                <li key={index} className="flex items-start">
                  <div className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0">🇱🇰</div>
                  <span className="text-sm text-gray-700">{optimization}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}