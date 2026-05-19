"""
AI Security Analyst - FAISS Vector Store Service
Manages log embedding and similarity search for the RAG chat feature.
"""
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from ..models.schemas import LogEntry
from ..config import settings


# Global vector store instances keyed by analysis_id
_vector_stores: dict[str, FAISS] = {}

# Use a local embedding model (no API key needed)
_embeddings = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Get or create the embeddings model (lazy-loaded)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def _entries_to_documents(entries: list[LogEntry]) -> list[Document]:
    """Convert log entries into LangChain Documents for embedding."""
    documents = []
    # Group entries into chunks of 5 for better context
    chunk_size = 5
    for i in range(0, len(entries), chunk_size):
        chunk = entries[i:i + chunk_size]
        content_parts = []
        for entry in chunk:
            parts = []
            if entry.timestamp:
                parts.append(f"Time: {entry.timestamp}")
            if entry.source_ip:
                parts.append(f"IP: {entry.source_ip}")
            if entry.username:
                parts.append(f"User: {entry.username}")
            if entry.action:
                parts.append(f"Action: {entry.action}")
            if entry.service:
                parts.append(f"Service: {entry.service}")
            parts.append(f"Message: {entry.message}")
            parts.append(f"Severity: {entry.severity.value}")
            content_parts.append(" | ".join(parts))

        content = "\n".join(content_parts)
        metadata = {
            "line_start": chunk[0].line_number,
            "line_end": chunk[-1].line_number,
            "has_threat": any(e.severity.value in ("critical", "high", "medium") for e in chunk),
        }
        documents.append(Document(page_content=content, metadata=metadata))

    return documents


async def ingest_logs(analysis_id: str, entries: list[LogEntry]) -> int:
    """Ingest parsed log entries into a FAISS vector store."""
    documents = _entries_to_documents(entries)

    if not documents:
        return 0

    embeddings = _get_embeddings()

    # Create FAISS index from documents
    vector_store = FAISS.from_documents(documents, embeddings)

    # Save to disk
    store_path = os.path.join(settings.VECTOR_STORE_DIR, analysis_id)
    vector_store.save_local(store_path)

    # Cache in memory
    _vector_stores[analysis_id] = vector_store

    return len(documents)


async def search_logs(
    analysis_id: str,
    query: str,
    k: int = 5,
) -> list[str]:
    """Search for relevant log entries matching a query."""
    vector_store = _get_vector_store(analysis_id)
    if not vector_store:
        return []

    results = vector_store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]


def _get_vector_store(analysis_id: str) -> FAISS | None:
    """Get a vector store by analysis_id (from cache or disk)."""
    if analysis_id in _vector_stores:
        return _vector_stores[analysis_id]

    # Try loading from disk
    store_path = os.path.join(settings.VECTOR_STORE_DIR, analysis_id)
    if os.path.exists(store_path):
        try:
            embeddings = _get_embeddings()
            vector_store = FAISS.load_local(
                store_path,
                embeddings,
                allow_dangerous_deserialization=True
            )
            _vector_stores[analysis_id] = vector_store
            return vector_store
        except Exception:
            pass

    return None


def has_vector_store(analysis_id: str) -> bool:
    """Check if a vector store exists for the given analysis_id."""
    if analysis_id in _vector_stores:
        return True
    store_path = os.path.join(settings.VECTOR_STORE_DIR, analysis_id)
    return os.path.exists(store_path)
