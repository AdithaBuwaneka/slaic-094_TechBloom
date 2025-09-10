# scripts/seed_database.py

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Use environment variables for consistency ---
MONGO_DETAILS = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DATABASE_NAME", "transit_companion_db")
COLLECTION_NAME = "bus_routes"

# --- Here is our mock data ---
mock_bus_routes = [
    {
        "route_number": "138",
        "origin": "Pettah",
        "destination": "Maharagama",
        "stops": ["Fort", "Maradana", "Borella", "Narahenpita", "Nugegoda"],
        "operator": "SLTB",
    },
    {
        "route_number": "177",
        "origin": "Kollupitiya",
        "destination": "Kaduwela",
        "stops": ["Bambalapitiya", "Thummulla", "Rajagiriya", "Battaramulla", "Malabe"],
        "operator": "Private",
    },
    {
        "route_number": "120",
        "origin": "Pettah",
        "destination": "Piliyandala",
        "stops": ["Fort", "Slave Island", "Wellawatte", "Dehiwala", "Kohuwala", "Nugegoda", "Delkanda"],
        "operator": "SLTB",
    }
]

async def seed_data():
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Clear existing data to avoid duplicates on re-run
    await collection.delete_many({})
    print("Cleared existing data in the bus_routes collection.")
    
    # Insert new data
    result = await collection.insert_many(mock_bus_routes)
    print(f"Seeded {len(result.inserted_ids)} bus routes into the database.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())