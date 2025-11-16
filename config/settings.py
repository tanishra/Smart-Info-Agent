import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# EURON API Key
# EURON_API_KEY = os.getenv("EURON_API_KEY")

# GOOGLE API KEY
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# OpenRouter API settings
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  
# OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Optional headers for site ranking on OpenRouter.ai
# OPENROUTER_HTTP_REFERER = os.getenv("OPENROUTER_HTTP_REFERER")
# OPENROUTER_X_TITLE = os.getenv("OPENROUTER_X_TITLE")           

# Default model
# DEFAULT_MODEL = "openai/gpt-oss-20b:free"
# DEFAULT_MODEL="mistralai/Mistral-7B-Instruct-v0.3"
# DEFAULT_MODEL= "meta-llama/llama-3.1-8b-instruct:free"
# DEFAULT_MODEL = "qwen/qwen3-coder:free"
# DEFAULT_MODEL = "gpt-4.1-nano"
# DEFAULT_MODEL = "gemini-2.5-flash-lite"

# WeatherStack API
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API")

# Crypto API
COINMARKETCAP_API = os.getenv("COINMARKETCAP_API")

# NumVerify API
NUMVERIFY_API = os.getenv("NUMVERIFY_API")

# Amadeus Credentials
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")


# HuggingFace API
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# GROK API KEY
# GROK_API_KEY = os.getenv("GROK_API_KEY")
# GROK_API_URL = os.getenv("GROK_API_URL")

# AZURE API KEY
AZURE_OPENAI_KEY =os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

# Azure OpenAI Embeddings (for RAG)
# AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")

# ChromaDB settings
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", None)

# OpenAI API Version
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

# Chroma DB Credentials
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
CHROMA_CLIENT_HOST = os.getenv("CHROMA_CLIENT_HOST")