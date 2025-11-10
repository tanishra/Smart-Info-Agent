from langchain_core.tools import tool
import requests
from datetime import datetime
from config import settings


class AmadeusAPI:
    """
    Internal API client for Amadeus flight data.
    Handles authentication, IATA lookup, and flight searches.
    """

    BASE_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
    BASE_FLIGHT_SEARCH_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    BASE_LOCATION_URL = "https://test.api.amadeus.com/v1/reference-data/locations"

    def __init__(self):
        self.client_id = settings.AMADEUS_CLIENT_ID
        self.client_secret = settings.AMADEUS_CLIENT_SECRET
        self.access_token = None
        self._authenticate()

    # Core API methods
    def _authenticate(self):
        """Fetch a valid access token."""
        try:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            resp = requests.post(self.BASE_TOKEN_URL, data=data, timeout=10)
            resp.raise_for_status()
            self.access_token = resp.json().get("access_token")
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with Amadeus API: {e}")

    def _headers(self):
        """Return authorization headers."""
        if not self.access_token:
            self._authenticate()
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_iata_code(self, city_name: str) -> str:
        """Convert a city name to its IATA code."""
        try:
            params = {"keyword": city_name, "subType": "CITY"}
            resp = requests.get(self.BASE_LOCATION_URL, headers=self._headers(), params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            locations = data.get("data", [])
            return locations[0]["iataCode"] if locations else None
        except Exception as e:
            raise RuntimeError(f"Failed to get IATA code for {city_name}: {e}")

    def search_flights(self, origin_city: str, destination_city: str, departure_date: str = None) -> dict:
        """Search for flights between two cities."""
        departure_date = departure_date or datetime.now().strftime("%Y-%m-%d")

        origin_code = self.get_iata_code(origin_city)
        destination_code = self.get_iata_code(destination_city)

        if not origin_code or not destination_code:
            return {"status": "error", "message": "Could not find IATA code for one of the cities."}

        params = {
            "originLocationCode": origin_code,
            "destinationLocationCode": destination_code,
            "departureDate": departure_date,
            "adults": 1,
            "max": 5,
        }

        try:
            resp = requests.get(self.BASE_FLIGHT_SEARCH_URL, headers=self._headers(), params=params, timeout=15)
            resp.raise_for_status()
            flights = resp.json().get("data", [])
            if not flights:
                return {"status": "error", "message": "No flights found."}

            formatted = []
            for f in flights:
                itinerary = f.get("itineraries", [{}])[0]
                if not itinerary.get("segments"):
                    continue
                seg = itinerary["segments"][0]
                formatted.append({
                    "airline": seg["carrierCode"],
                    "flight_number": seg["number"],
                    "departure_airport": seg["departure"]["iataCode"],
                    "departure_time": seg["departure"]["at"],
                    "arrival_airport": seg["arrival"]["iataCode"],
                    "arrival_time": seg["arrival"]["at"],
                })

            return {"status": "success", "flights": formatted}

        except Exception as e:
            return {"status": "error", "message": f"Flight search failed: {e}"}


# LangGraph Tool Wrapper
amadeus_client = AmadeusAPI()


@tool("search_flights_amadeus")
def search_flights_amadeus(origin_city: str, destination_city: str, departure_date: str = None) -> dict:
    """
    LangGraph Tool: Find available flights between two cities using the Amadeus API..

    Args:
        origin_city (str): Name of origin city (e.g., 'New York')
        destination_city (str): Name of destination city (e.g., 'London')
        departure_date (str, optional): Flight departure date in YYYY-MM-DD format.

    Returns:
        dict: Contains either flight options or error message.
    """
    try:
        return amadeus_client.search_flights(origin_city, destination_city, departure_date)
    except Exception as e:
        return {"status": "error", "message": str(e)}
