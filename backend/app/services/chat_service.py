"""
AI Security Analyst - Chat Service
RAG-based conversational interface to query log data using Ollama.
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from ..services import vector_store as vs
from ..models.schemas import ChatMessage
from ..config import settings


# In-memory chat history per analysis_id
_chat_histories: dict[str, list[ChatMessage]] = {}


CHAT_SYSTEM_PROMPT = """You are a cybersecurity analyst AI assistant helping a small business owner understand their server logs.

You have access to relevant log entries that were retrieved based on the user's question.
Use these log entries to provide accurate, evidence-based answers.

Rules:
1. Always reference specific log entries when answering
2. Explain technical terms in simple language
3. If the logs don't contain the answer, say so honestly
4. Provide actionable advice when relevant
5. Be concise but thorough
6. Use bullet points and formatting for readability

Retrieved Log Entries:
{context}

Previous conversation for context (if any):
{chat_history}"""


CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", CHAT_SYSTEM_PROMPT),
    ("human", "{question}"),
])


def _get_llm() -> ChatOllama:
    """Get an Ollama LLM instance for chat."""
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=0.4,
    )


async def chat_with_logs(
    analysis_id: str,
    message: str,
) -> tuple[str, list[str]]:
    """
    Chat with the log data using RAG.
    Returns (response_text, source_entries).
    """
    # Search for relevant log entries
    sources = await vs.search_logs(analysis_id, message, k=5)
    context = "\n\n".join(sources) if sources else "No relevant log entries found for this query."

    # Get chat history
    history = _chat_histories.get(analysis_id, [])
    history_text = ""
    if history:
        recent = history[-10:]  # Last 10 messages
        history_parts = []
        for msg in recent:
            role = "User" if msg.role == "user" else "Assistant"
            history_parts.append(f"{role}: {msg.content}")
        history_text = "\n".join(history_parts)

    try:
        llm = _get_llm()
        chain = CHAT_PROMPT | llm

        response = await chain.ainvoke({
            "context": context,
            "chat_history": history_text,
            "question": message,
        })

        response_text = response.content
    except Exception as e:
        # Fallback without AI
        response_text = _generate_fallback_response(message, sources)

    # Update chat history
    if analysis_id not in _chat_histories:
        _chat_histories[analysis_id] = []

    _chat_histories[analysis_id].append(ChatMessage(role="user", content=message))
    _chat_histories[analysis_id].append(ChatMessage(role="assistant", content=response_text))

    # Limit history size
    if len(_chat_histories[analysis_id]) > 50:
        _chat_histories[analysis_id] = _chat_histories[analysis_id][-20:]

    return response_text, sources


def get_chat_history(analysis_id: str) -> list[ChatMessage]:
    """Get chat history for an analysis."""
    return _chat_histories.get(analysis_id, [])


def clear_chat_history(analysis_id: str) -> None:
    """Clear chat history for an analysis."""
    if analysis_id in _chat_histories:
        del _chat_histories[analysis_id]


def _generate_fallback_response(message: str, sources: list[str]) -> str:
    """Generate a response when Ollama is not available."""
    if not sources:
        return (
            "I couldn't find any relevant log entries for your question. "
            "Please make sure you've uploaded and analyzed logs first.\n\n"
            "**Tip:** Start Ollama with `ollama serve` for AI-powered responses."
        )

    response = "Here are the relevant log entries I found:\n\n"
    for i, source in enumerate(sources, 1):
        response += f"**Entry {i}:**\n```\n{source}\n```\n\n"

    response += (
        "\n> **Note:** For intelligent analysis, start Ollama with `ollama serve` "
        "and ensure the model is pulled: `ollama pull llama3.2`"
    )
    return response
