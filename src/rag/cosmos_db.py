import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
from azure.core.exceptions import AzureError
from azure.cosmos import CosmosClient, PartitionKey
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import os
import datetime
import uuid
import logging

cosmos_db_host = os.environ.get("AZURE_COSMOS_DB_HOST")
cosmos_db_master_key = os.environ.get("AZURE_COSMOS_DB_KEY")
cosmos_db_database_id = os.environ.get("AZURE_COSMOS_DATABASE")
cosmos_db_container_id = os.environ.get("AZURE_COSMOS_CONTAINER")

logging.info(f"cosmos_db_host: {cosmos_db_host}")
if cosmos_db_master_key:
    logging.info(f"cosmos_db_master_key: {len(cosmos_db_master_key)}")
logging.info(f"cosmos_db_database_id: {cosmos_db_database_id}")
logging.info(f"cosmos_db_container_id: {cosmos_db_container_id}")


# setup connection to Cosmos DB
client = cosmos_client.CosmosClient(
    cosmos_db_host,
    {"masterKey": cosmos_db_master_key},
    user_agent="TeamsNDRWebApp",
    user_agent_overwrite=True,
)
db = client.get_database_client(cosmos_db_database_id)
container = db.get_container_client(cosmos_db_container_id)


def query_items(conversation_id):
    items = list(
        container.query_items(
            query="SELECT * FROM r WHERE r.conversationId=@conversation_id",
            parameters=[{"name": "@conversation_id", "value": conversation_id}],
        )
    )
    return items


def create_items(item):
    chat_message = {
        "id": str(uuid.uuid4()),
        "conversationId": item.get("conversation_id"),
        "role": item.get("role"),
        "content": item.get("content"),
        "timestamp": datetime.datetime.now().isoformat(),
        "position": item.get("position") or 0,
    }
    container.create_item(body=chat_message)

