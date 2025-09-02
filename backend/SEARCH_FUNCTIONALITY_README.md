# Search Functionality Integration

This document explains how the search functionality has been integrated into the travel agent system using the Serper API.

## Overview

The system now includes comprehensive web search capabilities that provide real-time information about routes, including:
- Transportation information and local tips
- Points of interest and landmarks
- Current traffic conditions and roadworks
- Weather conditions
- Local events and activities
- Public transport schedules

## How It Works

### 1. Automatic Search Integration

When you call the `/plan-route` endpoint, the system automatically:
1. Processes your route request
2. Executes multiple web searches for relevant information
3. Integrates search results into the route recommendations
4. Provides comprehensive context for your journey

### 2. Search Results Structure

The search results are organized into several categories:

```json
{
  "search_results": {
    "summary": {
      "total_searches": 6,
      "successful_searches": 5,
      "failed_searches": 1,
      "search_categories": ["route_info", "poi_info", "traffic_info", "weather_info", "events_info", "transit_info"]
    },
    "local_insights": {
      "route_info": { /* Route and transportation information */ },
      "traffic_info": { /* Current traffic conditions */ },
      "weather_info": { /* Weather information */ },
      "events_info": { /* Local events and activities */ },
      "transit_info": { /* Public transport information */ }
    },
    "points_of_interest": [ /* Attractions and landmarks */ ],
    "route_context": [ /* Additional contextual information */ ]
  }
}
```

### 3. New Endpoints

#### `/search-route-info` - Dedicated Search Endpoint
Use this endpoint to get comprehensive search results for any route:

```bash
curl -X POST http://localhost:8000/api/v1/travel/search-route-info \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "source": "pettah",
    "destination": "piliyandala",
    "mode": "transit"
  }'
```

#### `/test-search` - Test Search Functionality
Use this endpoint to verify that the search functionality is working:

```bash
curl -X POST http://localhost:8000/api/v1/travel/test-search
```

## Configuration

### Environment Variables

Make sure you have the following environment variable set:

```bash
SERPER_API_KEY=your_serper_api_key_here
```

### Serper API Setup

1. Sign up at [serper.dev](https://serper.dev)
2. Get your API key
3. Set the environment variable
4. The system will automatically use it for all searches

## Search Categories

### 1. Route Information (`route_info`)
- General transportation information
- Local tips and recommendations
- Route-specific advice

### 2. Points of Interest (`poi_info`)
- Attractions and landmarks
- Tourist destinations
- Cultural sites

### 3. Traffic Information (`traffic_info`)
- Current traffic conditions
- Roadworks and construction
- Traffic alerts

### 4. Weather Information (`weather_info`)
- Current weather conditions
- Weather forecasts
- Travel advisories

### 5. Events Information (`events_info`)
- Local festivals and events
- Cultural activities
- Seasonal attractions

### 6. Transit Information (`transit_info`)
- Public transport schedules
- Bus and train information
- Station details

## Example Response

Here's what you'll see in your route planning response:

```json
{
  "request_id": "req_1234567890",
  "status": "success",
  "response": {
    "query": {
      "source": "pettah",
      "destination": "piliyandala",
      "mode": "transit",
      "user_id": "user_123"
    },
    "recommended_routes": [ /* Your route options */ ],
    "search_results": {
      "summary": {
        "total_searches": 6,
        "successful_searches": 5,
        "failed_searches": 1
      },
      "local_insights": {
        "route_info": {
          "summary": "Pettah to Piliyandala is a popular route with multiple transport options...",
          "key_points": [
            "Bus routes available from Pettah Bus Stand",
            "Train service from Fort Railway Station",
            "Approximate travel time: 1-1.5 hours"
          ]
        },
        "traffic_info": {
          "summary": "Current traffic conditions are moderate...",
          "key_points": [
            "Heavy traffic expected during peak hours",
            "Roadworks on Galle Road near Dehiwala"
          ]
        }
      }
    },
    "metadata": {
      "has_search_results": true,
      "search_summary": { /* Search statistics */ }
    }
  }
}
```

## Testing

Run the test script to verify everything is working:

```bash
cd backend
python test_search_integration.py
```

This will test:
1. The dedicated search endpoint
2. Search integration in the main plan-route endpoint
3. Basic search functionality

## Troubleshooting

### Common Issues

1. **No search results appearing**
   - Check if `SERPER_API_KEY` is set
   - Verify the Serper API is working with `/test-search`
   - Check server logs for errors

2. **Search results incomplete**
   - Some searches may fail due to API limits or network issues
   - Check the `search_summary` for success/failure counts
   - Failed searches will show error details

3. **Slow response times**
   - Multiple searches are executed sequentially
   - Consider implementing parallel search execution for better performance
   - Monitor Serper API usage and limits

### Debug Information

The system provides detailed debug information:
- Search queries executed
- Success/failure counts
- Error messages for failed searches
- Timestamps for all operations

## Performance Considerations

- **Search Execution**: 6 different search queries are executed
- **Response Time**: Each search adds ~1-3 seconds to total response time
- **API Limits**: Monitor your Serper API usage
- **Caching**: Consider implementing result caching for frequently searched routes

## Future Enhancements

Potential improvements:
1. **Parallel Search Execution**: Run searches concurrently
2. **Result Caching**: Cache search results for repeated queries
3. **Smart Query Optimization**: Dynamically adjust search queries based on route type
4. **Local Knowledge Database**: Store and retrieve frequently accessed information
5. **Search Result Ranking**: Prioritize most relevant search results

## Support

If you encounter issues:
1. Check the server logs for detailed error messages
2. Use the `/test-search` endpoint to verify API connectivity
3. Verify your Serper API key and usage limits
4. Check the test script output for specific failure points
