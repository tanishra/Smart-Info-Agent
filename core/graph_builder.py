import os
import operator
from typing_extensions import TypedDict, Annotated

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AnyMessage
from langgraph.graph import StateGraph, START, END

from core.memory_store import MemoryStore
from config import settings

# Import already LangGraph-compatible tools
from tools.weather_tool import get_weather_info
from tools.crypto_tool import get_crypto_price
from tools.numverify_tool import verify_phone_number
from tools.amadeus_tool import search_flights_amadeus

from langsmith.run_helpers import traceable


# Define the agent's internal state
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


# Initialize Azure OpenAI model
api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

llm = AzureChatOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    api_version=api_version,
    deployment_name=settings.AZURE_DEPLOYMENT_NAME,
    openai_api_type="azure",
    max_completion_tokens=800,
)

tools = [get_weather_info, get_crypto_price, verify_phone_number, search_flights_amadeus]
tools_by_name = {t.name: t for t in tools}

# Bind tools to the LLM so it can call them automatically
llm_with_tools = llm.bind_tools(tools)

# System prompt
SYSTEM_PROMPT = """
You are SmartInfoAgent — an intelligent AI assistant with access to these tools:
1 get_weather_info(city)
2 get_crypto_price(symbol)
3 verify_phone_number(phone_number)
4 search_flights_amadeus(source, destination, date)

💡 Rules:
- Always use tools when users ask for weather, crypto, phone, or flight information.
- Summarize tool results in natural, friendly language.
- Be concise, polite, and clear.
"""


# Node 1: LLM decides what to do
def llm_node(state: AgentState) -> dict:
    msgs = state["messages"]
    system = SystemMessage(content=SYSTEM_PROMPT)

    response = llm_with_tools.invoke([system] + msgs)
    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# Node 2: Execute tool calls
def tool_node(state: AgentState) -> dict:
    msgs = state["messages"]
    last_msg = msgs[-1]
    results = []

    tool_calls = getattr(last_msg, "tool_calls", [])
    if not tool_calls:
        print("No tool calls found in LLM output.")
        return {"messages": []}

    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        print(f"🛠 Executing tool: {tool_name} | Args: {tool_args}")

        try:
            tool_func = tools_by_name[tool_name]

            # use .invoke() — pass input dict directly
            observation = tool_func.invoke(tool_args)

            print(f"{tool_name} executed successfully.")
            results.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))

        except Exception as e:
            error_msg = f"Error executing {tool_name}: {e}"
            print(error_msg)
            results.append(ToolMessage(content=error_msg, tool_call_id=tool_call["id"]))

    return {"messages": results}


# Node 3: Decide whether to call tools again or finish
def decide_next(state: AgentState) -> str:
    msgs = state["messages"]
    last = msgs[-1]
    if getattr(last, "tool_calls", []):
        return "tool_node"
    return END


# Build the LangGraph workflow
graph = StateGraph(AgentState)
graph.add_node("llm_node", llm_node)
graph.add_node("tool_node", tool_node)

graph.add_edge(START, "llm_node")
graph.add_conditional_edges("llm_node", decide_next, ["tool_node", END])
graph.add_edge("tool_node", "llm_node")

agent = graph.compile()


# Agent wrapper class
class SmartInfoAgent:
    def __init__(self):
        self.agent = agent
        self.memory = MemoryStore()

    @traceable(name="SmartInfoAgent.run")
    def run(self, user_input: str) -> str:
        try:
            state: AgentState = {
                "messages": [HumanMessage(content=user_input)],
                "llm_calls": 0
            }
            result_state = self.agent.invoke(state)
            output_msgs = result_state["messages"]
            ai_msg = output_msgs[-1]
            reply = ai_msg.content
            self.memory.append(user_input, reply)
            return reply
        except Exception as e:
            return f"Could not complete the request.\nDetails: {e}"


    def show_history(self):
        return self.memory.get_history()