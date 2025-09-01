# Multiagentic Transit Route Planning System

This document describes the implementation of a multiagentic system using LangChain and LangGraph for intelligent transit route planning.

## System Overview

The multiagentic system consists of multiple specialized agents that work together to provide comprehensive route planning:

1. **Route Planning Agent** - Finds optimal routes using Google Maps API
2. **Fare Analysis Agent** - Analyzes costs and provides fare information
3. **User Preference Agent** - Matches routes to user preferences
4. **Local Knowledge Agent** - Gathers local insights and safety information
5. **Disruption Monitoring Agent** - Monitors and handles transit disruptions

## Architecture

### Core Components

- **LangChain**: Framework for building LLM-powered applications
- **LangGraph**: Orchestration framework for multi-agent workflows
- **MongoDB**: Database for storing transit data, user preferences, and disruptions
- **Google Maps API**: Primary route planning service
- **Groq LLM**: Language model for agent reasoning

### System Flow

```
User Request → Route Planning Agent → Fare Analysis Agent → 
Preference Matching Agent → Local Knowledge Agent → 
Disruption Check Agent → Final Response Assembly
```

## Installation and Setup

### Prerequisites

- Python 3.8+
- MongoDB database
- Google Maps API key
- Groq API key

### Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file with:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=transit_companion_db
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GROQ_API_KEY=your_groq_api_key
```

## Data Seeding

### Seed Complete Data

Run the comprehensive seeding script:

```bash
cd backend/scripts
python seed_complete_data.py
```

This will create:
- Transit routes (bus and train)
- Fare information
- Last mile connectivity options
- User preferences
- Sample disruptions

### Collections Created

- `transit_routes` - Available transit routes
- `transit_fares` - Fare information for routes
- `last_mile_options` - Last mile connectivity options
- `user_preferences` - User preference data
- `transit_disruptions` - Active transit disruptions

## API Endpoints

### Enhanced Route Planning

#### POST `/api/v1/enhanced/enhanced-route`

Get enhanced route with supplementary options and multiagent analysis.

**Parameters:**
- `origin`: Starting location
- `destination`: End location
- `mode`: Travel mode (driving, transit, walking, bicycling, three_wheeler, uber)
- `transit_preference`: Preferred transit mode (bus or train) when mode is transit
- `user_id`: User ID for personalized recommendations
- `include_supplementary`: Whether to include supplementary route options

**Response:**
```json
{
  "success": true,
  "primary_route": {...},
  "supplementary_routes": [...],
  "multiagent_analysis": {...},
  "fares": [...],
  "last_mile_options": [...]
}
```

#### POST `/api/v1/enhanced/route-with-preferences`

Get route optimized for user preferences.

**Parameters:**
- `origin`: Starting location
- `destination`: End location
- `mode`: Travel mode
- `user_id`: User ID for preferences
- `preferences`: User preference dictionary

### Data Management

#### GET `/api/v1/enhanced/transit-routes`
Get available transit routes from database.

#### GET `/api/v1/enhanced/route-fares`
Get fare information for routes.

#### GET `/api/v1/enhanced/last-mile-options`
Get last mile connectivity options.

#### GET `/api/v1/enhanced/user-preferences/{user_id}`
Get user preferences.

#### POST `/api/v1/enhanced/user-preferences/{user_id}`
Update user preferences.

#### GET `/api/v1/enhanced/disruptions`
Get active transit disruptions.

#### POST `/api/v1/enhanced/disruptions`
Report a new transit disruption.

## Usage Examples

### Basic Enhanced Route Planning

```python
from app.services.enhanced_route_service import EnhancedRouteService

service = EnhancedRouteService()

# Get enhanced route
result = await service.get_enhanced_route(
    origin="Colombo Fort",
    destination="Maharagama",
    mode="transit",
    transit_preference="bus",
    user_id="user123"
)
```

### Route with User Preferences

```python
# Define user preferences
preferences = {
    "cost": {"max_fare": 500, "prefer_cheaper": True},
    "time": {"max_duration": 120, "prefer_faster": True},
    "safety": {"avoid_night_travel": True}
}

