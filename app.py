import streamlit as st
import time
from core.graph_builder import SmartInfoAgent
from core.memory_store import MemoryStore

# Page configuration
st.set_page_config(
    page_title="Smart Info Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Initialization
if "agent" not in st.session_state:
    st.session_state.agent = SmartInfoAgent()
if "memory" not in st.session_state:
    st.session_state.memory = MemoryStore()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Smart Info Agent Settings")
    st.markdown("Ask about:")
    st.markdown("- 🌦️ Weather\n- 💰 Crypto Prices\n- ✈️ Flights\n- 📞 Phone Verification")
    st.divider()

    if st.button("🧹 Clear Chat History"):
        st.session_state.memory.clear()
        st.session_state.messages = []
        st.success("Chat history cleared!")

    st.caption("Built with ❤️ using LangChain + AzureOpenAI")

# Chat UI Header
st.markdown(
    """
    <style>
    .chat-title {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: #00BFFF;
        margin-bottom: 0.5rem;
    }
    .subtext {
        text-align: center;
        color: gray;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown('<div class="chat-title">🤖 Smart Info Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">Your AI assistant for live data queries</div>', unsafe_allow_html=True)
st.markdown("---")

# Display Chat History
for msg in st.session_state.messages:
    role, content = msg["role"], msg["content"]
    with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🤖"):
        st.markdown(content)

# User Input
if prompt := st.chat_input("Ask something (e.g., 'Weather in Delhi', 'Bitcoin price', 'Flights from Delhi to Mumbai on 21 Nov')"):
    # Display user message instantly
    st.chat_message("user", avatar="🧑‍💻").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response after spinner
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Thinking..."):
            start = time.time()
            response = st.session_state.agent.run(prompt)
            end = time.time()
            st.markdown(response)
            st.caption(f"⏱️ Responded in {end - start:.2f}s")

    # Save response to history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.caption("💡 Tip: Try 'Flights from Delhi to Mumbai on 21 November' or 'Verify +919690190921'")
