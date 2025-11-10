import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# WeatherStack API
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API")

# Crypto API
COINMARKETCAP_API = os.getenv("COINMARKETCAP_API")

# NumVerify API
NUMVERIFY_API = os.getenv("NUMVERIFY_API")

# Amadeus Credentials
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

# AZURE API KEY
AZURE_OPENAI_KEY =os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")