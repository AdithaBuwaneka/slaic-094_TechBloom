import google.generativeai as genai
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from langchain.tools import BaseTool

# Load environment variables
load_dotenv()

class LLMSummarizerService:
    """
    Service for using Google's Generative AI to summarize search results
    into user-friendly, concise outputs (4-5 lines)
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        # Configure Google Generative AI
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("Google Generative AI model initialized successfully")
        except Exception as e:
            print(f" Error initializing Google Generative AI: {str(e)}")
            raise
    
    def summarize_search_results(self, search_results: Dict[str, Any], 
                               user_query: str, 
                               context: Optional[str] = None) -> Dict[str, Any]:
        """
        Summarize search results into a user-friendly, concise format
        
        Args:
            search_results: Dictionary containing search results
            user_query: The original user query
            context: Optional additional context (e.g., user location, preferences)
        
        Returns:
            Dictionary with summarized information
        """
        try:
            # Extract key information from search results
            extracted_info = self._extract_key_information(search_results)
            
            # Create a prompt for the LLM
            prompt = self._create_summarization_prompt(
                extracted_info, user_query, context
            )
            
            # Generate summary using Google Generative AI
            response = self.model.generate_content(prompt)
            
            # Process the response
            summary = self._process_llm_response(response)
            
            return {
                "status": "success",
                "summary": summary,
                "original_query": user_query,
                "timestamp": datetime.now().isoformat(),
                "model_used": "gemini-1.5-flash"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_key_information(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key information from search results for summarization"""
        extracted = {
            "general_info": "",
            "key_points": [],
            "relevant_links": [],
            "raw_data": {}
        }
        
        # Extract general info
        if "general_info" in search_results:
            general_info = search_results["general_info"]
            if isinstance(general_info, dict):
                extracted["general_info"] = general_info.get("summary", "")
                extracted["key_points"] = general_info.get("key_points", [])
                extracted["relevant_links"] = general_info.get("relevant_links", [])
            else:
                extracted["general_info"] = str(general_info)
        
        # Extract raw results if available
        if "raw_results" in search_results:
            extracted["raw_data"] = search_results["raw_results"]
        
        return extracted
    
    def _create_summarization_prompt(self, extracted_info: Dict[str, Any], 
                                    user_query: str, 
                                    context: Optional[str] = None) -> str:
        """Create a prompt for the LLM to generate a concise summary"""
        
        prompt = f"""
You are a helpful local knowledge assistant. Your task is to provide destination insights and local knowledge in exactly 4-5 lines.

USER QUERY: {user_query}

SEARCH RESULTS:
- General Info: {extracted_info['general_info']}
- Key Points: {', '.join(extracted_info['key_points'][:5])}
- Relevant Links: {', '.join(extracted_info['relevant_links'][:3])}

CONTEXT: {context or 'No additional context provided'}

INSTRUCTIONS:
1. Focus on DESTINATION INSIGHTS and LOCAL KNOWLEDGE, not route planning
2. Provide information about the destination area, attractions, local tips, weather, events, etc.
3. Give practical insights that would help someone visiting or staying in the destination
4. Use simple, clear language
5. Provide exactly 4-5 lines of destination-focused information
6. If the information is insufficient, mention what additional details might be helpful

FORMAT YOUR RESPONSE AS DESTINATION INSIGHTS IN 4-5 LINES:
"""
        return prompt
    
    def _process_llm_response(self, response) -> str:
        """Process the LLM response and extract the summary"""
        try:
            # Extract text from the response
            if hasattr(response, 'text'):
                summary = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                summary = response.candidates[0].content.parts[0].text.strip()
            else:
                summary = str(response)
            
            # Clean up the summary
            summary = self._clean_summary(summary)
            
            return summary
            
        except Exception as e:
            print(f"Error processing LLM response: {str(e)}")
            return "Unable to generate summary due to processing error."
    
    def _clean_summary(self, summary: str) -> str:
        """Clean and format the summary"""
        # Remove any markdown formatting
        summary = summary.replace('**', '').replace('*', '').replace('`', '')
        
        # Split into lines and clean each line
        lines = summary.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Remove markdown headers
                cleaned_lines.append(line)
        
        # Ensure we have 4-5 lines
        if len(cleaned_lines) < 4:
            # If too few lines, split longer lines
            while len(cleaned_lines) < 4 and any(len(line) > 100 for line in cleaned_lines):
                new_lines = []
                for line in cleaned_lines:
                    if len(line) > 100:
                        # Split long lines at sentence boundaries
                        sentences = line.split('. ')
                        new_lines.extend(sentences)
                    else:
                        new_lines.append(line)
                cleaned_lines = new_lines
        
        # Limit to 5 lines maximum
        cleaned_lines = cleaned_lines[:5]
        
        return '\n'.join(cleaned_lines)
    
    def generate_route_recommendation(self, routes: List[Dict], 
                                    user_preferences: Dict, 
                                    search_context: Dict) -> str:
        """
        Generate destination insights and local tips using LLM
        
        Args:
            routes: List of available routes
            user_preferences: User's travel preferences
            search_context: Context from search results
        
        Returns:
            Destination insights summary
        """
        try:
            # Create a prompt for destination insights
            prompt = f"""
You are a helpful local travel guide. Generate destination insights and local tips in exactly 4-5 lines.

DESTINATION CONTEXT: {search_context.get('summary', 'No additional context')}

USER PREFERENCES:
- Preferred modes: {getattr(user_preferences, 'preferred_transit_modes', ['any'])}
- Budget preference: {getattr(user_preferences, 'budget_preference', 'medium')}
- Max walking distance: {getattr(user_preferences, 'max_walking_distance', 1.0)} km

INSTRUCTIONS:
1. Focus on DESTINATION INSIGHTS, not route planning
2. Provide local knowledge about the destination area
3. Include practical tips for visitors
4. Mention attractions, local culture, or useful information
5. Use encouraging, helpful language

FORMAT YOUR RESPONSE AS DESTINATION INSIGHTS IN 4-5 LINES:
"""
            
            # Generate destination insights
            response = self.model.generate_content(prompt)
            insights = self._process_llm_response(response)
            
            return insights
            
        except Exception as e:
            return f"Unable to generate destination insights: {str(e)}"


