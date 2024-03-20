import os
from openai import AzureOpenAI

# from langchain_openai import AzureChatOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    QueryCaptionResult,
    QueryType,
    VectorizedQuery,
    VectorQuery,
)
import logging

#importing Azure OpenAI creds
api_key = os.environ.get("AZURE_OPENAI_KEY")
azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
deployment_name=os.environ.get("EMBEDDING_DEPLOYMENT_NAME")

#initiate AI Searchservice
service_endpoint = os.environ.get("AI_SEARCH_SERVICE_ENDPOINT")
service_name = os.environ.get("AI_SEARCH_NAME")
cogkey = os.environ.get("AI_SEARCH_ADMIN_KEY")
credential = AzureKeyCredential(cogkey)
index_name = os.environ.get("AI_SEARCH_INDEX_NAME")

logging.info(f"service_endpoint: {service_endpoint}")
logging.info(f"service_name: {service_name}")
if cogkey:
    logging.info(f"cogkey: {len(cogkey)}")
logging.info(f"index_name: {index_name}")

client = AzureOpenAI(
    azure_endpoint=azure_endpoint, api_key=api_key, api_version="2023-05-15"
)

search_client = SearchClient(
    endpoint=service_endpoint,
    index_name=index_name,
    credential=credential,
)


def get_doc_azure_ai(prompt, similarity_threshold=0):
    embedding = client.embeddings.create(input=prompt, model=deployment_name).data[0].embedding
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields="embedding")

    results = search_client.search(  
        search_text=None,  
        vector_queries= [vector_query],
        select=["id", "line", "filename"],
    )  

    return [chunk["line"].strip() for chunk in results if chunk["@search.score"] > similarity_threshold]