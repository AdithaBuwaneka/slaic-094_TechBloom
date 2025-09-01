# scripts/seed_database.py

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# --- Make sure these details match your database.py ---
MONGO_DETAILS = "mongodb+srv://TechBloom:TechBloom123@smarttransitcompanion.j3c5osf.mongodb.net/"
DB_NAME = "transit_companion_db_dev"  # Match the .env DATABASE_NAME
COLLECTION_NAME = "bus_routes"

# --- Here is our mock data ---
mock_bus_routes = [
    {
        "route_number": "138",
        "origin": "Pettah",
        "destination": "Maharagama",
        "stops": ["Fort", "Maradana", "Borella", "Narahenpita", "Nugegoda"],
        "operator": "SLTB",
        "fare": 45.0,
        "frequency": "15-20 minutes",
        "operating_hours": "5:00 AM - 11:00 PM"
    },
    {
        "route_number": "177",
        "origin": "Kollupitiya",
        "destination": "Kaduwela",
        "stops": ["Bambalapitiya", "Thummulla", "Rajagiriya", "Battaramulla", "Malabe"],
        "operator": "Private",
        "fare": 65.0,
        "frequency": "10-15 minutes",
        "operating_hours": "5:30 AM - 10:30 PM"
    },
    {
        "route_number": "120",
        "origin": "Pettah",
        "destination": "Piliyandala",
        "stops": ["Fort", "Slave Island", "Wellawatte", "Dehiwala", "Kohuwala", "Nugegoda", "Delkanda"],
        "operator": "SLTB",
        "fare": 55.0,
        "frequency": "20-25 minutes",
        "operating_hours": "5:00 AM - 11:30 PM"
    },
    {
        "route_number": "01",
        "origin": "Pettah",
        "destination": "Kandy",
        "stops": ["Fort", "Maradana", "Kelaniya", "Kiribathgoda", "Gampaha", "Veyangoda", "Mirigama", "Polgahawela", "Kurunegala", "Dambulla"],
        "operator": "SLTB",
        "fare": 180.0,
        "frequency": "30-45 minutes",
        "operating_hours": "4:30 AM - 10:00 PM"
    },
    {
        "route_number": "02",
        "origin": "Pettah",
        "destination": "Galle",
        "stops": ["Fort", "Mount Lavinia", "Kalutara", "Beruwala", "Aluthgama", "Hikkaduwa", "Unawatuna"],
        "operator": "SLTB",
        "fare": 165.0,
        "frequency": "20-30 minutes",
        "operating_hours": "4:00 AM - 11:00 PM"
    }
]

# Add train routes data
mock_train_routes = [
    {
        "route_name": "Main Line",
        "origin": "Colombo Fort",
        "destination": "Badulla",
        "stops": ["Maradana", "Ragama", "Gampaha", "Veyangoda", "Mirigama", "Polgahawela", "Kurunegala", "Dambulla", "Matale", "Kandy", "Peradeniya", "Gampola", "Nawalapitiya", "Hatton", "Nanu Oya", "Pattipola", "Ohiya", "Idalgashinna", "Haputale", "Diyatalawa", "Bandarawela"],
        "operator": "Sri Lanka Railways",
        "classes": ["3rd Class", "2nd Class", "1st Class"],
        "fares": {"3rd_class": 120.0, "2nd_class": 240.0, "1st_class": 480.0},
        "frequency": "4 trains daily",
        "operating_hours": "6:00 AM - 9:00 PM"
    },
    {
        "route_name": "Coastal Line",
        "origin": "Colombo Fort",
        "destination": "Matara",
        "stops": ["Maradana", "Mount Lavinia", "Panadura", "Kalutara South", "Beruwala", "Aluthgama", "Hikkaduwa", "Galle", "Unawatuna", "Koggala", "Weligama"],
        "operator": "Sri Lanka Railways",
        "classes": ["3rd Class", "2nd Class"],
        "fares": {"3rd_class": 85.0, "2nd_class": 170.0},
        "frequency": "6 trains daily",
        "operating_hours": "5:30 AM - 8:30 PM"
    }
]

# Add tuk-tuk services
mock_tuk_tuk_services = [
    {
        "service_name": "Colombo City Tuk-Tuk",
        "coverage_area": "Colombo Metropolitan Area",
        "base_fare": 100.0,
        "per_km_rate": 50.0,
        "contact_number": "+94 11 234 5678",
        "estimated_arrival_time": 5,
        "available_24_7": True
    },
    {
        "service_name": "Kandy Hill Taxis",
        "coverage_area": "Kandy and Hill Country",
        "base_fare": 120.0,
        "per_km_rate": 60.0,
        "contact_number": "+94 81 234 5678",
        "estimated_arrival_time": 8,
        "available_24_7": False
    }
]

async def seed_data():
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]
    
    # Seed bus routes
    bus_collection = db[COLLECTION_NAME]
    await bus_collection.delete_many({})
    print("Cleared existing data in the bus_routes collection.")
    
    bus_result = await bus_collection.insert_many(mock_bus_routes)
    print(f"Seeded {len(bus_result.inserted_ids)} bus routes into the database.")
    
    # Seed train routes
    train_collection = db["train_routes"]
    await train_collection.delete_many({})
    print("Cleared existing data in the train_routes collection.")
    
    train_result = await train_collection.insert_many(mock_train_routes)
    print(f"Seeded {len(train_result.inserted_ids)} train routes into the database.")
    
    # Seed tuk-tuk services
    tuktuk_collection = db["tuk_tuk_services_collection"]
    await tuktuk_collection.delete_many({})
    print("Cleared existing data in the tuk_tuk_services collection.")
    
    tuktuk_result = await tuktuk_collection.insert_many(mock_tuk_tuk_services)
    print(f"Seeded {len(tuktuk_result.inserted_ids)} tuk-tuk services into the database.")
    
    print("\n=== Database Seeding Complete ===")
    print(f"Total bus routes: {len(bus_result.inserted_ids)}")
    print(f"Total train routes: {len(train_result.inserted_ids)}")
    print(f"Total tuk-tuk services: {len(tuktuk_result.inserted_ids)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())