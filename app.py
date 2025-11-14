import os
import io
import time
import streamlit as st
from typing import List, Tuple

from core.graph_builder import SmartInfoAgent
from core.rag import index_documents, get_retriever_for_collection
from config import settings

# Page configuration
st.set_page_config(
    page_title="Smart Info Agent (RAG)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
                # Now supports OCR and image-based documents
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
        font-size: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
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
if prompt := st.chat_input("Ask something (e.g., 'Weather in Delhi' or 'What does the document say about pricing?')"):
    # Display user message instantly
    st.chat_message("user", avatar="🧑‍💻").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Run agent (either normal or RAG mode)
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

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.caption("💡 Tip: Try uploading a contract, report, or image of a document and ask, 'Summarize the key points about pricing.'")
