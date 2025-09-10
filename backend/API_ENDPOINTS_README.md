# Travel Agent Workflow API Endpoints

This document describes the new API endpoints that enable real-world interaction with the multi-agent travel system.

## Base URL
```
http://localhost:8000/api/v1
```

## Available Endpoints

### 1. Plan Travel Route
**POST** `/travel/plan-route`

Triggers the complete agentic workflow to plan a travel route.

**Request Body:**
```json
{
  "user_id": "string",
  "source": "string",
  "destination": "string", 
  "mode": "string",
  "preferred_transit": "string (optional)",
  "departure_time": "datetime (optional)"
}
```

**Response:**
```json
{
  "request_id": "string",
  "status": "string",
  "response": "object",
  "processing_time": "number",
  "agents_used": ["string"],
  "trace_id": "string (optional)"
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:8000/api/v1/travel/plan-route \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "source": "Times Square, New York",
    "destination": "Brooklyn Bridge, New York",
    "mode": "transit",
    "preferred_transit": "subway"
  }'
```

### 2. Update User Preferences
**POST** `/travel/update-user-preferences`

Updates user preferences based on route selection to improve future recommendations.

**Request Body:**
```json
{
  "user_id": "string",
  "route_id": "string",
  "source": "string",
  "destination": "string",
  "mode": "string",
  "selected_route_data": "object"
}
```

**Response:**
```json
{
  "user_id": "string",
  "status": "string",
  "message": "string",
  "updated_preferences": "object",
  "timestamp": "datetime"
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:8000/api/v1/travel/update-user-preferences \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "route_id": "route_456",
    "source": "Times Square, New York",
    "destination": "Brooklyn Bridge, New York",
    "mode": "transit",
    "selected_route_data": {
      "summary": {
        "duration_minutes": 25,
        "estimated_fare": 2.75
      }
    }
  }'
```

### 3. Search Route Information
**POST** `/travel/search-route-info`

Performs comprehensive web searches for route information using the Serper API.

**Request Body:**
```json
{
  "user_id": "string",
  "source": "string",
  "destination": "string",
  "mode": "string",
  "preferred_transit": "string (optional)",
  "departure_time": "datetime (optional)"
}
```

**Response:**
```json
{
  "status": "string",
  "message": "string",
  "request_id": "string",
  "query": "object",
  "search_results": "object",
  "summary": "object",
  "timestamp": "string"
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:8000/api/v1/travel/search-route-info \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "source": "Colombo",
    "destination": "Kandy",
    "mode": "transit"
  }'
```

### 4. Test Search Functionality
**POST** `/travel/test-search`

Tests the search functionality to ensure Serper API is working correctly.

**Response:**
```json
{
  "status": "string",
  "message": "string",
  "test_queries": ["string"],
  "results": "object",
  "timestamp": "string"
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:8000/api/v1/travel/test-search
```

### 5. Report Disruption
**POST** `/travel/report-disruption`

Reports a disruption in a selected route and provides alternative routes.

**Request Body:**
```json
{
  "user_id": "string",
  "route_id": "string",
  "location": "string",
  "disruption_type": "string",
  "severity": "string",
  "description": "string",
  "affected_routes": ["string"]
}
```

**Response:**
```json
{
  "disruption_id": "string",
  "status": "string",
  "message": "string",
  "alternative_routes": ["object"],
  "timestamp": "datetime"
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:8000/api/v1/travel/report-disruption \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "route_id": "route_456",
    "location": "34th Street Station",
    "disruption_type": "construction",
    "severity": "medium",
    "description": "Platform maintenance causing delays",
    "affected_routes": ["route_456", "route_789"]
  }'
```

### 6. Get User Preferences
**GET** `/travel/user-preferences/{user_id}`

Retrieves current user preferences and route history.

**Response:**
```json
{
  "user_id": "string",
  "preferences": "object",
  "route_history": ["object"],
  "last_updated": "datetime",
  "route_selection_count": "number"
}
```

**Example Usage:**
```bash
curl http://localhost:8000/api/v1/travel/user-preferences/user_123
```

### 7. Get Active Disruptions
**GET** `/travel/active-disruptions`

Retrieves all currently active disruptions.

**Response:**
```json
{
  "active_disruptions_count": "number",
  "disruptions": [
    {
      "disruption_id": "string",
      "location": "string",
      "type": "string",
      "severity": "string",
      "description": "string",
      "reported_at": "datetime",
      "affected_routes": ["string"]
    }
  ]
}
```

**Example Usage:**
```bash
curl http://localhost:8000/api/v1/travel/active-disruptions
```

## Workflow Integration

These endpoints integrate with the multi-agent travel system:

1. **Route Planning**: Uses the complete agentic workflow including:
   - Input processing
   - Mode routing
   - Route generation
   - User preference analysis
   - Local knowledge integration
   - Disruption monitoring
   - Route optimization

2. **User Learning**: The system learns from user choices to improve future recommendations

3. **Disruption Handling**: Real-time disruption reporting and alternative route generation

## Database Collections

The endpoints use the following MongoDB collections:

- `travel_requests`: Stores route planning requests and results
- `user_preferences`: Stores user preferences and route history
- `disruptions`: Stores reported disruptions
- `error_logs`: Stores error information for debugging

## Error Handling

All endpoints include comprehensive error handling:

- Input validation using Pydantic models
- Database operation error handling
- Graceful fallbacks for failed operations
- Detailed error logging for debugging

## Testing

Use the provided test script to verify endpoint functionality:

```bash
cd backend
source .venv/bin/activate
python test_api_endpoints.py
```

## Swagger Documentation

Access the interactive API documentation at:
```
http://localhost:8000/docs
```

The travel endpoints are grouped under the "Travel Agent Workflow" tag for easy navigation.

## Environment Variables

Ensure the following environment variables are set in your `.env` file:

- `GOOGLE_MAPS_API_KEY`: For route generation
- `MONGODB_CONNECTION_STRING`: For database operations
- `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`: For tracing (optional)

## Running the Server

Start the server using:

```bash
cd backend
source .venv/bin/activate
python run.py
```

The server will be available at `http://localhost:8000` with the API endpoints accessible at `/api/v1/travel/*`.
