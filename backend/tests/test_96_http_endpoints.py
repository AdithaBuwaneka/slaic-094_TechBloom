#!/usr/bin/env python3
"""
Test 96 HTTP Endpoints Only
Fast test for all HTTP endpoints without WebSocket connections
"""
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any
from datetime import datetime, timezone

class HTTPEndpointsTest:
    def __init__(self, base_url: str = "http://localhost:8011"):
        self.base_url = base_url
        self.jwt_token = None
        self.refresh_token = None
        self.results = []
        self.request_timeout = 5  # Fast timeout
        
    async def test_96_http_endpoints(self) -> Dict[str, Any]:
        """Test 96 HTTP endpoints (excluding WebSocket connections)"""
        print("Testing 96 HTTP API Endpoints")
        print("=" * 50)
        print("HTTP Endpoint Breakdown:")
        print("  Base: 3, Agent: 2, Data: 2, Route: 3, Personalization: 3")
        print("  Fare: 4, Accessibility: 6, Language: 1, Disruption: 9")
        print("  Local Knowledge: 10, Orchestration: 9, WebSocket REST: 8")
        print("  User: 11, Journey: 13, External: 12")
        print("  Total: 96 HTTP endpoints")
        print(f"  Request timeout: {self.request_timeout}s")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Get JWT token for authenticated endpoints
            await self.get_auth_token(session)
            
            # Step 2: Test all HTTP endpoints by category
            endpoints_tested = 0
            
            # Base endpoints (3)
            endpoints_tested += await self.test_base_endpoints(session)
            
            # Agent endpoints (2)
            endpoints_tested += await self.test_agent_endpoints(session)
            
            # Data endpoints (2)
            endpoints_tested += await self.test_data_endpoints(session)
            
            # Route endpoints (3)
            endpoints_tested += await self.test_route_endpoints(session)
            
            # Personalization endpoints (3)
            endpoints_tested += await self.test_personalization_endpoints(session)
            
            # Fare endpoints (4)
            endpoints_tested += await self.test_fare_endpoints(session)
            
            # Accessibility endpoints (6)
            endpoints_tested += await self.test_accessibility_endpoints(session)
            
            # Language endpoints (1)
            endpoints_tested += await self.test_language_endpoints(session)
            
            # Disruption endpoints (9)
            endpoints_tested += await self.test_disruption_endpoints(session)
            
            # Local Knowledge endpoints (10)
            endpoints_tested += await self.test_local_knowledge_endpoints(session)
            
            # Orchestration endpoints (9)
            endpoints_tested += await self.test_orchestration_endpoints(session)
            
            # WebSocket REST endpoints (8)
            endpoints_tested += await self.test_websocket_rest_endpoints(session)
            
            # User endpoints (11)
            endpoints_tested += await self.test_user_endpoints(session)
            
            # Journey Planning endpoints (13)
            endpoints_tested += await self.test_journey_endpoints(session)
            
            # External API endpoints (12)
            endpoints_tested += await self.test_external_endpoints(session)
            
            # Final summary
            successful_endpoints = sum(1 for r in self.results if r["success"])
            print(f"\n{'='*50}")
            print(f"96 HTTP ENDPOINTS TEST RESULTS:")
            print(f"Total HTTP endpoints tested: {len(self.results)}")
            print(f"Expected HTTP endpoints: 96")
            print(f"Successful endpoints: {successful_endpoints}/{len(self.results)}")
            print(f"Success rate: {successful_endpoints/len(self.results)*100:.1f}%")
            print(f"{'='*50}")
            
            return {
                "total_endpoints_tested": len(self.results),
                "expected_endpoints": 96,
                "success_rate": successful_endpoints / len(self.results) * 100 if self.results else 0,
                "successful_endpoints": successful_endpoints,
                "results": self.results,
                "test_completed": datetime.now(timezone.utc).isoformat(),
                "test_type": "HTTP_ONLY"
            }

    async def get_auth_token(self, session):
        """Get JWT token for authenticated endpoints"""
        try:
            login_data = {"username_or_email": "testuser@example.com", "password": "password123"}
            result = await self.make_request(session, "POST", "/api/v1/users/login", json_data=login_data)
            
            if result and result.get("success", False) and "data" in result:
                api_response = result["data"]
                if isinstance(api_response, dict) and "data" in api_response:
                    inner_data = api_response["data"]
                    if "tokens" in inner_data and "access_token" in inner_data["tokens"]:
                        self.jwt_token = inner_data["tokens"]["access_token"]
                        self.refresh_token = inner_data["tokens"]["refresh_token"]
                print(f"SUCCESS: Authentication token obtained")
            else:
                print("WARNING: Could not obtain auth token, some tests may fail")
                
        except Exception as e:
            print(f"WARNING: Authentication setup failed: {e}")

    async def make_request(self, session, method: str, endpoint: str, json_data=None, params=None):
        """Make HTTP request and record results with timeout"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.jwt_token and endpoint not in ["/api/v1/users/register", "/api/v1/users/login"]:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
            
        start_time = time.time()
        
        try:
            kwargs = {"headers": headers, "timeout": aiohttp.ClientTimeout(total=self.request_timeout)}
            if json_data:
                kwargs["json"] = json_data
            if params:
                kwargs["params"] = params
                
            async with session.request(method, url, **kwargs) as response:
                response_time = (time.time() - start_time) * 1000
                success = response.status < 400
                
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status,
                    "success": success,
                    "response_time_ms": round(response_time, 2),
                    "data": data if success else str(data)[:200]
                }
                
                self.results.append(result)
                status_icon = "PASS" if success else "FAIL"
                print(f"{status_icon} {method} {endpoint} - {response.status} ({response_time:.0f}ms)")
                
                return result
                
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": 408,
                "success": False,
                "response_time_ms": round(response_time, 2),
                "error": f"Request timeout after {self.request_timeout}s"
            }
            self.results.append(result)
            print(f"TIMEOUT {method} {endpoint} - {self.request_timeout}s timeout")
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "success": False,
                "response_time_ms": round(response_time, 2),
                "error": str(e)
            }
            self.results.append(result)
            print(f"FAIL {method} {endpoint} - ERROR: {str(e)[:50]}")
            return result

    # Copy all the endpoint test methods from the original file
    async def test_base_endpoints(self, session) -> int:
        """Test base endpoints (3)"""
        print("\n--- Base Endpoints (3) ---")
        await self.make_request(session, "GET", "/api/v1/")
        await self.make_request(session, "GET", "/api/v1/health")
        await self.make_request(session, "GET", "/api/v1/db-connection")
        return 3

    async def test_agent_endpoints(self, session) -> int:
        """Test agent endpoints (2)"""
        print("\n--- Agent Endpoints (2) ---")
        await self.make_request(session, "GET", "/api/v1/agents/status")
        await self.make_request(session, "POST", "/api/v1/agents/test", json_data={"test_message": "hello"})
        return 2

    async def test_data_endpoints(self, session) -> int:
        """Test data endpoints (2)"""
        print("\n--- Data Endpoints (2) ---")
        await self.make_request(session, "POST", "/api/v1/data/transport", json_data={"location": "Colombo"})
        await self.make_request(session, "POST", "/api/v1/data/validate-sources", json_data={"sources": ["SLTB"]})
        return 2

    async def test_route_endpoints(self, session) -> int:
        """Test route endpoints (3)"""
        print("\n--- Route Endpoints (3) ---")
        route_data = {
            "origin": {"latitude": 6.9271, "longitude": 79.8612, "name": "Colombo"},
            "destination": {"latitude": 7.2906, "longitude": 80.6337, "name": "Kandy"}
        }
        await self.make_request(session, "POST", "/api/v1/route/optimize", json_data=route_data)
        await self.make_request(session, "POST", "/api/v1/route/alternatives", json_data=route_data)
        await self.make_request(session, "POST", "/api/v1/route/feasibility", json_data=route_data)
        return 3

    async def test_personalization_endpoints(self, session) -> int:
        """Test personalization endpoints (3)"""
        print("\n--- Personalization Endpoints (3) ---")
        profile_data = {"user_id": "test_user", "preferences": {"transport_mode": "bus"}}
        await self.make_request(session, "POST", "/api/v1/personalization/create-profile", json_data=profile_data)
        await self.make_request(session, "POST", "/api/v1/personalization/get-preferences", json_data={"user_id": "test_user"})
        await self.make_request(session, "POST", "/api/v1/personalization/generate-recommendations", json_data={"user_id": "test_user"})
        return 3

    async def test_fare_endpoints(self, session) -> int:
        """Test fare endpoints (4)"""
        print("\n--- Fare Endpoints (4) ---")
        fare_data = {
            "origin": {"latitude": 6.9271, "longitude": 79.8612, "name": "Colombo"},
            "destination": {"latitude": 7.2906, "longitude": 80.6337, "name": "Kandy"}
        }
        await self.make_request(session, "POST", "/api/v1/fare/calculate", json_data=fare_data)
        await self.make_request(session, "POST", "/api/v1/fare/optimize", json_data=fare_data)
        await self.make_request(session, "POST", "/api/v1/fare/discounts", json_data=fare_data)
        await self.make_request(session, "POST", "/api/v1/fare/season-passes", json_data={"user_id": "test_user"})
        return 4

    async def test_accessibility_endpoints(self, session) -> int:
        """Test accessibility endpoints (6)"""
        print("\n--- Accessibility Endpoints (6) ---")
        profile_data = {"user_id": "test_user", "accessibility_needs": ["wheelchair"]}
        await self.make_request(session, "POST", "/api/v1/accessibility/profile", json_data=profile_data)
        await self.make_request(session, "POST", "/api/v1/accessibility/info", json_data={"operator": "SLTB"})
        await self.make_request(session, "POST", "/api/v1/accessibility/assess", json_data={"route_id": "test_route"})
        await self.make_request(session, "POST", "/api/v1/accessibility/alerts", json_data={"transport_mode": "bus"})
        await self.make_request(session, "POST", "/api/v1/accessibility/emergency-info", json_data={"transport_mode": "bus"})
        await self.make_request(session, "POST", "/api/v1/accessibility/feedback", json_data={"accessibility_rating": 4})
        return 6

    async def test_language_endpoints(self, session) -> int:
        """Test language endpoints (1)"""
        print("\n--- Language Endpoints (1) ---")
        translate_data = {"text": "Hello", "from_language": "english", "to_language": "sinhala"}
        await self.make_request(session, "POST", "/api/v1/language/translate", json_data=translate_data)
        return 1

    async def test_disruption_endpoints(self, session) -> int:
        """Test disruption endpoints (9)"""
        print("\n--- Disruption Endpoints (9) ---")
        disruption_data = {"title": "Test Disruption", "transport_mode": "bus"}
        await self.make_request(session, "POST", "/api/v1/disruption/create", json_data=disruption_data)
        update_data = {"disruption_id": "test_id", "status": "resolved"}
        await self.make_request(session, "PUT", "/api/v1/disruption/update", json_data=update_data)
        await self.make_request(session, "POST", "/api/v1/disruption/query", json_data={"transport_mode": "bus"})
        await self.make_request(session, "POST", "/api/v1/disruption/impact/test_id", json_data={"route_id": "test_route"})
        await self.make_request(session, "POST", "/api/v1/disruption/contingency-plans", json_data={"disruption_id": "test_id"})
        await self.make_request(session, "POST", "/api/v1/disruption/monitor-route", json_data={"route_id": "test_route"})
        await self.make_request(session, "POST", "/api/v1/disruption/resolve/test_id", json_data={"resolution": "fixed"})
        await self.make_request(session, "GET", "/api/v1/disruption/active")
        await self.make_request(session, "GET", "/api/v1/disruption/test")
        return 9

    async def test_local_knowledge_endpoints(self, session) -> int:
        """Test local knowledge endpoints (10)"""
        print("\n--- Local Knowledge Endpoints (10) ---")
        query_data = {"query": "restaurants near Colombo Fort", "location": "Colombo"}
        await self.make_request(session, "POST", "/api/v1/local-knowledge/query", json_data=query_data)
        create_data = {"title": "New Place", "description": "A nice place", "location": "Colombo"}
        await self.make_request(session, "POST", "/api/v1/local-knowledge/create", json_data=create_data)
        update_data = {"entry_id": "test_id", "title": "Updated Place"}
        await self.make_request(session, "PUT", "/api/v1/local-knowledge/update", json_data=update_data)
        culture_data = {"location": "Colombo", "interests": ["history", "food"]}
        await self.make_request(session, "POST", "/api/v1/local-knowledge/cultural-insights", json_data=culture_data)
        tourist_data = {"destination": "Kandy", "interests": ["temples", "nature"]}
        await self.make_request(session, "POST", "/api/v1/local-knowledge/tourist-guidance", json_data=tourist_data)
        safety_data = {"location": "Colombo", "time_of_day": "night"}
        await self.make_request(session, "POST", "/api/v1/local-knowledge/safety-info", json_data=safety_data)
        event_data = {"location": "Colombo", "date": "2024-12-25"}
        await self.make_request(session, "POST", "/api/v1/local-knowledge/events", json_data=event_data)
        rec_data = {"user_preferences": ["food", "culture"], "location": "Colombo"}
        await self.make_request(session, "POST", "/api/v1/local-knowledge/recommendations", json_data=rec_data)
        await self.make_request(session, "GET", "/api/v1/local-knowledge/test")
        await self.make_request(session, "GET", "/api/v1/local-knowledge/attractions/Colombo")
        return 10

    async def test_orchestration_endpoints(self, session) -> int:
        """Test orchestration endpoints (9)"""
        print("\n--- Orchestration Endpoints (9) ---")
        exec_data = {"task": "route_planning", "origin": "Colombo", "destination": "Kandy"}
        await self.make_request(session, "POST", "/api/v1/orchestration/execute", json_data=exec_data)
        complex_data = {"waypoints": ["Colombo", "Kandy", "Galle"], "optimize": True}
        await self.make_request(session, "POST", "/api/v1/orchestration/complex-route-planning", json_data=complex_data)
        await self.make_request(session, "GET", "/api/v1/orchestration/system-status")
        await self.make_request(session, "GET", "/api/v1/orchestration/performance-metrics")
        await self.make_request(session, "GET", "/api/v1/orchestration/optimization-recommendations/journey")
        strategy_data = {"strategies": ["fastest", "cheapest"], "route": "Colombo-Kandy"}
        await self.make_request(session, "POST", "/api/v1/orchestration/strategy-comparison", json_data=strategy_data)
        await self.make_request(session, "POST", "/api/v1/orchestration/agent-collaboration-test", json_data={"agents": ["route", "fare"]})
        await self.make_request(session, "POST", "/api/v1/orchestration/update-config", json_data={"config": {"timeout": 30}})
        await self.make_request(session, "GET", "/api/v1/orchestration/test")
        return 9

    async def test_websocket_rest_endpoints(self, session) -> int:
        """Test WebSocket REST endpoints (8) only"""
        print("\n--- WebSocket REST Endpoints (8) ---")
        await self.make_request(session, "GET", "/api/v1/websocket/connections/status")
        notification_data = {
            "notification_type": "schedule_update",
            "title": "Test Notification",
            "message": "Test message",
            "priority": "normal",
            "target_users": ["all"]
        }
        await self.make_request(session, "POST", "/api/v1/websocket/broadcast-notification", json_data=notification_data)
        await self.make_request(session, "POST", "/api/v1/websocket/trigger-test-update/schedule", json_data={"data": "test"})
        await self.make_request(session, "POST", "/api/v1/websocket/streaming/start", json_data={"type": "schedules"})
        await self.make_request(session, "POST", "/api/v1/websocket/streaming/stop", json_data={"type": "schedules"})
        await self.make_request(session, "POST", "/api/v1/websocket/streaming/configure", json_data={"interval": 30})
        await self.make_request(session, "GET", "/api/v1/websocket/subscriptions/types")
        await self.make_request(session, "GET", "/api/v1/websocket/demo-client")
        return 8

    async def test_user_endpoints(self, session) -> int:
        """Test user endpoints (11)"""
        print("\n--- User Endpoints (11) ---")
        register_data = {"username": "testuser2", "email": "testuser2@example.com", "password": "password123", "full_name": "Test User 2"}
        await self.make_request(session, "POST", "/api/v1/users/register", json_data=register_data)
        
        await self.make_request(session, "POST", "/api/v1/users/verify-email", params={"verification_token": "test_token"})
        await self.make_request(session, "GET", "/api/v1/users/profile")
        await self.make_request(session, "PUT", "/api/v1/users/profile", json_data={"first_name": "Updated"})
        await self.make_request(session, "GET", "/api/v1/users/preferences")
        await self.make_request(session, "PUT", "/api/v1/users/preferences", json_data={"theme": "dark"})
        await self.make_request(session, "GET", "/api/v1/users/stats")
        refresh_data = {"refresh_token": self.refresh_token} if self.refresh_token else {"refresh_token": "test_token"}
        await self.make_request(session, "POST", "/api/v1/users/refresh-token", json_data=refresh_data)
        await self.make_request(session, "POST", "/api/v1/users/logout")
        await self.make_request(session, "GET", "/api/v1/users/test-auth")
        return 11

    async def test_journey_endpoints(self, session) -> int:
        """Test journey planning endpoints (13)"""
        print("\n--- Journey Planning Endpoints (13) ---")
        journey_data = {
            "origin": {"latitude": 6.9271, "longitude": 79.8612, "name": "Colombo"},
            "destination": {"latitude": 7.2906, "longitude": 80.6337, "name": "Kandy"}
        }
        await self.make_request(session, "POST", "/api/v1/journey/plan", json_data=journey_data)
        
        multi_stop_data = {
            "origin": {"latitude": 6.9271, "longitude": 79.8612, "name": "Colombo"},
            "destination": {"latitude": 7.2906, "longitude": 80.6337, "name": "Kandy"},
            "waypoints": [{"latitude": 7.0, "longitude": 80.0, "name": "Waypoint"}]
        }
        await self.make_request(session, "POST", "/api/v1/journey/plan-multi-stop", json_data=multi_stop_data)
        
        book_data = {"journey_id": "test_journey", "user_id": "test_user"}
        await self.make_request(session, "POST", "/api/v1/journey/book", json_data=book_data)
        await self.make_request(session, "GET", "/api/v1/journey/trip/test_trip_id")
        await self.make_request(session, "POST", "/api/v1/journey/trip/test_trip_id/start", json_data={})
        location_data = {"latitude": 6.95, "longitude": 79.85}
        await self.make_request(session, "POST", "/api/v1/journey/trip/test_trip_id/update-location", json_data=location_data)
        await self.make_request(session, "POST", "/api/v1/journey/trip/test_trip_id/complete", json_data={})
        await self.make_request(session, "POST", "/api/v1/journey/trip/test_trip_id/cancel", json_data={"reason": "user_cancelled"})
        search_data = {"query": "bus to Kandy", "origin": "Colombo"}
        await self.make_request(session, "POST", "/api/v1/journey/search", json_data=search_data)
        await self.make_request(session, "GET", "/api/v1/journey/analytics")
        await self.make_request(session, "GET", "/api/v1/journey/quick-routes", params={"origin_lat": "6.9271", "origin_lng": "79.8612", "destination_lat": "7.2906", "destination_lng": "80.6337"})
        await self.make_request(session, "GET", "/api/v1/journey/popular-routes")
        await self.make_request(session, "GET", "/api/v1/journey/service-status")
        return 13

    async def test_external_endpoints(self, session) -> int:
        """Test external API endpoints (12)"""
        print("\n--- External API Endpoints (12) ---")
        await self.make_request(session, "GET", "/api/v1/external/status")
        await self.make_request(session, "GET", "/api/v1/external/health-check")
        await self.make_request(session, "GET", "/api/v1/external/weather", params={"latitude": "6.9271", "longitude": "79.8612"})
        await self.make_request(session, "GET", "/api/v1/external/traffic", params={"origin_lat": "6.9271", "origin_lng": "79.8612", "dest_lat": "7.2906", "dest_lng": "80.6337"})
        await self.make_request(session, "GET", "/api/v1/external/schedules/railway", params={"origin": "Colombo", "destination": "Kandy"})
        await self.make_request(session, "GET", "/api/v1/external/schedules/bus", params={"route_number": "1"})
        await self.make_request(session, "GET", "/api/v1/external/real-time/vehicles", params={"route_id": "test_route"})
        await self.make_request(session, "GET", "/api/v1/external/usage-statistics")
        await self.make_request(session, "GET", "/api/v1/external/configurations")
        await self.make_request(session, "POST", "/api/v1/external/test-connection", json_data={"service": "weather"})
        await self.make_request(session, "GET", "/api/v1/external/data-freshness")
        await self.make_request(session, "GET", "/api/v1/external/coverage-areas")
        return 12

    def print_summary(self, results: Dict[str, Any]):
        """Print test summary"""
        print(f"\nHTTP ENDPOINTS TEST SUMMARY:")
        print(f"Total endpoints: {results['total_endpoints_tested']}")
        print(f"Successful: {results['successful_endpoints']}")
        print(f"Failed: {results['total_endpoints_tested'] - results['successful_endpoints']}")
        print(f"Success rate: {results['success_rate']:.1f}%")

async def main():
    tester = HTTPEndpointsTest()
    
    print("Starting 96 HTTP endpoints test...")
    start_time = time.time()
    
    results = await tester.test_96_http_endpoints()
    tester.print_summary(results)
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total test time: {total_time:.1f} seconds")
    
    # Save results
    with open("96_http_endpoints_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: 96_http_endpoints_test_results.json")

if __name__ == "__main__":
    print("96 HTTP Endpoints Test")
    print("Testing all HTTP endpoints excluding WebSocket connections")
    asyncio.run(main())