# Get optimized route
result = await service.get_route_with_preferences(
    origin="Colombo Fort",
    destination="Maharagama",
    mode="transit",
    user_id="user123",
    preferences=preferences
)
```

### Multiagent System Usage

```python
from app.services.multiagent_system import TransitMultiAgentSystem

system = TransitMultiAgentSystem()
await system.initialize_agents()

# Plan route using multiagent system
result = await system.plan_route(
    origin="Colombo Fort",
    destination="Maharagama",
    mode="transit"
)
```

## Agent Capabilities

### Route Planning Agent

- Integrates with Google Maps API
- Finds optimal routes for different travel modes
- Provides alternative route suggestions
- Handles transit preferences (bus vs train)

### Fare Analysis Agent

- Retrieves fare information from database
- Calculates total route costs
- Provides cost breakdowns
- Identifies cost-effective alternatives

### User Preference Agent

- Retrieves user preferences from database
- Scores routes based on user preferences
- Updates preferences dynamically
- Provides personalized recommendations

### Local Knowledge Agent

- Gathers local insights about routes
- Provides safety information
- Offers cultural and practical tips
- Integrates with web search APIs (planned)

### Disruption Monitoring Agent

- Monitors active disruptions
- Suggests alternative routes
- Provides real-time updates
- Handles disruption reporting

## Configuration

### MongoDB Collections

The system expects the following collections:

- `transit_routes`: Route information
- `transit_fares`: Fare data
- `last_mile_options`: Last mile connectivity
- `user_preferences`: User preference data
- `transit_disruptions`: Disruption information

### LLM Configuration

The system uses Groq's Llama3-70B model by default. You can modify the model in `multiagent_system.py`:

```python
self.llm = ChatGroq(
    groq_api_key=settings.GROQ_API_KEY,
    model_name="llama3-70b-8192"  # Change model here
)
```

## Error Handling

The system includes comprehensive error handling:

- Fallback to basic route planning if multiagent system fails
- Graceful degradation when specific agents are unavailable
- Detailed error messages for debugging
- Automatic retry mechanisms for transient failures

## Performance Considerations

- Database queries are optimized with indexes
- LLM calls are cached where possible
- Asynchronous processing for concurrent operations
- Rate limiting for external API calls

## Security

- API key management through environment variables
- Input validation and sanitization
- Database access controls
- Rate limiting for public endpoints

## Future Enhancements

### Planned Features

1. **Web Search Integration**: Integrate with Serper API for real-time local knowledge
2. **Advanced ML Scoring**: Implement machine learning-based route scoring
3. **Real-time Updates**: WebSocket support for live disruption updates
4. **Multi-language Support**: Support for Sinhala and Tamil
5. **Predictive Analytics**: Predict disruptions and optimize routes proactively

### Scalability Improvements

1. **Redis Caching**: Implement Redis for caching frequent queries
2. **Load Balancing**: Distribute agent workloads across multiple instances
3. **Database Sharding**: Shard data by geographic regions
4. **Microservices**: Split into separate microservices for each agent type

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check MongoDB service status
   - Verify connection string in .env file
   - Check network connectivity

2. **LLM API Errors**
   - Verify Groq API key
   - Check API rate limits
   - Ensure model availability

3. **Google Maps API Errors**
   - Verify API key validity
   - Check API quotas
   - Ensure billing is enabled

### Debug Mode

Enable debug mode in `config.py`:

```python
DEBUG: bool = True
```

This will provide detailed logging for troubleshooting.

## Contributing

### Development Setup

1. Clone the repository
2. Install dependencies
3. Set up environment variables
4. Run data seeding script
5. Start the development server

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Include docstrings for all functions
- Write unit tests for new features

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the troubleshooting section
