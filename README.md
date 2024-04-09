# RAG-Chatbot-for-Teams
A Chatbot to chat with Azure OpenAI on your own data, ready to be deployed to Teams

## Prerequisites
1. Create virtual python environment and install dependencies from `requirements.txt`.
2. Create `.env`-file in root directory of the project and add the following environment variables:
```
AZURE_OPENAI_KEY = "" 
AZURE_OPENAI_ENDPOINT = ""
EMBEDDING_DEPLOYMENT_NAME = ""
CHAT_DEPLOYMENT_NAME = ""

AI_SEARCH_SERVICE_ENDPOINT = ""
AI_SEARCH_NAME = ""
AI_SEARCH_INDEX_NAME = ""
AI_SEARCH_ADMIN_KEY = ""

AZURE_COSMOS_DB_HOST = ""
AZURE_COSMOS_DB_KEY = ""
AZURE_COSMOS_DATABASE = ""
AZURE_COSMOS_CONTAINER = ""

MICROSOFT_APP_ID = ""
MICROSOFT_APP_PASSWORD = ""
```