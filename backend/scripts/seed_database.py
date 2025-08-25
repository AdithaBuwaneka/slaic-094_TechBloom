# scripts/seed_database.py

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# --- Make sure these details match your database.py ---
MONGO_DETAILS = "mongodb+srv://TechBloom:TechBloom123@smarttransitcompanion.j3c5osf.mongodb.net/"
DB_NAME = "transit_companion"
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