from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum


class OrchestrationStrategy(str, Enum):
    SEQUENTIAL = "sequential"           # Execute agents one by one
    PARALLEL = "parallel"              # Execute all agents simultaneously
    PIPELINE = "pipeline"              # Chain agent outputs as inputs
    CONDITIONAL = "conditional"        # Execute based on conditions
    PRIORITY_BASED = "priority_based"  # Execute by priority order
    COLLABORATIVE = "collaborative"    # Agents work together on sub-tasks


class ExecutionMode(str, Enum):
    SYNCHRONOUS = "synchronous"        # Wait for all agents
    ASYNCHRONOUS = "asynchronous"      # Don't wait for completion
    STREAMING = "streaming"            # Stream results as they arrive
    BATCH = "batch"                    # Process in batches


class ConflictResolutionMethod(str, Enum):
    WEIGHTED_VOTING = "weighted_voting"
    HIGHEST_CONFIDENCE = "highest_confidence"
    CONSENSUS_BASED = "consensus_based"
    EXPERT_OVERRIDE = "expert_override"
    MAJORITY_VOTE = "majority_vote"
    HYBRID_APPROACH = "hybrid_approach"


class AgentRole(str, Enum):
    PRIMARY = "primary"                # Main agent for this request type
    SUPPORTING = "supporting"          # Provides additional context
    VALIDATOR = "validator"           # Validates results from other agents
    OPTIMIZER = "optimizer"           # Optimizes solutions from other agents
    MONITOR = "monitor"               # Monitors performance and quality


class OrchestrationRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    request_type: str
    payload: Dict[str, Any]
    strategy: OrchestrationStrategy = OrchestrationStrategy.PARALLEL
    execution_mode: ExecutionMode = ExecutionMode.SYNCHRONOUS
    conflict_resolution: ConflictResolutionMethod = ConflictResolutionMethod.WEIGHTED_VOTING
    timeout_seconds: float = 10.0
    max_retries: int = 2
    priority: int = Field(default=5, ge=1, le=10)
    
    # Agent-specific configurations
    required_agents: List[str] = []
    excluded_agents: List[str] = []
    agent_roles: Dict[str, AgentRole] = {}
    agent_weights: Dict[str, float] = {}
    
    # Quality requirements
    min_confidence_threshold: float = 0.5
    require_consensus: bool = False
    consensus_threshold: float = 0.7
    
    # Performance constraints
    max_processing_time: Optional[float] = None
    resource_limits: Dict[str, Any] = {}
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentExecutionPlan(BaseModel):
    agent_id: str
    role: AgentRole
    execution_order: int
    depends_on: List[str] = []  # Agent IDs this execution depends on
    timeout_seconds: float
    weight: float = 1.0
    retry_count: int = 0
    max_retries: int = 2
    
    # Resource allocation
    cpu_priority: int = 1
    memory_limit_mb: Optional[int] = None
    
    # Quality metrics
    expected_confidence: float = 0.8
    quality_weight: float = 1.0


class OrchestrationPlan(BaseModel):
    request_id: str
    strategy: OrchestrationStrategy
    execution_mode: ExecutionMode
    agent_plans: List[AgentExecutionPlan]
    estimated_duration: float
    estimated_cost: float = 0.0
    quality_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentExecutionResult(BaseModel):
    agent_id: str
    success: bool
    data: Dict[str, Any] = {}
    error: Optional[str] = None
    processing_time: float
    confidence_score: float = 0.0
    quality_metrics: Dict[str, float] = {}
    resource_usage: Dict[str, Any] = {}
    timestamp: datetime
    retry_count: int = 0


