# LLM Summarizer Service

This service integrates Google's Generative AI (Gemini) to provide user-friendly, summarized outputs from search results in 4-5 lines.

## Features

- **Destination Insights**: Converts complex search results into destination-focused insights in 4-5 lines
- **Local Knowledge Synthesis**: Generates practical local tips and destination information
- **LangChain Integration**: Available as a LangChain tool for workflow integration
- **Error Handling**: Graceful fallbacks when LLM service is unavailable

## Configuration

### Environment Variables

Ensure your `.env` file contains:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### Dependencies

The service requires the following packages (already in `requirements.txt`):

```bash
google-generativeai>=0.4.1
langchain>=0.3.27
python-dotenv>=1.0.0
```

## Usage

### 1. Basic Service Usage

```python
from app.services.llm_summarizer import LLMSummarizerService

# Initialize the service
summarizer = LLMSummarizerService()

# Summarize search results
summary_result = summarizer.summarize_search_results(
    search_results=your_search_data,
    user_query="How do I get from A to B?",
    context="User needs practical travel information"
)

if summary_result["status"] == "success":
    print(summary_result["summary"])
```

### 2. Route Recommendations

```python
# Generate personalized route recommendations
recommendation = summarizer.generate_route_recommendation(
    routes=available_routes,
    user_preferences=user_prefs,
    search_context=search_context
)

print(recommendation)
```

### 3. LangChain Tool Integration

```python
from app.services.llm_summarizer import LLMSummarizerTool

# Use as a LangChain tool
tool = LLMSummarizerTool()
result = tool._run(
    search_results=search_data,
    user_query="travel query",
    context="additional context"
)
```

## Integration in Workflow

The LLM summarizer is automatically integrated into the travel agent workflow:

1. **Local Knowledge Agent**: Gathers search results from multiple sources
2. **Response Compilation**: Uses LLM to generate user-friendly summaries
3. **Personalized Recommendations**: Creates tailored route suggestions

### Workflow Integration Points

- **Search Results Summary**: Converts raw search data into 4-5 line summaries
- **Route Recommendations**: Provides personalized travel advice
- **Error Handling**: Graceful fallbacks when LLM is unavailable

## API Endpoints

### Test LLM Summarizer

```bash
POST /api/v1/test-llm-summarizer
```

Tests the LLM summarizer service with sample data.

### Plan Travel Route (Enhanced)

```bash
POST /api/v1/plan-route
```

Now includes only the LLM-generated destination summary in the response:

```json
{
  "destination_summary": "LLM-generated 4-5 line destination insights",
  "recommended_routes": [...],
  "query": {...}
}
```

## Testing

### Run Test Script

```bash
cd backend
python test_llm_summarizer.py
```

### Test via API

```bash
curl -X POST "http://localhost:8000/api/v1/test-llm-summarizer"
```

## Example Output

### Destination Insights (4-5 lines)

```
Kandy is a beautiful hill city known for its cultural heritage and scenic views.
The city is home to the Temple of the Sacred Tooth Relic, a UNESCO World Heritage site.
Visit during the Esala Perahera festival (July/August) for traditional dance performances.
The climate is cooler than Colombo, perfect for exploring the Royal Botanical Gardens.
Local markets offer traditional crafts, spices, and the famous Kandy tea.
```

### Local Knowledge Summary

```
Piliyandala offers a mix of urban convenience and suburban charm near Colombo.
The area has good connectivity with frequent bus services to the city center.
Local attractions include the Piliyandala Clock Tower and nearby Bolgoda Lake.
The area is known for its residential neighborhoods and proximity to major highways.
Weather is typically warm and humid, with afternoon rain showers common.
```

## Error Handling

The service includes comprehensive error handling:

- **API Key Missing**: Clear error message if `GOOGLE_API_KEY` is not set
- **Service Unavailable**: Graceful fallbacks when LLM service fails
- **Rate Limiting**: Handles API rate limits gracefully
- **Network Issues**: Retry logic for transient failures

## Performance Considerations

- **Response Time**: LLM calls typically take 2-5 seconds
- **Caching**: Consider implementing response caching for repeated queries
- **Batch Processing**: Process multiple summaries in parallel when possible

## Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY not set"**
   - Check your `.env` file
   - Ensure the key is valid and has Generative AI access

2. **"LLM Summarizer Service initialization failed"**
   - Verify API key permissions
   - Check network connectivity
   - Ensure Google Generative AI is enabled

3. **"Summarization failed"**
   - Check API quotas and rate limits
   - Verify input data format
   - Review error logs for specific issues

### Debug Mode

Enable debug logging by setting:

```bash
LOG_LEVEL=DEBUG
```

## Future Enhancements

- **Response Caching**: Cache common summaries to reduce API calls
- **Multiple Models**: Support for different LLM providers
- **Custom Prompts**: User-configurable summarization styles
- **Batch Processing**: Process multiple summaries simultaneously
- **Quality Metrics**: Track and improve summary quality over time

## Support

For issues or questions:

1. Check the test script output
2. Review API endpoint responses
3. Check application logs
4. Verify environment configuration

## License

This service is part of the Transit Companion Backend project.
