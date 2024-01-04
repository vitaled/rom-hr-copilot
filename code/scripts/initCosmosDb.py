import json
import os
from azure.cosmos import CosmosClient
import codecs
from dotenv import load_dotenv
from azure.identity import ManagedIdentityCredential

# Define the connection string and database details
endpoint = os.getenv("COSMOS_ENDPOINT")  # Get Cosmos DB endpoint from environment variable
database_name = os.getenv("COSMOS_DATABASE_NAME")  # Get Cosmos DB database name from environment variable
container_name = "profiles"  # Define the container name

# Read the JSON file
with codecs.open("./data/profiles.json", "r",encoding='UTF-8') as file:
    items = json.load(file)  # Load the JSON data into the items variable

# Initialize the Cosmos DB client
# Use ManagedIdentityCredential to authenticate using the client ID of the managed identity
client = CosmosClient(endpoint, credential=ManagedIdentityCredential(client_id=os.getenv("APP_CONTAINER_CLIENT_ID")))

# Get the database and container
database = client.get_database_client(database_name)  # Get a client for the specified database
container = database.get_container_client(container_name)  # Get a client for the specified container

# Insert the items into the container
for item in items:
    container.upsert_item(item)  # Insert each item into the container. If an item with the same id already exists, it will be replaced