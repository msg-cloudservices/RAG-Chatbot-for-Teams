import os
from dotenv import load_dotenv
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

load_dotenv()

#importing Azure OpenAI creds
api_key = os.getenv("AZURE_OPENAI_KEY")
os.environ["OPENAI_API_KEY"]= api_key
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name=os.getenv("EMBEDDING_DEPLOYMENT_NAME")
key = os.getenv("AZURE_SEARCH_ADMIN_KEY")

#initiate AI Searchservice
service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
service_name = os.getenv("AZURE_SEARCH_NAME")
cogkey = os.getenv("AZURE_SEARCH_ADMIN_KEY")
credential = AzureKeyCredential(key)
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

client = AzureOpenAI(
    azure_endpoint=azure_endpoint, api_key=api_key, api_version="2023-05-15"
)

search_client = SearchClient(
    endpoint=service_endpoint,
    index_name=index_name,
    credential=credential,
)


def get_doc_azure_ai(prompt):
    embedding = client.embeddings.create(input=prompt, model=deployment_name).data[0].embedding
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields="embedding")
    
    results = search_client.search(  
        search_text=None,  
        vector_queries= [vector_query],
        select=["id", "line", "filename"],
    )  
    
    return [chunk["line"].strip() for chunk in results]