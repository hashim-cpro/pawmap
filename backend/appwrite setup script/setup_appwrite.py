import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from dotenv import load_dotenv

load_dotenv()

# Appwrite Configurations
ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
API_KEY = os.getenv("APPWRITE_API_KEY")

DATABASE_ID = "pawmap_db"
DATABASE_NAME = "PawMap Database"
ANIMALS_COLLECTION_ID = "animals"
BUCKET_ID = "animal_media"

if not PROJECT_ID or not API_KEY:
    print("Please set APPWRITE_PROJECT_ID and APPWRITE_API_KEY in the .env file.")
    exit(1)

client = Client()
client.set_endpoint(ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)

databases = Databases(client)
storage = Storage(client)

def setup_appwrite():
    print("Setting up Appwrite project...")
    
    # 1. Create Database
    try:
        databases.get(DATABASE_ID)
        print(f"Database {DATABASE_ID} already exists.")
    except Exception:
        print(f"Creating database {DATABASE_ID}...")
        databases.create(DATABASE_ID, DATABASE_NAME)
    
    # 2. Create Collection
    try:
        databases.get_collection(DATABASE_ID, ANIMALS_COLLECTION_ID)
        print(f"Collection {ANIMALS_COLLECTION_ID} already exists.")
    except Exception:
        print(f"Creating collection {ANIMALS_COLLECTION_ID}...")
        databases.create_collection(
            database_id=DATABASE_ID, 
            collection_id=ANIMALS_COLLECTION_ID, 
            name="Animals"
        )
        
        print("Adding attributes to collection...")
        # Add attributes (schema based on original Postgres schema)
        attributes = [
            ("animal_name", "string", 255, True),
            ("animal_type", "string", 50, True),
            ("breed", "string", 255, False),
            ("color", "string", 100, False),
            ("size", "string", 50, False),
            ("health_status", "string", 255, False),
            ("incident", "string", 50, True),
            ("last_seen", "datetime", 0, True),  # Using ISO 8601 string dates via datetime
            ("latitude", "float", 0, True),
            ("longitude", "float", 0, True),
            ("radius", "integer", 0, False),    # default 1000 in frontend usually
            ("color_code", "string", 50, False),
            ("assets", "string", 10000, False, True), # array of strings (file IDs)
            ("created_at", "datetime", 0, False)
        ]
        
        for attr in attributes:
            attr_name = attr[0]
            attr_type = attr[1]
            attr_size = attr[2]
            required = attr[3]
            is_array = attr[4] if len(attr) > 4 else False
            
            if attr_type == "string":
                databases.create_string_attribute(DATABASE_ID, ANIMALS_COLLECTION_ID, attr_name, attr_size, required, array=is_array)
            elif attr_type == "float":
                databases.create_float_attribute(DATABASE_ID, ANIMALS_COLLECTION_ID, attr_name, required, array=is_array)
            elif attr_type == "integer":
                databases.create_integer_attribute(DATABASE_ID, ANIMALS_COLLECTION_ID, attr_name, required, array=is_array)
            elif attr_type == "datetime":
                databases.create_datetime_attribute(DATABASE_ID, ANIMALS_COLLECTION_ID, attr_name, required, array=is_array)
            
            print(f"  Added {attr_name}")

    # 3. Create Storage Bucket
    try:
        storage.get_bucket(BUCKET_ID)
        print(f"Bucket {BUCKET_ID} already exists.")
    except Exception:
        print(f"Creating bucket {BUCKET_ID}...")
        storage.create_bucket(
            bucket_id=BUCKET_ID,
            name="Animal Media",
            permissions=["read(\"any\")", "create(\"users\")", "update(\"users\")", "delete(\"users\")"], # Any user can read, logged in can create
            file_security=False,
            maximum_file_size=5242880, # 5MB limit
            allowed_file_extensions=["jpg", "jpeg", "png", "gif", "mp4", "webm"]
        )

    print("\nSetup Complete!")
    print(f"Database ID: {DATABASE_ID}")
    print(f"Collection ID: {ANIMALS_COLLECTION_ID}")
    print(f"Bucket ID: {BUCKET_ID}")

if __name__ == "__main__":
    setup_appwrite()
