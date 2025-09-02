#!/usr/bin/env python3
"""
Test script for the LLM Summarizer Service
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def test_llm_summarizer():
    """Test the LLM summarizer service"""
    
    print("🧪 Testing LLM Summarizer Service")
    print("=" * 50)
    
    # Check if GOOGLE_API_KEY is set
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please check your .env file")
        return False
    
    print(f"✅ GOOGLE_API_KEY found: {api_key[:10]}...")
    
    try:
        # Import and test the service
        from app.services.llm_summarizer import LLMSummarizerService
        
        print("\n🔄 Initializing LLM Summarizer Service...")
        summarizer = LLMSummarizerService()
        print("✅ Service initialized successfully")
        
        # Test with sample search results
        print("\n📝 Testing search result summarization...")
        
        test_search_results = {
            "general_info": {
                "summary": "Multiple transportation options available from Colombo to Kandy",
                "key_points": [
                    "Express buses take 3-4 hours and cost 200-300 LKR",
                    "Regular buses take 5-6 hours and cost 150-200 LKR", 
                    "Trains available but limited schedule",
                    "Private taxis cost 8000-12000 LKR",
                    "Shared vans cost 400-600 LKR per person"
                ],
                "relevant_links": [
                    "https://example.com/bus-routes",
                    "https://example.com/train-schedule",
                    "https://example.com/taxi-services"
                ]
            },
            "raw_results": "Additional search data about local conditions, weather, and attractions"
        }
        
        # Test basic summarization
        summary_result = summarizer.summarize_search_results(
            test_search_results,
            "How do I get from Colombo to Kandy?",
            "User is in Colombo and needs to reach Kandy by evening, prefers affordable options"
        )
        
        if summary_result["status"] == "success":
            print("✅ Summarization successful!")
            print(f"📊 Model used: {summary_result['model_used']}")
            print(f"📝 Summary ({len(summary_result['summary'].split(chr(10)))} lines):")
            print("-" * 40)
            print(summary_result["summary"])
            print("-" * 40)
        else:
            print(f"❌ Summarization failed: {summary_result.get('error', 'Unknown error')}")
            return False
        
        # Test destination insights
        print("\n🎯 Testing destination insights...")
        
        test_preferences = {
            "preferred_transit_modes": ["bus", "train"],
            "budget_preference": "medium",
            "max_walking_distance": 1.0
        }
        
        test_context = {
            "summary": "Traveling to Kandy from Colombo"
        }
        
        insights = summarizer.generate_route_recommendation(
            [],  # Empty routes list for destination focus
            test_preferences,
            test_context
        )
        
        print("✅ Destination insights generated!")
        print(f"📝 Insights ({len(insights.split(chr(10)))} lines):")
        print("-" * 40)
        print(insights)
        print("-" * 40)
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_langchain_tool():
    """Test the LangChain tool wrapper"""
    
    print("\n🔧 Testing LangChain Tool Wrapper")
    print("=" * 50)
    
    try:
        from app.services.llm_summarizer import LLMSummarizerTool
        
        print("🔄 Initializing LLM Summarizer Tool...")
        tool = LLMSummarizerTool()
        
        if tool.summarizer:
            print("✅ Tool initialized successfully")
            
            # Test the tool
            test_results = {
                "general_info": {
                    "summary": "Local bus service information",
                    "key_points": ["Buses run every 15 minutes", "Fare is 50 LKR", "Route covers main areas"],
                    "relevant_links": ["https://example.com/bus-info"]
                }
            }
            
            result = tool._run(
                test_results,
                "What are the local bus options?",
                "User needs to get around the city"
            )
            
            if result["status"] == "success":
                print("✅ Tool execution successful!")
                print(f"📝 Summary: {result['summary'][:100]}...")
            else:
                print(f"❌ Tool execution failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print("❌ Tool initialization failed - no summarizer available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing tool wrapper: {str(e)}")
        return False
    
    return True

def main():
    """Main test function"""
    
    print("🚀 LLM Summarizer Service Test Suite")
    print("=" * 60)
    
    # Test basic service
    if not test_llm_summarizer():
        print("\n❌ Basic service test failed")
        return
    
    # Test LangChain tool
    if not test_langchain_tool():
        print("\n❌ LangChain tool test failed")
        return
    
    print("\n🎉 All tests completed successfully!")
    print("\nThe LLM Summarizer Service is ready to use in your workflow!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
