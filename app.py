import time
import streamlit as st
from typing import List, Tuple

from core.graph_builder import SmartInfoAgent
from core.rag import index_documents, get_retriever_for_collection

# Page configuration
st.set_page_config(
    page_title="Smart Info Agent (RAG)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

    /* GLOBAL*/
    body {
        background-color: #f7f9fc !important;
        color: #1e293b;
        font-family: "Inter", sans-serif;
    }

    .main {
        background-color: #f7f9fc !important;
    }

    /* SIDEBAR (glass UI) */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #2563eb !important;
        font-weight: 700 !important;
    }

    /* Radio Buttons */
    .stRadio > label {
        font-weight: 600 !important;
        color: #475569 !important;
    }

    /* MAIN HEADER*/
    .chat-title {
        text-align: center;
        font-size: 34px;
        font-weight: 800;
        color: #1e40af;
        margin-top: 1rem;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }

    .subtext {
        text-align: center;
        color: #64748b;
        font-size: 16px;
        margin-bottom: 1rem;
    }

    /* MESSAGE BUBBLES*/

    /* Chat wrapper */
    div[data-testid="stChatMessage"] {
        padding: 1rem !important;
        border-radius: 14px !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }

    /* User bubble (right) */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatar"][aria-label='🧑‍💻']) {
        background: #e8f3ff !important;
        border: 1px solid #cde4ff !important;
    }

    /* Assistant bubble (left) */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatar"][aria-label='🤖']) {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
    }

    /* Avatar font size */
    .stChatMessageAvatar {
        font-size: 20px !important;
    }

    /* CHAT INPUT*/
    .stChatInputContainer {
        border-radius: 12px !important;
        border: 1px solid #d0d7e2 !important;
        background: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }

    /* BUTTONS (Modern)*/
    .stButton > button {
        background: #2563eb !important;
        color: white !important;
        padding: 0.6rem 1rem !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: 0.2s;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
    }

    .stButton > button:hover {
        background: #1d4ed8 !important;
        transform: scale(1.02);
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.4);
    }

    
    /* File Upload*/
    .uploadedFile {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* Alerts */
    .stAlert {
        border-radius: 10px !important;
    }
            
    [data-testid="stSidebar"] {
            background-color: #0F1117 !important;  /* pure dark sidebar */
        }

</style>
""", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.title("⚙️ Smart Info Agent Settings")
    st.markdown("### Select Mode:")
    chat_mode = st.radio(
        "Choose mode:",
        ["Smart Info Agent (Normal)", "Chat with Documents (RAG)"]
    )
    st.divider()

    if st.button("🧹 Clear Chat History"):
        st.session_state.clear()
        st.experimental_rerun()

# Session State Initialization
if "agent" not in st.session_state:
    st.session_state.agent = SmartInfoAgent(retriever=None)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "collection" not in st.session_state:
    st.session_state.collection = None
if "retriever" not in st.session_state:
    st.session_state.retriever = None

# RAG Upload UI
uploaded_files = None
if chat_mode == "Chat with Documents (RAG)":
    st.sidebar.markdown("#### Upload Documents or Images")

    uploaded_files = st.sidebar.file_uploader(
        "Upload Files",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "jpg", "jpeg", "png"]
    )

    if uploaded_files and st.sidebar.button("📥 Process Documents"):
        files: List[Tuple[str, bytes]] = []
        for f in uploaded_files:
            files.append((f.name, f.read()))

        with st.spinner("🔍 Indexing documents... This may take a few seconds."):
            try:
                # Supports OCR / images
                collection = index_documents(files, collection_name="session_docs")
                retriever = get_retriever_for_collection(collection, top_k=5)

                st.session_state.collection = collection
                st.session_state.retriever = retriever
                st.session_state.agent = SmartInfoAgent(retriever=retriever, rag_top_k=5)

                st.success(f"✅ Successfully indexed {len(files)} file(s). You can now chat with them!")
            except Exception as e:
                st.error(f"❌ Error while processing documents: {e}")

    if not st.session_state.collection:
        st.info("📄 Please upload and process documents to start RAG-based chatting.")

# Chat Header
st.markdown('<div class="chat-title">🤖 Smart Info Agent</div>', unsafe_allow_html=True)

mode_subtext = (
    "📚 Document Chat Mode Enabled (RAG)"
    if chat_mode == "Chat with Documents (RAG)"
    else "💡 Normal Assistant Mode"
)
st.markdown(f'<div class="subtext">{mode_subtext}</div>', unsafe_allow_html=True)
st.markdown("---")

# Display Chat History
for msg in st.session_state.messages:
    role, content = msg["role"], msg["content"]
    with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🤖"):
        st.markdown(content)

# Chat Input
prompt = st.chat_input(
    "Ask something (e.g., 'Weather in Delhi' or 'What does the document say about pricing?')"
)

if prompt:
    # Show user message
    st.chat_message("user", avatar="🧑‍💻").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Thinking..."):
            start = time.time()
            try:
                response = st.session_state.agent.run(prompt)
            except Exception as e:
                response = f"⚠️ Error during response generation:\n\n{e}"
            end = time.time()

            st.markdown(response)
            st.caption(f"⏱️ Responded in {end - start:.2f}s")

    # Save response
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.caption("💡 Tip: Upload a contract, report, or image and ask: 'Summarize the pricing details.'")