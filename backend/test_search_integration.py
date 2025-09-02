#!/usr/bin/env python3
"""
Test script to verify search functionality integration
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1/travel"
TEST_USER_ID = "test_user_search"

def test_search_endpoint():
    """Test the dedicated search endpoint"""
    print("🔍 Testing dedicated search endpoint...")
    
    payload = {
        "user_id": TEST_USER_ID,
        "source": "pettah",
        "destination": "piliyandala",
        "mode": "transit"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/search-route-info", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search endpoint working!")
            print(f"Request ID: {result.get('request_id')}")
            print(f"Total searches: {result.get('summary', {}).get('total_searches')}")
            print(f"Successful searches: {result.get('summary', {}).get('successful_searches')}")
            print(f"Failed searches: {result.get('summary', {}).get('failed_searches')}")
            
            # Show search categories
            categories = result.get('summary', {}).get('search_categories', [])
            print(f"Search categories: {', '.join(categories)}")
            
            # Show sample search results
            search_results = result.get('search_results', {})
            for category, data in list(search_results.items())[:2]:  # Show first 2
                print(f"\n📋 {category.upper()}:")
                if 'result' in data:
                    print(f"  Query: {data.get('query', 'N/A')}")
                    print(f"  Status: {data.get('result', {}).get('status', 'N/A')}")
                else:
                    print(f"  Error: {data.get('error', 'N/A')}")
            
            return True
        else:
            print(f"❌ Search endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during search test: {str(e)}")
        return False

def test_plan_route_with_search():
    """Test the main plan-route endpoint to see if search results are included"""
    print("\n🚗 Testing plan-route endpoint with search integration...")
    
    payload = {
        "user_id": TEST_USER_ID,
        "source": "pettah",
        "destination": "piliyandala",
        "mode": "transit"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/plan-route", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Plan route endpoint working!")
            
            # Check if search results are included
            response_data = result.get('response', {})
            
            # Check for search results in the main response
            if 'search_results' in response_data:
                print("✅ Search results found in main response!")
                search_summary = response_data['search_results'].get('summary', {})
                print(f"  Total searches: {search_summary.get('total_searches')}")
                print(f"  Successful searches: {search_summary.get('successful_searches')}")
            else:
                print("⚠️  No search_results section found in main response")
            
            # Check for local insights (backward compatibility)
            if 'local_insights' in response_data:
                print("✅ Local insights found (backward compatibility)")
            
            # Check metadata for search information
            metadata = response_data.get('metadata', {})
            if metadata.get('has_search_results'):
                print("✅ Search results indicated in metadata")
            else:
                print("⚠️  Search results not indicated in metadata")
            
            return True
        else:
            print(f"❌ Plan route endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during plan route test: {str(e)}")
        return False

def test_search_functionality():
    """Test the basic search functionality"""
    print("\n🧪 Testing basic search functionality...")
    
    try:
        response = requests.post(f"{BASE_URL}/test-search")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search functionality test working!")
            print(f"Test queries: {len(result.get('test_queries', []))}")
            
            # Show test results
            test_results = result.get('results', {})
            for query, data in test_results.items():
                print(f"\n📝 Query: {query[:50]}...")
                print(f"  Status: {data.get('status', 'N/A')}")
                if data.get('status') == 'success':
                    print(f"  Data available: {'Yes' if data.get('result') else 'No'}")
                else:
                    print(f"  Error: {data.get('error', 'N/A')}")
            
            return True
        else:
            print(f"❌ Search functionality test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during search functionality test: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Search Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Search Endpoint", test_search_endpoint),
        ("Plan Route with Search", test_plan_route_with_search),
        ("Search Functionality", test_search_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Search integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
