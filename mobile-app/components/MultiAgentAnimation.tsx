import React, { useState, useEffect } from 'react';
import { View, Text, Modal, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withTiming, 
  withRepeat, 
  withSequence,
  runOnJS
} from 'react-native-reanimated';

interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  result?: string;
}

interface MultiAgentAnimationProps {
  visible: boolean;
  onComplete: (results: any) => void;
  onClose: () => void;
  requestData: {
    source: string;
    destination: string;
    mode: string;
  };
}

export default function MultiAgentAnimation({ 
  visible, 
  onComplete, 
  onClose, 
  requestData 
}: MultiAgentAnimationProps) {
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: '1',
      name: 'Input Processing Agent',
      description: 'Validating and processing user input',
      icon: '🔍',
      status: 'pending',
      progress: 0
    },
    {
      id: '2',
      name: 'Mode Router Agent',
      description: 'Analyzing travel mode requirements',
      icon: '🚦',
      status: 'pending',
      progress: 0
    },
    {
      id: '3',
      name: 'Transit Route Agent',
      description: 'Aggregating public transit options',
      icon: '🚌',
      status: 'pending',
      progress: 0
    },
    {
      id: '4',
      name: 'Fare Calculation Agent',
      description: 'Computing step-by-step pricing',
      icon: '💰',
      status: 'pending',
      progress: 0
    },
    {
      id: '5',
      name: 'Fare Optimization Agent',
      description: 'Finding cheapest combinations',
      icon: '📊',
      status: 'pending',
      progress: 0
    },
    {
      id: '6',
      name: 'User Preference Agent',
      description: 'Applying personal preferences',
      icon: '👤',
      status: 'pending',
      progress: 0
    },
    {
      id: '7',
      name: 'Local Knowledge Agent',
      description: 'Gathering contextual information',
      icon: '🌐',
      status: 'pending',
      progress: 0
    },
    {
      id: '8',
      name: 'Disruption Monitor Agent',
      description: 'Checking for delays and issues',
      icon: '⚠️',
      status: 'pending',
      progress: 0
    },
    {
      id: '9',
      name: 'Route Optimization Agent',
      description: 'Ranking and optimizing routes',
      icon: '🎯',
      status: 'pending',
      progress: 0
    },
    {
      id: '10',
      name: 'Response Compilation Agent',
      description: 'Finalizing recommendations',
      icon: '📋',
      status: 'pending',
      progress: 0
    }
  ]);

  const [currentAgentIndex, setCurrentAgentIndex] = useState(0);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  // Animation values
  const pulseScale = useSharedValue(1);
  const progressWidth = useSharedValue(0);

  useEffect(() => {
    if (visible) {
      startAgentProcessing();
    }
  }, [visible]);

  const startAgentProcessing = () => {
    setCurrentAgentIndex(0);
    setOverallProgress(0);
    setIsComplete(false);
    setAgents(prev => prev.map(agent => ({ ...agent, status: 'pending', progress: 0 })));
    processNextAgent(0);
  };

  const processNextAgent = (index: number) => {
    if (index >= agents.length) {
      completeProcessing();
      return;
    }

    setCurrentAgentIndex(index);
    
    // Start processing animation for current agent
    setAgents(prev => prev.map((agent, i) => 
      i === index ? { ...agent, status: 'processing' } : agent
    ));

    // Simulate agent processing time (varies by agent complexity)
    const processingTime = getAgentProcessingTime(index);
    
    // Animate progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setAgents(prev => prev.map((agent, i) => 
        i === index ? { ...agent, progress } : agent
      ));
      
      if (progress >= 100) {
        clearInterval(interval);
        completeAgent(index);
      }
    }, processingTime / 10);
  };

  const getAgentProcessingTime = (index: number): number => {
    // Different agents take different amounts of time
    const times = [800, 1200, 1500, 1000, 1300, 900, 1400, 1100, 1200, 700];
    return times[index] || 1000;
  };

  const completeAgent = (index: number) => {
    setAgents(prev => prev.map((agent, i) => 
      i === index ? { 
        ...agent, 
        status: 'completed', 
        progress: 100,
        result: getAgentResult(index)
      } : agent
    ));

    const newProgress = ((index + 1) / agents.length) * 100;
    setOverallProgress(newProgress);
    progressWidth.value = withTiming(newProgress, { duration: 300 });

    // Start next agent after a brief delay
    setTimeout(() => {
      processNextAgent(index + 1);
    }, 300);
  };

  const getAgentResult = (index: number): string => {
    const results = [
      'Input validated ✓',
      'Transit mode selected ✓',
      '3 route options found ✓',
      'Fares calculated ✓',
      'Cheapest option identified ✓',
      'Preferences applied ✓',
      'Local insights gathered ✓',
      'No disruptions detected ✓',
      'Routes optimized ✓',
      'Response ready ✓'
    ];
    return results[index] || 'Completed ✓';
  };

  const completeProcessing = () => {
    setIsComplete(true);
    
    // Generate mock results
    const results = {
      routes: [
        {
          id: '1',
          title: `${requestData.source} → ${requestData.destination}`,
          duration: '2h 30m',
          fare: 'Rs. 280',
          mode: requestData.mode,
          agentsUsed: agents.length,
          optimization: 'Fastest route with cost optimization'
        }
      ],
      agentSummary: {
        totalAgents: agents.length,
        processingTime: '12.3 seconds',
        optimizationLevel: 'Maximum'
      }
    };

    setTimeout(() => {
      onComplete(results);
    }, 2000);
  };

  // Pulse animation for active agent
  useEffect(() => {
    pulseScale.value = withRepeat(
      withSequence(
        withTiming(1.1, { duration: 600 }),
        withTiming(1, { duration: 600 })
      ),
      -1,
      true
    );
  }, []);

  const animatedPulseStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: pulseScale.value }]
    };
  });

  const animatedProgressStyle = useAnimatedStyle(() => {
    return {
      width: `${progressWidth.value}%`
    };
  });

  return (
    <Modal visible={visible} animationType="slide" transparent>
      <View className="flex-1 bg-black/50">
        <SafeAreaView className="flex-1">
          <View className="flex-1 bg-white m-4 rounded-lg">
            {/* Header */}
            <View className="bg-blue-600 p-4 rounded-t-lg">
              <View className="flex-row items-center justify-between">
                <View>
                  <Text className="text-white text-lg font-bold">🤖 AI Agents Processing</Text>
                  <Text className="text-blue-100 text-sm">
                    {requestData.source} → {requestData.destination}
                  </Text>
                </View>
                <TouchableOpacity onPress={onClose} className="p-2">
                  <Text className="text-white text-lg">✕</Text>
                </TouchableOpacity>
              </View>
              
              {/* Overall Progress */}
              <View className="mt-4">
                <View className="flex-row justify-between mb-2">
                  <Text className="text-white text-sm">Overall Progress</Text>
                  <Text className="text-white text-sm">{Math.round(overallProgress)}%</Text>
                </View>
                <View className="bg-blue-500 h-2 rounded-full overflow-hidden">
                  <Animated.View 
                    className="bg-white h-full"
                    style={animatedProgressStyle}
                  />
                </View>
              </View>
            </View>

            {/* Agents List */}
            <ScrollView 
              className="flex-1 p-4" 
              showsVerticalScrollIndicator={true}
              contentContainerStyle={{ flexGrow: 1 }}
            >
              {isComplete ? (
                <View className="flex-1 justify-center items-center">
                  <Text className="text-6xl mb-4">🎉</Text>
                  <Text className="text-2xl font-bold text-green-600 mb-2">Processing Complete!</Text>
                  <Text className="text-gray-600 text-center mb-4">
                    All 10 AI agents have successfully analyzed your route
                  </Text>
                  <View className="bg-green-50 p-4 rounded-lg">
                    <Text className="text-green-800 text-center">
                      ✓ Routes optimized with fare calculation{'\n'}
                      ✓ Real-time disruptions checked{'\n'}
                      ✓ Personal preferences applied{'\n'}
                      ✓ Best recommendations ready
                    </Text>
                  </View>
                </View>
              ) : (
                <View>
                  {agents.map((agent, index) => (
                    <View key={agent.id} style={{ marginBottom: 12 }}>
                      <View className={`p-3 rounded-lg border ${
                        agent.status === 'completed' ? 'bg-green-50 border-green-200' :
                        agent.status === 'processing' ? 'bg-blue-50 border-blue-200' :
                        'bg-gray-50 border-gray-200'
                      }`}>
                        <View className="flex-row items-center justify-between mb-2">
                          <View className="flex-row items-center flex-1">
                            {index === currentAgentIndex && agent.status === 'processing' ? (
                              <Animated.Text 
                                style={animatedPulseStyle}
                                className="text-lg mr-3"
                              >
                                {agent.icon}
                              </Animated.Text>
                            ) : (
                              <Text className="text-lg mr-3">{agent.icon}</Text>
                            )}
                            <View className="flex-1">
                              <Text className={`font-medium ${
                                agent.status === 'completed' ? 'text-green-800' :
                                agent.status === 'processing' ? 'text-blue-800' :
                                'text-gray-600'
                              }`}>
                                {agent.name}
                              </Text>
                              <Text className="text-xs text-gray-500">{agent.description}</Text>
                            </View>
                          </View>
                          
                          <View className="items-end">
                            {agent.status === 'completed' && (
                              <Text className="text-green-600 text-lg">✓</Text>
                            )}
                            {agent.status === 'processing' && (
                              <View className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full" />
                            )}
                            {agent.status === 'pending' && (
                              <Text className="text-gray-400 text-lg">⏳</Text>
                            )}
                          </View>
                        </View>
                        
                        {/* Agent Progress Bar */}
                        {agent.status === 'processing' && (
                          <View className="mt-2">
                            <View className="bg-blue-200 h-1 rounded-full overflow-hidden">
                              <View
                                className="bg-blue-600 h-full"
                                style={{ width: `${agent.progress}%` }}
                              />
                            </View>
                          </View>
                        )}
                        
                        {/* Agent Result */}
                        {agent.result && (
                          <Text className="text-xs text-green-600 mt-1">{agent.result}</Text>
                        )}
                      </View>
                    </View>
                  ))}
                </View>
              )}
            </ScrollView>

            {/* Footer Stats */}
            <View className="bg-gray-50 p-4 rounded-b-lg border-t border-gray-200">
              <View className="flex-row justify-between">
                <View className="items-center">
                  <Text className="text-lg font-bold text-blue-600">{agents.filter(a => a.status === 'completed').length}</Text>
                  <Text className="text-xs text-gray-600">Completed</Text>
                </View>
                <View className="items-center">
                  <Text className="text-lg font-bold text-orange-600">
                    {agents.filter(a => a.status === 'processing').length}
                  </Text>
                  <Text className="text-xs text-gray-600">Processing</Text>
                </View>
                <View className="items-center">
                  <Text className="text-lg font-bold text-gray-600">
                    {agents.filter(a => a.status === 'pending').length}
                  </Text>
                  <Text className="text-xs text-gray-600">Pending</Text>
                </View>
                <View className="items-center">
                  <Text className="text-lg font-bold text-purple-600">10</Text>
                  <Text className="text-xs text-gray-600">Total Agents</Text>
                </View>
              </View>
            </View>
          </View>
        </SafeAreaView>
      </View>
    </Modal>
  );
}