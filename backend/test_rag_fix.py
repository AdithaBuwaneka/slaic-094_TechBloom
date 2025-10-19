#!/usr/bin/env python3
"""
Quick test script to verify RAG system is working correctly
Run this after starting the backend: python test_rag_fix.py
"""

import requests
import json
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://localhost:8000/api/v1"

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.YELLOW}ℹ️  {text}{Style.RESET_ALL}")

def test_health_check():
    """Test if RAG system is initialized"""
    print_header("1. Testing RAG System Health")
    
    try:
        response = requests.get(f"{BASE_URL}/chatbot/health")
        data = response.json()
        
        if data.get("rag_system_initialized"):
            print_success("RAG system is initialized")
            print_info(f"Vector DB exists: {data.get('vector_db_exists')}")
            print_info(f"Vector DB path: {data.get('vector_db_path')}")
        else:
            print_error("RAG system NOT initialized!")
            return False
            
        return True
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False

def test_intent_detection():
    """Test if intent detection is working correctly"""
    print_header("2. Testing Intent Detection")
    
    test_cases = [
        ("What is Smart Transit Companion?", "general_info", "Should use RAG"),
        ("How do buses work?", "general_info", "Should use RAG"),
        ("Plan a route from Colombo to Kandy", "route_planning", "Should NOT use RAG"),
        ("Tell me about AI agents", "general_info", "Should use RAG"),
    ]
    
    try:
        response = requests.get(f"{BASE_URL}/chatbot/test-rag")
        data = response.json()
        
        print_info(f"Summary: {data.get('summary')}")
        
        for result in data.get('test_results', []):
            question = result.get('question')
            intent = result.get('intent')
            should_use_rag = result.get('should_use_rag')
            status = result.get('status')
            
            if should_use_rag:
                print_success(f"'{question}' → {intent} → {status}")
            else:
                print_info(f"'{question}' → {intent} → {status}")
        
        return True
    except Exception as e:
        print_error(f"Intent detection test failed: {str(e)}")
        return False

def test_rag_retrieval():
    """Test RAG retrieval with a sample question"""
    print_header("3. Testing RAG Document Retrieval")
    
    question = "What is Smart Transit Companion?"
    
    try:
        response = requests.post(
            f"{BASE_URL}/chatbot/debug-rag",
            params={"question": question}
        )
        data = response.json()
        
        if data.get('status') == 'success':
            print_success(f"RAG retrieval successful for: '{question}'")
            print_info(f"Intent detected: {data.get('intent_detection', {}).get('intent_type')}")
            print_info(f"Documents retrieved: {data.get('documents_retrieved')}")
            
            docs = data.get('documents', [])
            for i, doc in enumerate(docs[:2]):
                print(f"\n{Fore.MAGENTA}Document {i+1}:{Style.RESET_ALL}")
                print(f"{doc.get('content')}...")
            
            print(f"\n{Fore.MAGENTA}Answer:{Style.RESET_ALL}")
            print(f"{data.get('qa_result')}")
            
            return True
        else:
            print_error(f"RAG retrieval failed: {data.get('message')}")
            return False
            
    except Exception as e:
        print_error(f"RAG retrieval test failed: {str(e)}")
        return False

def test_actual_chatbot():
    """Test the actual chatbot endpoint"""
    print_header("4. Testing Actual Chatbot Endpoint")
    
    test_questions = [
        "What features does the app have?",
        "How do I use the app?",
    ]
    
    for question in test_questions:
        try:
            response = requests.post(
                f"{BASE_URL}/chatbot/ask",
                json={
                    "question": question,
                    "temperature": 0.7
                }
            )
            data = response.json()
            
            rag_used = data.get('action_data', {}).get('rag_used', False)
            docs_retrieved = data.get('action_data', {}).get('documents_retrieved', 0)
            
            print(f"\n{Fore.BLUE}Q: {question}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}A: {data.get('answer')[:200]}...{Style.RESET_ALL}")
            
            if rag_used:
                print_success(f"RAG was used! Retrieved {docs_retrieved} documents")
            else:
                print_error("RAG was NOT used!")
            
        except Exception as e:
            print_error(f"Chatbot test failed: {str(e)}")
            return False
    
    return True

def main():
    print(f"\n{Fore.MAGENTA}{'*'*60}")
    print(f"{Fore.MAGENTA}    RAG System Fix Verification Test")
    print(f"{Fore.MAGENTA}{'*'*60}{Style.RESET_ALL}\n")
    
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health_check()))
    results.append(("Intent Detection", test_intent_detection()))
    results.append(("RAG Retrieval", test_rag_retrieval()))
    results.append(("Chatbot Endpoint", test_actual_chatbot()))
    
    # Print summary
    print_header("Test Summary")
    
    for test_name, passed in results:
        if passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n{Fore.CYAN}Overall: {total_passed}/{total_tests} tests passed{Style.RESET_ALL}\n")
    
    if total_passed == total_tests:
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}🎉 All tests passed! RAG system is working correctly!")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.RED}{'='*60}")
        print(f"{Fore.RED}⚠️  Some tests failed. Check the output above for details.")
        print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