class OrchestrationResult(BaseModel):
    request_id: str
    success: bool
    final_result: Dict[str, Any] = {}
    error: Optional[str] = None
    
    # Execution details
    strategy_used: OrchestrationStrategy
    execution_mode: ExecutionMode
    conflict_resolution_used: ConflictResolutionMethod
    
    # Agent results
    agent_results: List[AgentExecutionResult] = []
    successful_agents: int = 0
    failed_agents: int = 0
    
    # Performance metrics
    total_processing_time: float
    orchestration_overhead: float
    quality_score: float = 0.0
    confidence_score: float = 0.0
    
    # Resource usage
    total_resource_usage: Dict[str, Any] = {}
    cost_breakdown: Dict[str, float] = {}
    
    # Quality and reliability metrics
    consensus_achieved: bool = False
    consensus_percentage: float = 0.0
    conflict_resolution_applied: bool = False
    
    created_at: datetime
    completed_at: datetime


class SystemPerformanceMetrics(BaseModel):
    timestamp: datetime
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    
    # Agent metrics
    agent_utilization: Dict[str, float] = {}  # agent_id -> utilization %
    agent_success_rates: Dict[str, float] = {}  # agent_id -> success rate
    agent_average_response_times: Dict[str, float] = {}  # agent_id -> avg time
    
    # Quality metrics
    average_confidence_score: float = 0.0
    consensus_achievement_rate: float = 0.0
    conflict_resolution_frequency: float = 0.0
    
    # System health
    memory_usage_mb: float = 0.0
    cpu_utilization: float = 0.0
    active_connections: int = 0
    queue_sizes: Dict[str, int] = {}


class OrchestrationConfig(BaseModel):
    # Global settings
    default_timeout: float = 10.0
    max_concurrent_requests: int = 100
    default_strategy: OrchestrationStrategy = OrchestrationStrategy.PARALLEL
    default_execution_mode: ExecutionMode = ExecutionMode.SYNCHRONOUS
    
    # Quality settings
    min_quality_threshold: float = 0.6
    consensus_threshold: float = 0.7
    confidence_threshold: float = 0.5
    
    # Performance settings
    performance_monitoring_enabled: bool = True
    metrics_collection_interval: int = 60  # seconds
    auto_scaling_enabled: bool = False
    
    # Agent management
    agent_health_check_interval: int = 30  # seconds
    max_retry_attempts: int = 3
    backoff_multiplier: float = 1.5
    
    # Resource limits
    max_memory_usage_mb: int = 1024
    max_cpu_utilization: float = 0.8
    max_queue_size: int = 1000


class ConflictResolutionContext(BaseModel):
    request_id: str
    conflicting_results: List[AgentExecutionResult]
    resolution_method: ConflictResolutionMethod
    context_data: Dict[str, Any] = {}
    user_preferences: Dict[str, Any] = {}
    domain_constraints: Dict[str, Any] = {}
    
    # Resolution parameters
    weight_factors: Dict[str, float] = {
        "agent_reliability": 0.3,
        "result_confidence": 0.25,
        "processing_time": 0.15,
        "historical_accuracy": 0.2,
        "user_preference_match": 0.1
    }


class QualityAssessment(BaseModel):
    request_id: str
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    
    # Component scores
    accuracy_score: float = Field(ge=0.0, le=1.0)
    completeness_score: float = Field(ge=0.0, le=1.0)
    consistency_score: float = Field(ge=0.0, le=1.0)
    timeliness_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    
    # Quality factors
    agent_agreement_level: float = Field(ge=0.0, le=1.0)
    confidence_alignment: float = Field(ge=0.0, le=1.0)
    result_coherence: float = Field(ge=0.0, le=1.0)
    
    # Recommendations for improvement
    improvement_suggestions: List[str] = []
    quality_issues_identified: List[str] = []
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OptimizationRecommendation(BaseModel):
    request_type: str
    current_performance: Dict[str, float]
    suggested_strategy: OrchestrationStrategy
    suggested_agent_selection: List[str]
    estimated_improvement: Dict[str, float]
    implementation_effort: str  # low, medium, high
    risk_level: str  # low, medium, high
    reasoning: str
    created_at: datetime = Field(default_factory=datetime.utcnow)