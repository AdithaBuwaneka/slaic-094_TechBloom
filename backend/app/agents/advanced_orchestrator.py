from typing import Dict, List, Optional, Any, Tuple
from app.agents.base_agent import BaseAgent, AgentMessage, AgentResponse
from app.models.orchestration import (
    OrchestrationRequest, OrchestrationPlan, AgentExecutionPlan,
    AgentExecutionResult, OrchestrationResult, SystemPerformanceMetrics,
    OrchestrationConfig, ConflictResolutionContext, QualityAssessment,
    OptimizationRecommendation, OrchestrationStrategy, ExecutionMode,
    ConflictResolutionMethod, AgentRole
)
import asyncio
from datetime import datetime, timedelta
import json
import uuid
from collections import defaultdict
import statistics


class AdvancedOrchestrator:
    """
    Advanced Multi-Agent Orchestration System
    
    Provides sophisticated coordination, conflict resolution, and optimization
    for complex multi-agent interactions in the transit companion system.
    """
    
    def __init__(self, config: OrchestrationConfig = None):
        self.config = config or OrchestrationConfig()
        self.agents: Dict[str, BaseAgent] = {}
        
        # Performance tracking
        self.performance_metrics = SystemPerformanceMetrics(timestamp=datetime.utcnow())
        self.request_history: List[OrchestrationResult] = []
        self.quality_assessments: Dict[str, QualityAssessment] = {}
        
        # Execution state
        self.active_requests: Dict[str, OrchestrationRequest] = {}
        self.execution_plans: Dict[str, OrchestrationPlan] = {}
        
        # Optimization state
        self.strategy_performance: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        self.agent_performance_history: Dict[str, List[AgentExecutionResult]] = defaultdict(list)
        
        # Monitoring
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self):
        """Start performance monitoring and optimization"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    async def orchestrate_request(self, request: OrchestrationRequest) -> OrchestrationResult:
        """Main orchestration method with advanced coordination"""
        start_time = datetime.utcnow()
        
        try:
            # Store active request
            self.active_requests[request.request_id] = request
            
            # Create execution plan
            plan = await self._create_execution_plan(request)
            self.execution_plans[request.request_id] = plan
            
            # Execute based on strategy
            agent_results = await self._execute_plan(plan, request)
            
            # Apply conflict resolution
            resolved_result = await self._resolve_conflicts(agent_results, request)
            
            # Assess quality
            quality_assessment = await self._assess_quality(request.request_id, agent_results, resolved_result)
            
            # Create final result
            end_time = datetime.utcnow()
            orchestration_result = OrchestrationResult(
                request_id=request.request_id,
                success=len([r for r in agent_results if r.success]) > 0,
                final_result=resolved_result,
                strategy_used=request.strategy,
                execution_mode=request.execution_mode,
                conflict_resolution_used=request.conflict_resolution,
                agent_results=agent_results,
                successful_agents=len([r for r in agent_results if r.success]),
                failed_agents=len([r for r in agent_results if not r.success]),
                total_processing_time=(end_time - start_time).total_seconds(),
                orchestration_overhead=0.1,  # Simplified calculation
                quality_score=quality_assessment.overall_quality_score,
                confidence_score=statistics.mean([r.confidence_score for r in agent_results if r.success]) if agent_results else 0.0,
                created_at=start_time,
                completed_at=end_time
            )
            
            # Store results for learning
            self.request_history.append(orchestration_result)
            self.quality_assessments[request.request_id] = quality_assessment
            
            # Update performance tracking
            await self._update_performance_metrics(orchestration_result)
            
            return orchestration_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            return OrchestrationResult(
                request_id=request.request_id,
                success=False,
                error=str(e),
                strategy_used=request.strategy,
                execution_mode=request.execution_mode,
                conflict_resolution_used=request.conflict_resolution,
                agent_results=[],
                successful_agents=0,
                failed_agents=len(self.agents),
                total_processing_time=(end_time - start_time).total_seconds(),
                orchestration_overhead=0.0,
                created_at=start_time,
                completed_at=end_time
            )
        finally:
            # Cleanup
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]
            if request.request_id in self.execution_plans:
                del self.execution_plans[request.request_id]
    
    async def _create_execution_plan(self, request: OrchestrationRequest) -> OrchestrationPlan:
        """Create an optimized execution plan based on request requirements"""
        
        # Determine which agents to use
        available_agents = self._select_agents(request)
        
        # Create agent execution plans
        agent_plans = []
        for i, agent_id in enumerate(available_agents):
            agent = self.agents[agent_id]
            
            # Determine role
            role = request.agent_roles.get(agent_id, AgentRole.PRIMARY)
            if agent_id in request.required_agents:
                role = AgentRole.PRIMARY
            
            # Calculate timeout and weight
            timeout = request.timeout_seconds / max(1, len(available_agents))
            weight = request.agent_weights.get(agent_id, agent.priority_weight)
            
            # Determine execution order based on strategy
            execution_order = self._calculate_execution_order(request.strategy, agent_id, i)
            
            # Determine dependencies
            depends_on = self._calculate_dependencies(request.strategy, agent_id, available_agents[:i])
            
            plan = AgentExecutionPlan(
                agent_id=agent_id,
                role=role,
                execution_order=execution_order,
                depends_on=depends_on,
                timeout_seconds=timeout,
                weight=weight,
                max_retries=request.max_retries
            )
            agent_plans.append(plan)
        
        # Sort by execution order
        agent_plans.sort(key=lambda x: x.execution_order)
        
        # Calculate estimates
        estimated_duration = self._estimate_execution_duration(agent_plans, request.strategy)
        estimated_cost = self._estimate_execution_cost(agent_plans)
        quality_score = self._estimate_quality_score(agent_plans)
        
        return OrchestrationPlan(
            request_id=request.request_id,
            strategy=request.strategy,
            execution_mode=request.execution_mode,
            agent_plans=agent_plans,
            estimated_duration=estimated_duration,
            estimated_cost=estimated_cost,
            quality_score=quality_score
        )
    
    def _select_agents(self, request: OrchestrationRequest) -> List[str]:
        """Select appropriate agents for the request"""
        available_agents = []
        
        # Start with required agents
        for agent_id in request.required_agents:
            if agent_id in self.agents and self.agents[agent_id].is_active:
                available_agents.append(agent_id)
        
        # Add other suitable agents
        for agent_id, agent in self.agents.items():
            if (agent.is_active and 
                agent_id not in request.excluded_agents and 
                agent_id not in available_agents):
                
                # Simple capability matching (in production, this would be more sophisticated)
                if self._agent_matches_request(agent, request):
                    available_agents.append(agent_id)
        
        return available_agents
    
    def _agent_matches_request(self, agent: BaseAgent, request: OrchestrationRequest) -> bool:
        """Check if an agent is suitable for handling the request type"""
        
        # Map request types to relevant agents
        request_agent_mapping = {
            "get_transport_data": ["data_aggregation_agent"],
            "optimize_routes": ["route_optimization_agent"],
            "get_disruptions": ["disruption_management_agent"],
            "get_local_knowledge": ["local_knowledge_agent"],
            "get_personalization": ["personalization_agent"],
            "optimize_fare": ["fare_optimization_agent"],
            "get_accessibility": ["language_accessibility_agent"]
        }
        
        relevant_agents = request_agent_mapping.get(request.request_type, [])
        return agent.agent_id in relevant_agents or len(relevant_agents) == 0
    
    def _calculate_execution_order(self, strategy: OrchestrationStrategy, agent_id: str, index: int) -> int:
        """Calculate execution order based on strategy"""
        if strategy == OrchestrationStrategy.SEQUENTIAL:
            return index
        elif strategy == OrchestrationStrategy.PARALLEL:
            return 0  # All execute at same time
        elif strategy == OrchestrationStrategy.PRIORITY_BASED:
            agent = self.agents[agent_id]
            return int((1.0 - agent.priority_weight) * 10)  # Higher weight = lower order number
        else:
            return index
    
    def _calculate_dependencies(self, strategy: OrchestrationStrategy, agent_id: str, previous_agents: List[str]) -> List[str]:
        """Calculate agent dependencies based on strategy"""
        if strategy == OrchestrationStrategy.PIPELINE:
            return previous_agents[-1:] if previous_agents else []
        elif strategy == OrchestrationStrategy.SEQUENTIAL:
            return previous_agents[-1:] if previous_agents else []
        else:
            return []  # No dependencies for parallel execution
    
    async def _execute_plan(self, plan: OrchestrationPlan, request: OrchestrationRequest) -> List[AgentExecutionResult]:
        """Execute the orchestration plan"""
        results = []
        
        if request.execution_mode == ExecutionMode.SYNCHRONOUS:
            results = await self._execute_synchronous(plan, request)
        elif request.execution_mode == ExecutionMode.ASYNCHRONOUS:
            results = await self._execute_asynchronous(plan, request)
        elif request.execution_mode == ExecutionMode.STREAMING:
            results = await self._execute_streaming(plan, request)
        else:
            results = await self._execute_parallel(plan, request)
        
        return results
    
    async def _execute_synchronous(self, plan: OrchestrationPlan, request: OrchestrationRequest) -> List[AgentExecutionResult]:
        """Execute agents synchronously based on their execution order"""
        results = []
        completed_agents = set()
        
        # Group by execution order
        order_groups = defaultdict(list)
        for agent_plan in plan.agent_plans:
            order_groups[agent_plan.execution_order].append(agent_plan)
        
        # Execute in order
        for order in sorted(order_groups.keys()):
            group_tasks = []
            for agent_plan in order_groups[order]:
                # Check dependencies
                if all(dep in completed_agents for dep in agent_plan.depends_on):
                    task = self._execute_single_agent(agent_plan, request)
                    group_tasks.append(task)
            
            # Wait for this order group to complete
            if group_tasks:
                group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
                for result in group_results:
                    if isinstance(result, AgentExecutionResult):
                        results.append(result)
                        if result.success:
                            completed_agents.add(result.agent_id)
        
        return results
    
    async def _execute_parallel(self, plan: OrchestrationPlan, request: OrchestrationRequest) -> List[AgentExecutionResult]:
        """Execute all agents in parallel"""
        tasks = []
        for agent_plan in plan.agent_plans:
            task = self._execute_single_agent(agent_plan, request)
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if isinstance(r, AgentExecutionResult)]
        
        return []
    
    async def _execute_asynchronous(self, plan: OrchestrationPlan, request: OrchestrationRequest) -> List[AgentExecutionResult]:
        """Execute agents asynchronously (fire and forget)"""
        tasks = []
        for agent_plan in plan.agent_plans:
            task = asyncio.create_task(self._execute_single_agent(agent_plan, request))
            tasks.append(task)
        
        # Don't wait for completion, return immediately
        return []
    
    async def _execute_streaming(self, plan: OrchestrationPlan, request: OrchestrationRequest) -> List[AgentExecutionResult]:
        """Execute agents and stream results as they become available"""
        # For now, implement as parallel execution
        return await self._execute_parallel(plan, request)
    
    async def _execute_single_agent(self, agent_plan: AgentExecutionPlan, request: OrchestrationRequest) -> AgentExecutionResult:
        """Execute a single agent with retry logic"""
        agent = self.agents[agent_plan.agent_id]
        start_time = datetime.utcnow()
        
        for attempt in range(agent_plan.max_retries + 1):
            try:
                # Create message
                message = AgentMessage(
                    id=f"{request.request_id}_{agent.agent_id}_{attempt}",
                    sender_id="advanced_orchestrator",
                    message_type="process_request",
                    payload=request.payload,
                    timestamp=datetime.utcnow(),
                    priority=request.priority
                )
                
                # Execute agent
                result = await asyncio.wait_for(
                    agent.process_request(request.payload),
                    timeout=agent_plan.timeout_seconds
                )
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                # Calculate confidence score
                confidence_score = result.get("confidence_score", 0.8)
                if not result.get("success", True):
                    confidence_score = 0.0
                
                return AgentExecutionResult(
                    agent_id=agent.agent_id,
                    success=result.get("success", True),
                    data=result.get("data", result),
                    processing_time=processing_time,
                    confidence_score=confidence_score,
                    timestamp=end_time,
                    retry_count=attempt
                )
                
            except asyncio.TimeoutError:
                if attempt == agent_plan.max_retries:
                    end_time = datetime.utcnow()
                    return AgentExecutionResult(
                        agent_id=agent.agent_id,
                        success=False,
                        error=f"Timeout after {agent_plan.timeout_seconds}s",
                        processing_time=(end_time - start_time).total_seconds(),
                        timestamp=end_time,
                        retry_count=attempt
                    )
                continue
            except Exception as e:
                if attempt == agent_plan.max_retries:
                    end_time = datetime.utcnow()
                    return AgentExecutionResult(
                        agent_id=agent.agent_id,
                        success=False,
                        error=str(e),
                        processing_time=(end_time - start_time).total_seconds(),
                        timestamp=end_time,
                        retry_count=attempt
                    )
                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                continue
    
    async def _resolve_conflicts(self, agent_results: List[AgentExecutionResult], request: OrchestrationRequest) -> Dict[str, Any]:
        """Advanced conflict resolution with multiple strategies"""
        
        successful_results = [r for r in agent_results if r.success]
        
        if not successful_results:
            return {"success": False, "error": "No successful agent responses"}
        
        if len(successful_results) == 1:
            return successful_results[0].data
        
        # Apply conflict resolution method
        context = ConflictResolutionContext(
            request_id=request.request_id,
            conflicting_results=successful_results,
            resolution_method=request.conflict_resolution
        )
        
        if request.conflict_resolution == ConflictResolutionMethod.WEIGHTED_VOTING:
            return await self._weighted_voting_resolution(context)
        elif request.conflict_resolution == ConflictResolutionMethod.HIGHEST_CONFIDENCE:
            return await self._highest_confidence_resolution(context)
        elif request.conflict_resolution == ConflictResolutionMethod.CONSENSUS_BASED:
            return await self._consensus_based_resolution(context)
        else:
            return await self._weighted_voting_resolution(context)  # Default
    
    async def _weighted_voting_resolution(self, context: ConflictResolutionContext) -> Dict[str, Any]:
        """Resolve conflicts using weighted voting"""
        total_weight = 0
        weighted_data = {}
        
        for result in context.conflicting_results:
            agent = self.agents[result.agent_id]
            weight = agent.priority_weight * result.confidence_score
            total_weight += weight
            
            # Merge response data with weights
            for key, value in result.data.items():
                if key not in weighted_data:
                    weighted_data[key] = []
                weighted_data[key].append({
                    "value": value,
                    "weight": weight,
                    "agent_id": result.agent_id
                })
        
        # Create resolved response
        resolved_data = {}
        for key, values in weighted_data.items():
            if len(values) == 1:
                resolved_data[key] = values[0]["value"]
            else:
                # Use the value from the highest weighted agent
                best_value = max(values, key=lambda x: x["weight"])
                resolved_data[key] = best_value["value"]
        
        resolved_data["success"] = True
        resolved_data["resolution_method"] = "weighted_voting"
        return resolved_data
    
    async def _highest_confidence_resolution(self, context: ConflictResolutionContext) -> Dict[str, Any]:
        """Use result from agent with highest confidence"""
        best_result = max(context.conflicting_results, key=lambda x: x.confidence_score)
        result_data = best_result.data.copy()
        result_data["resolution_method"] = "highest_confidence"
        return result_data
    
    async def _consensus_based_resolution(self, context: ConflictResolutionContext) -> Dict[str, Any]:
        """Attempt to find consensus among agent results"""
        # Simplified consensus implementation
        # In practice, this would analyze result similarity and agreement
        
        if len(context.conflicting_results) < 2:
            return context.conflicting_results[0].data
        
        # For now, use weighted voting as fallback
        return await self._weighted_voting_resolution(context)
    
    async def _assess_quality(self, request_id: str, agent_results: List[AgentExecutionResult], final_result: Dict[str, Any]) -> QualityAssessment:
        """Assess the quality of the orchestration result"""
        
        successful_results = [r for r in agent_results if r.success]
        
        if not successful_results:
            return QualityAssessment(
                request_id=request_id,
                overall_quality_score=0.0,
                accuracy_score=0.0,
                completeness_score=0.0,
                consistency_score=0.0,
                timeliness_score=0.0,
                relevance_score=0.0,
                agent_agreement_level=0.0,
                confidence_alignment=0.0,
                result_coherence=0.0
            )
        
        # Calculate quality metrics
        confidence_scores = [r.confidence_score for r in successful_results]
        avg_confidence = statistics.mean(confidence_scores)
        
        # Agreement level (simplified)
        agreement_level = min(1.0, len(successful_results) / len(agent_results))
        
        # Consistency (measure of how similar results are)
        consistency_score = 0.8  # Simplified calculation
        
        # Overall quality score
        overall_quality = (avg_confidence * 0.4 + 
                          agreement_level * 0.3 + 
                          consistency_score * 0.3)
        
        return QualityAssessment(
            request_id=request_id,
            overall_quality_score=overall_quality,
            accuracy_score=avg_confidence,
            completeness_score=agreement_level,
            consistency_score=consistency_score,
            timeliness_score=0.8,  # Based on execution time
            relevance_score=0.9,   # Assumed high for matched agents
            agent_agreement_level=agreement_level,
            confidence_alignment=1.0 - statistics.stdev(confidence_scores) if len(confidence_scores) > 1 else 1.0,
            result_coherence=consistency_score
        )
    
    def _estimate_execution_duration(self, agent_plans: List[AgentExecutionPlan], strategy: OrchestrationStrategy) -> float:
        """Estimate total execution duration"""
        if strategy == OrchestrationStrategy.PARALLEL:
            return max(plan.timeout_seconds for plan in agent_plans) if agent_plans else 0.0
        elif strategy == OrchestrationStrategy.SEQUENTIAL:
            return sum(plan.timeout_seconds for plan in agent_plans)
        else:
            return sum(plan.timeout_seconds for plan in agent_plans) * 0.7  # Optimistic estimate
    
    def _estimate_execution_cost(self, agent_plans: List[AgentExecutionPlan]) -> float:
        """Estimate execution cost (simplified)"""
        return len(agent_plans) * 0.1  # Simplified cost model
    
    def _estimate_quality_score(self, agent_plans: List[AgentExecutionPlan]) -> float:
        """Estimate expected quality score"""
        if not agent_plans:
            return 0.0
        
        weights = [plan.weight for plan in agent_plans]
        return statistics.mean(weights) * 0.8  # Optimistic quality estimate
    
    async def _update_performance_metrics(self, result: OrchestrationResult):
        """Update system performance metrics"""
        self.performance_metrics.total_requests += 1
        
        if result.success:
            self.performance_metrics.successful_requests += 1
        else:
            self.performance_metrics.failed_requests += 1
        
        # Update average response time
        current_avg = self.performance_metrics.average_response_time
        total_requests = self.performance_metrics.total_requests
        new_avg = ((current_avg * (total_requests - 1)) + result.total_processing_time) / total_requests
        self.performance_metrics.average_response_time = new_avg
        
        # Update confidence and quality
        self.performance_metrics.average_confidence_score = (
            (self.performance_metrics.average_confidence_score * (total_requests - 1) + result.confidence_score) 
            / total_requests
        )
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                await self._collect_metrics()
                await self._analyze_performance()
                await self._generate_optimizations()
                await asyncio.sleep(self.config.metrics_collection_interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _collect_metrics(self):
        """Collect current system metrics"""
        self.performance_metrics.timestamp = datetime.utcnow()
        
        # Update agent utilization (simplified)
        for agent_id, agent in self.agents.items():
            if agent.is_active:
                self.performance_metrics.agent_utilization[agent_id] = 0.5  # Placeholder
    
    async def _analyze_performance(self):
        """Analyze current system performance"""
        # Analyze recent request patterns
        recent_requests = [r for r in self.request_history 
                          if r.completed_at > datetime.utcnow() - timedelta(hours=1)]
        
        if recent_requests:
            # Calculate success rate trends
            success_rate = len([r for r in recent_requests if r.success]) / len(recent_requests)
            
            # Update strategy performance tracking
            for request in recent_requests:
                strategy = request.strategy_used.value
                self.strategy_performance[strategy]["success_rate"].append(1.0 if request.success else 0.0)
                self.strategy_performance[strategy]["response_time"].append(request.total_processing_time)
                self.strategy_performance[strategy]["quality_score"].append(request.quality_score)
    
    async def _generate_optimizations(self):
        """Generate optimization recommendations"""
        # This would analyze patterns and suggest improvements
        # For now, simplified implementation
        pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "orchestrator_status": "active" if self.is_monitoring else "inactive",
            "performance_metrics": self.performance_metrics.model_dump(),
            "active_requests": len(self.active_requests),
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.is_active]),
            "request_history_size": len(self.request_history),
            "config": self.config.model_dump()
        }
    
    def get_optimization_recommendations(self, request_type: str) -> List[OptimizationRecommendation]:
        """Get optimization recommendations for a request type"""
        # Simplified implementation - would analyze historical data
        recommendations = []
        
        if request_type in self.strategy_performance:
            performance_data = self.strategy_performance[request_type]
            
            # Analyze which strategy performs best
            best_strategy = OrchestrationStrategy.PARALLEL  # Default
            best_score = 0.0
            
            for strategy, metrics in performance_data.items():
                if "quality_score" in metrics and metrics["quality_score"]:
                    avg_quality = statistics.mean(metrics["quality_score"])
                    if avg_quality > best_score:
                        best_score = avg_quality
                        best_strategy = OrchestrationStrategy(strategy)
            
            if best_score > 0:
                recommendations.append(OptimizationRecommendation(
                    request_type=request_type,
                    current_performance={"quality_score": best_score},
                    suggested_strategy=best_strategy,
                    suggested_agent_selection=[],
                    estimated_improvement={"quality_score": 0.1},
                    implementation_effort="low",
                    risk_level="low",
                    reasoning=f"Strategy {best_strategy.value} shows best historical performance"
                ))
        
        return recommendations