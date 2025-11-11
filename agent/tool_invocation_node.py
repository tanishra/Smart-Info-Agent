from core.state_schema import AgentState
from tools.weather_tool import get_weather_info
from tools.crypto_tool import get_crypto_price
from tools.numverify_tool import verify_phone_number
from tools.amadeus_tool import search_flights_amadeus
from langchain_core.tools import BaseTool


# Tool registry (add all tools here)
TOOL_REGISTRY = {
    "get_weather_info": get_weather_info,
    "get_crypto_price": get_crypto_price,
    "verify_phone_number": verify_phone_number,
    "search_flights_amadeus": search_flights_amadeus,
}

def tool_invocation_node(state: AgentState, memory) -> AgentState:
    """
    Executes whichever tool the LLM selects, automatically and safely.
    Works with both LangChain BaseTool and normal Python functions.
    Handles alias normalization (e.g., 'location' → 'city').
    """
    tool_name = getattr(state, "tool_name", None)
    args = getattr(state, "tool_args", {}) or {}

    if not tool_name:
        state.final_response = "⚠️ No tool specified by the agent."
        return state

    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        state.final_response = f"⚠️ Unknown tool: {tool_name}"
        return state

    # Alias normalization for tool parameters
    alias_map = {
        "location": "city",
        "city": "city",
        "source": "origin_city",
        "origin": "origin_city",
        "from": "origin_city",
        "destination": "destination_city",
        "to": "destination_city",
        "phone": "phone_number",
        "number": "phone_number",
        "symbol": "symbol",
        "date": "date",
    }

    normalized_args = {}
    for key, value in args.items():
        normalized_key = alias_map.get(key.lower(), key)
        normalized_args[normalized_key] = value

    # Ensure 'city' is provided for weather tool
    if tool_name == "get_weather_info":
        if "city" not in normalized_args:
            if "location" in args:
                normalized_args["city"] = args["location"]
            else:
                state.final_response = (
                    "⚠️ Missing required parameter: 'city'. "
                    "Please provide a city name (e.g., 'Delhi' or 'Mumbai')."
                )
                return state

    try:
        # Safe execution of tool
        if isinstance(tool, BaseTool):
            result = tool.invoke(normalized_args)
        elif callable(tool):
            result = tool(**normalized_args)
        else:
            raise TypeError(f"Invalid tool type: {type(tool)}")

        # Save results into agent state
        state.tool_name = tool_name
        state.tool_args = normalized_args
        state.tool_result = result

        # Format human-readable response
        if isinstance(result, dict):
            if tool_name == "get_weather_info":
                state.final_response = (
                    f"🌦️ Weather Report for {normalized_args.get('city', 'Unknown')}:\n"
                    f"- Temperature: {result.get('temperature_c', 'N/A')}°C\n"
                    f"- Condition: {result.get('description', 'N/A')}\n"
                    f"- Feels Like: {result.get('feels_like_c', 'N/A')}°C\n"
                    f"- Humidity: {result.get('humidity', 'N/A')}%\n"
                    f"- Wind Speed: {result.get('wind_kph', 'N/A')} km/h"
                )
            elif tool_name == "get_crypto_price":
                state.final_response = (
                    f"💰 {result.get('symbol', '').upper()} Price: "
                    f"${result.get('price_usd', 'N/A')} USD"
                )
            elif tool_name == "verify_phone_number":
                state.final_response = (
                    f"📞 Phone Verification — {result.get('international_format', '')}\n"
                    f"- Country: {result.get('country_name', 'Unknown')}\n"
                    f"- Carrier: {result.get('carrier', 'Unknown')}\n"
                    f"- Line Type: {result.get('line_type', 'Unknown')}"
                )
            elif tool_name == "search_flights_amadeus":
                flights = result.get("flights", [])
                if flights:
                    formatted_flights = "\n".join(
                        [
                            f"✈️ {f['from']} → {f['to']} ({f['airline']}) - "
                            f"${f['price']} USD, Departs {f['departure_time']}"
                            for f in flights[:3]
                        ]
                    )
                    state.final_response = f"🛫 Available Flights:\n{formatted_flights}"
                else:
                    state.final_response = "No flights found for the given route/date."
            else:
                state.final_response = str(result)
        else:
            state.final_response = str(result)

    except Exception as e:
        state.final_response = f"Error executing {tool_name}: {e}"

    return state
