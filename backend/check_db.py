import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_db():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['transit_companion']
    
    try:
        # Check travel requests collection
        requests = await db.travel_requests.find().limit(3).to_list(length=3)
        
        print('=== TRAVEL REQUESTS IN DATABASE ===')
        for i, req in enumerate(requests):
            print(f'Request {i+1}:')
            print(f'  Source: {req.get("source")}')
            print(f'  Destination: {req.get("destination")}')
            
            result = req.get('result', {})
            response = result.get('response', {})
            best_route = response.get('best_route', {})
            
            print(f'  Distance: {best_route.get("distance_text")}')
            print(f'  Duration: {best_route.get("duration_text")}')
            print(f'  Cost: {best_route.get("estimated_cost")}')
            print('---')
            
        if not requests:
            print('No travel requests found in database')
    
    except Exception as e:
        print(f'Database error: {e}')
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_db())