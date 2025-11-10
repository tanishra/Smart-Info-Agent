from langchain_core.tools import tool
import requests
from datetime import datetime
from config import settings


class WeatherStackAPI:
    """
    Internal API client for the Weatherstack service.
    Fetches real-time weather information for any city.
    """

    BASE_URL = "http://api.weatherstack.com/current"

    def __init__(self):
        self.api_key = settings.WEATHERSTACK_API_KEY

    # Core Weather Retrieval Method
    def get_weather(self, city: str) -> dict:
        """
        Fetch the current weather for a given city using Weatherstack API.

        Args:
            city (str): City name (e.g., 'Delhi', 'New York', 'Tokyo').

        Returns:
            dict: A structured response containing temperature, humidity,
                  pressure, wind details, and weather descriptions.
        """
        if not city or not city.strip():
            return {"status": "error", "message": "City name is required."}

        params = {
            "access_key": self.api_key,
            "query": city.strip(),
        }

        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # Handle API-level errors
            if "error" in data:
                return {
                    "status": "error",
                    "message": data["error"].get("info", "Unknown error from Weatherstack API."),
                }

            current = data.get("current", {})
            location = data.get("location", {})

            # Build standardized result
            return {
                "status": "success",
                "city": location.get("name", city),
                "country": location.get("country"),
                "region": location.get("region"),
                "temperature_c": current.get("temperature"),
                "feelslike_c": current.get("feelslike"),
                "humidity": current.get("humidity"),
                "pressure": current.get("pressure"),
                "wind_speed": current.get("wind_speed"),
                "wind_dir": current.get("wind_dir"),
                "weather_descriptions": current.get("weather_descriptions", []),
                "observation_time": current.get("observation_time"),
                "timestamp": datetime.now().isoformat(),
            }

        except requests.Timeout:
            return {"status": "error", "message": "Weatherstack API request timed out."}

        except requests.RequestException as e:
            return {"status": "error", "message": f"Network or API error: {e}"}

        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}


# LangGraph Tool Wrapper
weather_client = WeatherStackAPI()


@tool("get_weather_info")
def get_weather_info(city: str) -> dict:
    """
    LangGraph Tool: Retrieve the current weather for a given city using the Weatherstack API.Includes temperature, humidity, and wind information..

    Args:
        city (str): City name (e.g., 'Delhi', 'New York', 'Tokyo').

    Returns:
        dict: Weather details including:
            - status: 'success' or 'error'
            - city: City name
            - country: Country name
            - temperature_c: Current temperature in Celsius
            - feelslike_c: Feels-like temperature
            - humidity: Humidity percentage
            - pressure: Atmospheric pressure
            - wind_speed: Wind speed in km/h
            - wind_dir: Wind direction
            - weather_descriptions: List of short textual descriptions
            - timestamp: ISO UTC timestamp
    """
    try:
        return weather_client.get_weather(city)
    except Exception as e:
        return {"status": "error", "message": str(e)}
