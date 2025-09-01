# Langfuse Integration Guide for Multi-Agent Travel System

This guide explains how to set up and use Langfuse for tracing and monitoring your AI agents in the multi-agent travel system.

## What is Langfuse?

Langfuse is an open-source LLM engineering platform that provides:
- **Tracing**: Monitor the execution flow of your AI agents
- **Observability**: Visualize agent interactions and decision-making
- **Evaluation**: Score and assess agent performance
- **Debugging**: Identify bottlenecks and issues in agent workflows

## Setup Instructions

### 1. Get Langfuse API Keys

1. Go to [Langfuse Cloud](https://cloud.langfuse.com) or set up a self-hosted instance
2. Create a new project
3. Navigate to Project Settings → API Keys
4. Copy your **Public Key** and **Secret Key**

### 2. Configure Environment Variables

Add these variables to your `.env` file:

```bash
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=your_public_key_here
LANGFUSE_SECRET_KEY=your_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com  # Optional: defaults to cloud
```

### 3. Install Dependencies

The required packages are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## How It Works

### Automatic Tracing

Once configured, Langfuse will automatically trace:

- **Workflow Execution**: Each travel request creates a trace
- **Agent Nodes**: Individual agent operations are tracked
- **LLM Calls**: All language model interactions are logged
- **Tool Usage**: External API calls (Google Maps, Serper) are monitored
- **Performance Metrics**: Processing times and resource usage

### Trace Structure

Each travel request creates a trace with:

```
travel-agent-request (Root Trace)
├── input_processing
├── mode_router
├── standard_route (or transit_route_aggregation)
│   ├── fare_calculation
│   ├── user_preference_analysis
│   └── local_knowledge_agent
├── route_optimization
├── disruption_monitoring
└── response_compilation
```

### What You'll See in Langfuse

1. **Traces Dashboard**: Overview of all travel requests
2. **Agent Graphs**: Visual representation of agent workflows
3. **Performance Metrics**: Response times and success rates
4. **Error Tracking**: Failed requests and their causes
5. **User Analytics**: Usage patterns and preferences

## Usage Examples

### Basic Request with Tracing

```python
from app.services.workflow import run_travel_agent

# This automatically creates a trace
result = run_travel_agent(
    source="New York",
    destination="Los Angeles",
    mode="transit",
    user_id="user_123"
)

# Access the trace ID
trace_id = result.get('trace_id')
print(f"View trace: https://cloud.langfuse.com/traces/{trace_id}")
```

### Adding Custom Scores

```python
from app.services.langfuse_service import langfuse_service

# Score a trace based on user feedback
langfuse_service.score_trace(
    trace_id="trace_123",
    name="user_satisfaction",
    value=4.5,
    comment="User rated route quality as 4.5/5"
)
```

### Custom Spans for Specific Operations

```python
from app.services.langfuse_service import langfuse_service

# Create a custom span for a specific operation
with langfuse_service.start_span("custom_operation") as span:
    # Your custom logic here
    result = perform_custom_operation()
    
    # Update span with results
    span.update(output={"result": result})
```

## Monitoring and Debugging

### Key Metrics to Watch

1. **Success Rate**: Percentage of successful travel requests
2. **Response Time**: Average processing time per request
3. **Agent Performance**: Which agents are most/least effective
4. **Error Patterns**: Common failure points and their causes
5. **User Satisfaction**: Scores and feedback ratings

### Debugging Workflows

1. **Trace Inspection**: Follow the execution path step-by-step
2. **Input/Output Analysis**: See what each agent received and produced
3. **Performance Profiling**: Identify slow agents or bottlenecks
4. **Error Context**: Understand why specific requests failed

### Agent Graph Visualization

Langfuse provides a visual representation of your agent workflows:

- **Node View**: See each agent as a node in the graph
- **Edge Analysis**: Understand how agents communicate
- **Execution Flow**: Follow the path of successful vs. failed requests
- **Performance Heatmap**: Identify slow or problematic agents

## Best Practices

### 1. Meaningful Trace Names

```python
# Good: Descriptive and searchable
trace = langfuse_service.create_trace(
    name="transit-route-optimization",
    user_id=user_id
)

# Avoid: Generic names
trace = langfuse_service.create_trace(
    name="request",  # Too generic
    user_id=user_id
)
```

### 2. Rich Metadata

```python
trace = langfuse_service.create_trace(
    name="travel-request",
    user_id=user_id,
    metadata={
        "source": source,
        "destination": destination,
        "mode": mode,
        "user_preferences": user_preferences,
        "request_timestamp": datetime.now().isoformat(),
        "environment": "production"
    }
)
```

### 3. Consistent Scoring

```python
# Use consistent score names across your application
langfuse_service.score_trace(trace_id, "route_quality", 4.5)
langfuse_service.score_trace(trace_id, "user_satisfaction", 4.0)
langfuse_service.score_trace(trace_id, "response_time", 2.1)
```

### 4. Error Handling

```python
try:
    result = workflow.invoke(state)
    trace.update(output={"status": "success", "result": result})
except Exception as e:
    trace.update(output={"status": "error", "error": str(e)})
    # Consider scoring the error
    langfuse_service.score_trace(trace_id, "error_severity", 1.0)
```

## Troubleshooting

### Common Issues

1. **"Langfuse not configured"**
   - Check your environment variables
   - Ensure API keys are correct
   - Verify network connectivity to Langfuse

2. **"Failed to create trace"**
   - Check API key permissions
   - Verify project configuration
   - Check Langfuse service status

3. **Missing traces in dashboard**
   - Ensure `langfuse_service.flush()` is called
   - Check for network issues
   - Verify trace creation was successful

### Debug Mode

Enable debug logging by setting:

```bash
LANGFUSE_DEBUG=true
```

This will show detailed information about trace creation and API calls.

## Advanced Features

### 1. Custom Evaluations

```python
# Create custom evaluation metrics
langfuse_service.score_trace(
    trace_id=trace_id,
    name="route_efficiency",
    value=calculate_efficiency_score(route),
    comment="Based on distance, time, and cost optimization"
)
```

### 2. Batch Operations

```python
# Process multiple requests and score them together
for request in batch_requests:
    result = run_travel_agent(**request)
    # Each gets its own trace automatically
```

### 3. Integration with Monitoring Tools

Langfuse can integrate with:
- **Grafana**: Custom dashboards
- **Datadog**: APM integration
- **Slack**: Error notifications
- **Email**: Performance reports

## Support and Resources

- **Documentation**: [docs.langfuse.com](https://docs.langfuse.com)
- **GitHub**: [github.com/langfuse/langfuse](https://github.com/langfuse/langfuse)
- **Discord**: [discord.gg/langfuse](https://discord.gg/langfuse)
- **Cookbook**: [LangGraph Integration Guide](https://langfuse.com/docs/guides/cookbook/integration_langgraph)

## Next Steps

1. **Set up your API keys** and test basic tracing
2. **Explore the dashboard** to understand your agent performance
3. **Add custom scoring** for business-specific metrics
4. **Set up alerts** for performance issues
5. **Create custom dashboards** for your team

Happy tracing! 🚀
