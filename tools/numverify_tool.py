from langchain_core.tools import tool
import requests
from config import settings


class NumVerifyAPI:
    """
    Internal API client for NumVerify.
    Validates phone numbers and retrieves metadata such as carrier, country, and line type.
    """

    BASE_URL = "http://apilayer.net/api/validate"

    def __init__(self):
        self.api_key = settings.NUMVERIFY_API

    # Core API logic
    def lookup(self, phone_number: str) -> dict:
        """
        Validate a phone number and fetch metadata via NumVerify API.

        Args:
            phone_number (str): The phone number (e.g., +14158586273).

        Returns:
            dict: Structured validation result with country, carrier, and line type.
        """
        if not phone_number or not phone_number.strip():
            return {"status": "error", "message": "Phone number is required."}

        params = {
            "access_key": self.api_key,
            "number": phone_number,
            "format": 1,
        }

        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # Handle API-level errors
            if "error" in data:
                return {
                    "status": "error",
                    "message": data["error"].get("info", "Invalid API request."),
                }

            if not data.get("valid"):
                return {
                    "status": "invalid",
                    "message": f"{phone_number} is not a valid phone number.",
                }

            return {
                "status": "success",
                "number": data.get("international_format"),
                "country_name": data.get("country_name"),
                "country_code": data.get("country_code"),
                "location": data.get("location"),
                "carrier": data.get("carrier"),
                "line_type": data.get("line_type"),
            }

        except requests.Timeout:
            return {"status": "error", "message": "NumVerify API request timed out."}

        except requests.RequestException as e:
            return {"status": "error", "message": f"Network or API error: {e}"}

        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}


# LangGraph-compatible Tool wrapper
numverify_client = NumVerifyAPI()


@tool("verify_phone_number")
def verify_phone_number(phone_number: str) -> dict:
    """
    LangGraph Tool: Validate a phone number and retrieve metadata using the NumVerify API.Returns country, carrier, and line type if available..

    Args:
        phone_number (str): The phone number to check (e.g., '+14158586273').

    Returns:
        dict: Contains validation results including:
            - status: 'success', 'invalid', or 'error'
            - number: formatted number
            - country_name: country of the number
            - country_code: ISO country code
            - location: city/region
            - carrier: telecom provider
            - line_type: 'mobile' or 'landline'
    """
    try:
        return numverify_client.lookup(phone_number)
    except Exception as e:
        return {"status": "error", "message": str(e)}
