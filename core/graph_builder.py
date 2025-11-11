import os
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from core.memory_store import MemoryStore
from config import settings
from tools.weather_tool import get_weather_info
from tools.crypto_tool import get_crypto_price
from tools.numverify_tool import verify_phone_number
from tools.amadeus_tool import search_flights_amadeus


class SmartInfoAgent:
    """
    Smart Info Agent powered by Azure OpenAI (GPT models).
    Uses automatic tool calling — the LLM decides which tool to use.
    """

    def __init__(self):
        self.memory = MemoryStore()

        # Provide required Azure API version
        api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

        # Initialize Azure OpenAI LLM
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version=api_version,
            deployment_name=settings.AZURE_DEPLOYMENT_NAME,
            openai_api_type="azure",
            model_kwargs={"max_completion_tokens": 800},
        )

        # Register tools
        self.tools = [
            get_weather_info,
            get_crypto_price,
            verify_phone_number,
            search_flights_amadeus,
        ]

        # Updated prompt with required `agent_scratchpad`
        self.prompt = ChatPromptTemplate.from_template("""
You are SmartInfoAgent — an intelligent AI assistant that can use the following tools:

1. 🌦️ get_weather_info(city: str) → Get current weather details.
2. 💰 get_crypto_price(symbol: str) → Get live cryptocurrency prices.
3. ☎️ verify_phone_number(phone_number: str) → Validate a phone number and get region/operator.
4. ✈️ search_flights_amadeus(source: str, destination: str, date: str) → Find available flights.

Your goals:
- Choose the correct tool automatically when needed.
- Respond conversationally when tools aren't required.
- Be polite, clear, and helpful.

Conversation:
{input}

Previous reasoning and actions:
{agent_scratchpad}
""")

        # Create tool-calling agent (ReAct pattern)
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )

        # Create executor (handles reasoning + tool execution)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
        )

    def run(self, user_input: str) -> str:
        """Executes user query using automatic Azure OpenAI tool selection."""
        try:
            response = self.executor.invoke({"input": user_input})
            final_response = response.get("output", "No response from model.")
            self.memory.append(user_input, final_response)
            return final_response
        except Exception as e:
            return f"⚠️ Could not complete the request.\nDetails: {e}"

    def show_history(self):
        """Return full chat history."""
        return self.memory.get_history()
