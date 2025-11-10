from langchain_core.tools import tool
import requests
from datetime import datetime
from config import settings


class CoinMarketAPI:
    """
    Internal API client for CoinMarketCap.
    Handles cryptocurrency price lookups and related metadata.
    """

    BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    def __init__(self):
        self.api_key = settings.COINMARKETCAP_API

    # Core API methods
    def get_price(self, symbol: str) -> dict:
        """
        Fetch the latest price for a given cryptocurrency symbol (e.g., BTC, ETH).
        Returns a structured dictionary suitable for agent responses.
        """
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key,
        }
        params = {"symbol": symbol.upper(), "convert": "USD"}

        try:
            resp = requests.get(self.BASE_URL, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if "data" not in data or symbol.upper() not in data["data"]:
                return {
                    "status": "error",
                    "message": f"Symbol '{symbol}' not found in API response.",
                }

            info = data["data"][symbol.upper()]
            quote = info["quote"]["USD"]

            return {
                "status": "success",
                "symbol": symbol.upper(),
                "name": info.get("name", "Unknown"),
                "price_usd": round(quote.get("price", 0), 2),
                "percent_change_24h": round(quote.get("percent_change_24h", 0), 2),
                "market_cap_usd": round(quote.get("market_cap", 0), 2),
                "timestamp": datetime.now().isoformat(),
            }

        except requests.Timeout:
            return {"status": "error", "message": "Request timed out while contacting CoinMarketCap API."}

        except requests.RequestException as e:
            return {"status": "error", "message": f"Network or API error: {e}"}

        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}


# LangGraph-compatible tool wrapper
coinmarket_client = CoinMarketAPI()


@tool("get_crypto_price")
def get_crypto_price(symbol: str) -> dict:
    """
    LangGraph Tool: Fetch the latest cryptocurrency price, 24-hour change, and market cap
        using the CoinMarketCap API.

    Args:
        symbol (str): The ticker symbol (e.g., 'BTC', 'ETH', 'DOGE').

    Returns:
        dict: A JSON-compatible structure containing:
            - status: "success" or "error"
            - symbol: Cryptocurrency symbol
            - name: Cryptocurrency name
            - price_usd: Latest price in USD
            - percent_change_24h: 24-hour percentage change
            - market_cap_usd: Market capitalization
            - timestamp: UTC ISO timestamp
    """
    try:
        return coinmarket_client.get_price(symbol)
    except Exception as e:
        return {"status": "error", "message": str(e)}

