import os
from typing import List, Tuple
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from core.utils import parse_pdf, parse_docx, chunk_text, extract_text_from_image_bytes
from config import settings as ChromaSettings
from dotenv import load_dotenv

load_dotenv()

HuggingFace_Auth_Token = ChromaSettings.HUGGINGFACE_API_KEY

# Create Chroma Cloud Vector Store
def create_chroma_vectorstore(collection_name: str = "documents"):
    """
    Create and return a Chroma Cloud vector store (LangChain wrapper)
    using the credentials defined in config.settings.
    """

    api_key = ChromaSettings.CHROMA_API_KEY
    tenant = ChromaSettings.CHROMA_TENANT
    database = ChromaSettings.CHROMA_DATABASE

    if not all([api_key, tenant, database]):
        raise ValueError("❌ Missing Chroma Cloud credentials. Please set CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE.")

    print("🌩️ Connecting to Chroma Cloud...")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"token": HuggingFace_Auth_Token},)

    try:
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            chroma_cloud_api_key=api_key,
            tenant=tenant,
            database=database,
        )
        print("✅ Connected to Chroma Cloud successfully.")
        return vector_store
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Chroma Cloud vector store: {e}")


# Index and embed uploaded documents
def index_documents(
    docs: List[Tuple[str, bytes]],  # list of (filename, file_bytes)
    collection_name: str = "documents",
    chunk_size: int = 1000,
    overlap: int = 200,
):
    """
    Parses uploaded files (PDF/DOCX/Image/TXT), splits them into chunks,
    creates embeddings using a HuggingFace model,
    and stores them in a Chroma Cloud collection.
    """

    # STEP 1: Connect / Create Chroma Collection 
    print(f"\n🌐 Initializing Chroma Cloud vector store for collection '{collection_name}'...")
    vector_store = create_chroma_vectorstore(collection_name)
    print("✅ Vector store ready for indexing.\n")

    # Lists to hold extracted text data and metadata for each chunk
    docs_texts, metadatas, ids = [], [], []

    # STEP 2: Parse Uploaded Files 
    print("📄 Starting document parsing and preprocessing...")
    for i, (fname, fbytes) in enumerate(docs):
        print(f"➡️ Processing file: {fname}")
        text = ""

        # Detect file type and extract text accordingly
        fname_lower = fname.lower()
        if fname_lower.endswith(".pdf"):
            print("   📘 Detected PDF — extracting text...")
            text = parse_pdf(fbytes)
        elif fname_lower.endswith(".docx"):
            print("   📄 Detected DOCX — extracting text...")
            text = parse_docx(fbytes)
        elif fname_lower.endswith((".jpg", ".jpeg", ".png")):
            print("   🖼️ Detected Image — extracting text via OCR...")
            text = extract_text_from_image_bytes(fbytes)
        else:
            # Fallback for plain text or unknown file types
            print("   📜 Detected Text/Other — attempting UTF-8 decode...")
            try:
                text = fbytes.decode("utf-8")
            except Exception:
                text = ""

        # Skip files with no extracted text
        if not text.strip():
            print(f"   ⚠️ No text extracted from {fname}. Skipping this file.\n")
            continue

        # STEP 3: Split Text into Chunks 
        print(f"   ✂️ Splitting text into chunks (size={chunk_size}, overlap={overlap})...")
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        print(f"   🧩 Created {len(chunks)} chunks from '{fname}'.")

        # Collect all chunks and related metadata
        for j, chunk in enumerate(chunks):
            docs_texts.append(chunk)
            metadatas.append({"source": fname, "chunk": j})
            ids.append(f"{i}_{j}")

    # STEP 4: Check for Valid Text Data 
    if not docs_texts:
        print("⚠️ No valid text extracted from any uploaded documents. Nothing to index.")
        return vector_store

    # STEP 5: Add Chunks to Chroma Cloud 
    print("\n🚀 Uploading text embeddings to Chroma Cloud...")
    try:
        vector_store.add_texts(texts=docs_texts, metadatas=metadatas, ids=ids)
        print(f"✅ Successfully indexed {len(docs_texts)} text chunks into Chroma Cloud collection '{collection_name}'.")
        return vector_store

    except Exception as e:
        print("❌ Failed to embed or index documents in Chroma Cloud.")
        raise RuntimeError(f"❌ Embedding or indexing failed: {e}")



# Retriever interface
def get_retriever_for_collection(vector_store, top_k: int = 5):
    """
    Returns a retriever function that searches the most relevant
    chunks from the Chroma Cloud collection for a given query.
    """
    def retriever(query: str, k: int = top_k):
        if not query.strip():
            return []

        try:
            results = vector_store.similarity_search_with_score(query, k=k)
            # Each result is (Document, score)
            formatted = [
                (doc.page_content, doc.metadata, score)
                for doc, score in results
            ]
            return formatted
        except Exception as e:
            print(f"❌ Retrieval failed: {e}")
            return []

    return retriever
