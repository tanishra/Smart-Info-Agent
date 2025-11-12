# 🤖 Smart Info Agent

## 📘 Overview

**Smart Info Agent** is a modular **LangGraph-based intelligent assistant** that interacts with multiple real-time APIs, maintains conversational context, and provides clear, human-readable answers to diverse user queries.  

It demonstrates **modern AI workflow design** concepts using **LangGraph**, **Azure OpenAI**, and **Streamlit**, making it an ideal project for training and educational purposes.

This system showcases:
- Multi-node, tool-based architecture  
- Modular workflow design  
- Memory and context management  
- Integration with real-time APIs  
- Intent classification and natural response generation  
- Seamless UI integration via Streamlit  

---

## 🚀 Key Features

### 🔹 Multi-Domain Query Support
Handles live data from multiple APIs:
| Domain | API Used | Example Query |
|--------|-----------|----------------|
| 🌦️ **Weather** | Weather Stack API | “Weather in Delhi” |
| 💰 **Crypto** | CoinMarket API | “Bitcoin price today” |
| ✈️ **Flights** | Amadeus API | “Flights from Delhi to Mumbai on 21 Nov” |
| 📞 **Phone Verification** | Numverify API | “Verify +919690190921” |

---

### 🔹 Context-Aware Follow-Ups
The agent remembers context for follow-up queries:
- “Temperature in Delhi” → “Compare with Mumbai”  
- “Bitcoin price” → “Compare with Ethereum”  

---

### 🔹 Modular LangGraph Nodes
Each function (LLM, tool execution, decision logic) is encapsulated in its own **LangGraph node**, enabling:
- Easy debugging  
- Independent testing  
- Scalable design  

---

### 🔹 Real-Time API Integration via Tools
Each tool (e.g., `get_weather_info`, `get_crypto_price`) wraps around an external API and returns structured JSON, which is processed and summarized naturally by the agent.

---

### 🔹 Efficient Memory Management
Stores minimal conversational data:
- User query  
- LLM response  
- Timestamp  

Memory is handled via a lightweight `MemoryStore` class that can be reset anytime.

---

### 🔹 Natural, Human-Like Responses
Uses **Azure OpenAI (Chat model)** to:
- Classify intent  
- Choose relevant tools  
- Summarize API outputs  
- Respond in friendly, concise language  

---

### 🔹 Interactive Streamlit UI
Beautiful and responsive web interface:
- Live chat layout  
- Spinners during processing  
- Persistent chat history  
- Clear chat/reset options  
- Role-based message styling  

---

### 🔹 Extensible & Maintainable Architecture
Easily extendable by:
- Adding a new **tool** (API wrapper)  
- Adding a new **LangGraph node**  
- Registering the node in the workflow  

---

## 🧩 Tech Stack

| Category | Tool / Library | Purpose |
|-----------|----------------|----------|
| **LLM** | Azure OpenAI (Chat) | Query understanding and response synthesis |
| **Workflow Engine** | LangGraph | Building node-based agent graphs |
| **Framework** | LangChain | Message handling, tool invocation |
| **APIs** | Amadeus, CoinMarket, WeatherStack, Numverify | Real-time data sources |
| **UI** | Streamlit | Interactive web chat interface |
| **Utility** | Requests, Datetime, JSON | API calls and data handling |
| **Tracking** | LangSmith | Tracing and monitoring LLM calls |

---

## 🧱 Folder Structure

| Folder | Description |
|---------|--------------|
| **config/** | API keys, constants, and Azure model setup |
| **core/** | LangGraph agent, memory store, and workflow logic |
| **tools/** | Individual API integration tools |
| **data/** | Memory dumps, logs, and test data |
| **main.py** | CLI entry point |
| **app.py** | Streamlit UI app |
| **README.md** | Project documentation |

---

## ⚙️ Workflow Overview

1. **User Input** → via CLI or Streamlit UI  
2. **LLM Node** → Interprets intent and decides tool usage  
3. **Tool Node** → Executes the corresponding API call  
4. **Decision Node** → Determines if more tools are needed  
5. **Response Node** → Summarizes and delivers result  
6. **Memory Store** → Updates with latest query and response  
7. **UI Display** → Shows formatted answer in chat interface  

---

## 💻 Usage Instructions

### ▶️ CLI Mode

Run the interactive command-line interface:
```bash
python main.py
```
#### Commands:
- **exit, quit, q** → End session
- **history, logs** → Show chat history
- **clear, reset** → Clear memory

---

## 🌐 Streamlit Web App
Launch the web-based chat interface:
```bash
streamlit run app.py
```

Then open the local URL (usually http://localhost:8501) in your browser.

#### Features:
- Enter queries in chat input
- View responses in formatted chat bubbles
- Clear chat history with one click
- Observe real-time response timing

--- 

## 🧠 Learnings & Takeaways
- How to design context-aware AI agents
- How to build modular, graph-based workflows using LangGraph
- Integrating multiple APIs efficiently
- Managing memory and context for better user experience
- Deploying interactive LLM interfaces using Streamlit
- Structuring projects for scalability and maintainability

---

## 🧩 Extending the Agent
To add a new capability:
- Create a new tool function inside tools/ (e.g., tools/news_tool.py).
- Add it to the tools list in core/graph_builder.py.
- Update the system prompt with its usage rule.
- Optionally, extend the Streamlit UI for specialized display.

---

## 🤝 Contributions
Feel free to contribute! Here’s how you can help improve Smart Info Agent:
- Fork the repository and create your own branch.
- Commit your changes with clear, descriptive messages.
- Test your updates thoroughly (both CLI and Streamlit modes).
- Submit a Pull Request explaining what feature or fix you added.


