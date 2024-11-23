import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_mongo_connection():
    """
    Create a MongoDB client connection using environment variables.
    """
    host = os.getenv("MONGO_HOST", "localhost")
    port = os.getenv("MONGO_PORT", "27017")
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")

    if username and password:
        uri = f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"
    else:
        uri = f"mongodb://{host}:{port}/"
    client = MongoClient(uri)
    return client


def backup_database(client, database_name, output_dir="mongo_backup"):
    """
    Back up all collections in a MongoDB database to JSON files.
    """
    try:
        db = client[database_name]
        os.makedirs(output_dir, exist_ok=True)
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            data = list(collection.find())

            # Convert ObjectId and other non-serializable types to strings
            for document in data:
                document["_id"] = str(document["_id"])

            # Save to JSON file
            output_file = os.path.join(output_dir, f"{collection_name}.json")
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"Backed up {collection_name} to {output_file}")
    except Exception as e:
        print(f"Error while backing up database: {e}")


if __name__ == "__main__":
    # Load configurations
    database_name = os.getenv("DATABASE_NAME")
    output_dir = os.getenv("OUTPUT_DIR", "mongo_backup")

    if not database_name:
        print("DATABASE_NAME is not set in the .env file.")
        exit(1)

    # Connect to MongoDB
    try:
        client = get_mongo_connection()
        print("Connected to MongoDB successfully.")

        # Back up the database
        backup_database(client, database_name, output_dir)
        print(f"Database backup completed. Files saved in '{output_dir}'.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