class LLMSummarizerTool(BaseTool):
    """
    LangChain tool wrapper for the LLM summarizer service
    """
    
    name: str = "llm_summarizer"
    description: str = "Summarize search results using Google Generative AI into user-friendly, concise format"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self._summarizer = LLMSummarizerService()
        except Exception as e:
            print(f"Warning: LLM Summarizer tool initialization failed: {str(e)}")
            self._summarizer = None
    
    @property
    def summarizer(self):
        """Property to access the summarizer service"""
        return self._summarizer
    
    def _run(self, search_results: Dict[str, Any], 
             user_query: str, 
             context: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the LLM summarizer tool
        
        Args:
            search_results: Search results to summarize
            user_query: Original user query
            context: Optional additional context
        
        Returns:
            Summarized results
        """
        if not self._summarizer:
            return {
                "status": "error",
                "error": "LLM Summarizer service not available",
                "timestamp": datetime.now().isoformat()
            }
        
        return self._summarizer.summarize_search_results(
            search_results, user_query, context
        )


# Example usage and testing
if __name__ == "__main__":
    # Test the service
    try:
        summarizer = LLMSummarizerService()
        print(" LLM Summarizer Service initialized successfully")
        
        # Test with sample data
        test_results = {
            "general_info": {
                "summary": "Multiple bus routes available from Colombo to Kandy",
                "key_points": ["Express buses take 3-4 hours", "Regular buses take 5-6 hours", "Fares range from 200-400 LKR"],
                "relevant_links": ["https://example.com/bus-routes", "https://example.com/fares"]
            },
            "raw_results": "Sample raw search results"
        }
        
        summary = summarizer.summarize_search_results(
            test_results, 
            "How do I get from Colombo to Kandy by bus?",
            "User is in Colombo and needs to reach Kandy by evening"
        )
        
        print("\n Generated Summary:")
        print(summary.get("summary", "No summary generated"))
        
    except Exception as e:
        print(f" Error testing LLM Summarizer: {str(e)}")
