# Smart Info Agent

## Overview
**Smart Info Agent** is a modular **LangGraph-based intelligent assistant** designed to interact with multiple public APIs, maintain conversational context, and provide synthesized, human-readable answers to user queries.  

This project serves as a practical demonstration of **modular AI workflow design** and is suitable for training freshers on:  

- LangGraph **node-tool architecture**  
- Modular **LLM workflows**  
- Integration with **real-time APIs**  
- Managing **memory & conversational context** efficiently  
- Implementing **intent classification** and response synthesis  
- Building **interactive user interfaces** with Streamlit  

The agent supports multiple domains including flights, cryptocurrency, weather, and phone number verification, with **follow-up queries** handled contextually.  

---

## Key Features

- **Multi-domain Query Support:**  
  - Flights → Amadeus API  
  - Crypto → CoinMarket API  
  - Weather → Weather Stack API  
  - Phone Verification → Numverify API  

- **Context-Aware Follow-Ups:** Handles queries like:  
  - “Temperature in Delhi” → “Compare with Mumbai”  
  - “Price of Bitcoin” → “Compare with Ethereum”  

- **Modular LangGraph Nodes:** Each functionality is encapsulated in its own node, making the system scalable and maintainable.  

- **API Integration via Tools:** Each node uses an API tool wrapper for seamless calls and data retrieval.  

- **Memory & Context Management:** Stores minimal data (user input, previous response, timestamp) to maintain session context.  

- **Intent Classification & Response Synthesis:** Uses LLMs for classifying queries and generating natural, human-readable answers.  

- **Interactive UI with Streamlit:**  
  - Chat interface  
  - Spinner during processing  
  - Persistent chat history  
  - Proper formatting for multi-line and tabular responses  

- **Extensible Architecture:** New domains and APIs can be added by creating new nodes and tools without disrupting the existing workflow.  

---

## Suggested Libraries & Tools

- **LangGraph** – Orchestrating nodes and workflow  
- **OpenAI** – For LLM-driven response synthesis  
- **Requests** – For API calls  
- **Streamlit** – User interface for chat  
- **Datetime** – Timestamping responses  
- **Python Dict / JSON** – In-memory storage and memory dump  
- **CoinMarket API, Weather Stack API, Amadeus API, Numverify API** – Real-time data sources  
- **EURON API** - For LLMs like (OpenAI, Gemini, Llama, Mistral, etc)

---

# Folder Structure

# smart_info_agent/
## README.md
Project overview, setup, and usage guide

## requirements.txt
Dependencies (LangGraph, requests, OpenAI, Streamlit, etc.)

## main.py
CLI entry point for testing the agent

## app.py
Streamlit interface for interactive chat

# config/
## __init__.py
## settings.py
API keys, constants, config parameters

# core/
## __init__.py
## graph_builder.py
Constructs LangGraph workflow

## memory_store.py
In-memory storage management

## intent_classifier.py
Classifies user intent

## response_synthesizer.py
Generates final responses

## state_schema.py
Agent schema

# nodes/
## __init__.py

## memory_node.py
Reads/writes memory

## decision_node.py
Routes workflow based on intent

## response_node.py
Synthesizes final output

## amadeus_node.py
Handles flight-related queries via Amadeus API

## crypto_node.py
Handles cryptocurrency-related queries via CoinMarket API

## weather_node.py
Handles weather-related queries via Weather Stack API

## numverify_node.py
Handles phone number verification via Numverify API

# tools/
## __init__.py

## amadeus_tool.py
Wrapper for Amadeus API

## crypto_tool.py
Wrapper for CoinMarket API

## weather_tool.py
Wrapper for Weather Stack API

## numverify_tool.py
Wrapper for Numverify API

# data/
## __init__.py
## memory_dump.json
Optional memory snapshot for evaluation


---

## Folder Purpose Summary

| Folder       | Purpose                                                                 |
|-------------|-------------------------------------------------------------------------|
| **config/**  | API keys, constants, LangGraph setup                                    |
| **core/**    | Graph building, memory management, intent classification, response synthesis |
| **nodes/**   | Individual LangGraph nodes (API, memory, decision, response)            |
| **tools/**   | API wrapper tools, utilities                                            |
| **data/**    | Runtime memory and sample data                                          |

---

## Typical Workflow

1. **User Input:** User submits a query via CLI (`main.py`) or Streamlit (`app.py`).  
2. **Intent Classification Node:** Determines query type (weather, crypto, flight, phone, etc.).  
3. **Decision Node:** Routes the query to the appropriate node.  
4. **Domain Node (API / Memory):** Executes API call or fetches from memory.  
5. **Response Node:** Synthesizes human-readable response using LLM.  
6. **Memory Storage:** Updates minimal memory (timestamp, user input, last response) for context and follow-ups.  
7. **Display:** Streamlit UI shows spinner while processing, then final response with chat history.

---

## Usage

### CLI Mode
```bash
python main.py
```
- Enter queries in console.
- Exit using exit, quit, or q.

### Streamlit Mode
```bash
streamlit run app.py
```
- Enter your question in the input box and click Send.
- Spinner shows during processing.
- Chat history is maintained for context-aware follow-ups.

---

## Example Queries

- **Weather:** What is the current temperature in Delhi

- **Crypto:** What is the current price of bitcoin

- **Flights:** Flights from Delhi to Mumbai on 8th November

- **Phone Verification:** Check this number +91xyxyxyxyxy

---


## Challenges & Learnings

- Handling context-aware follow-ups across multiple domains

- Integrating multiple third-party APIs in a modular workflow

- Maintaining session memory efficiently for follow-ups

- Designing a scalable node-based architecture

- Implementing real-time Streamlit UI and chat history

---

## Deliverables

- Functional LangGraph-based agent (Python files)
- Fully modular and documented codebase
- Streamlit interactive demo
- Sample memory dump