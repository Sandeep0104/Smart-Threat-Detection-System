"""
AI Security Analyst - Chat Router
Endpoints for conversational RAG chat with log data.
"""
from fastapi import APIRouter, HTTPException
from ..models.schemas import ChatRequest, ChatResponse, ChatMessage
from ..services.chat_service import chat_with_logs, get_chat_history, clear_chat_history
from ..services.vector_store import has_vector_store

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    """Send a message and get an AI-powered response based on log data."""
    if not req.analysis_id:
        raise HTTPException(400, "analysis_id is required. Upload and analyze logs first.")

    if not has_vector_store(req.analysis_id):
        raise HTTPException(404, "No log data found for this analysis. Please upload logs first.")

    response_text, sources = await chat_with_logs(req.analysis_id, req.message)

    return ChatResponse(
        response=response_text,
        sources=sources,
    )


@router.get("/history/{analysis_id}")
async def get_history(analysis_id: str):
    """Get conversation history for an analysis."""
    history = get_chat_history(analysis_id)
    return {"messages": [msg.model_dump() for msg in history]}


@router.delete("/history/{analysis_id}")
async def delete_history(analysis_id: str):
    """Clear conversation history for an analysis."""
    clear_chat_history(analysis_id)
    return {"status": "cleared"}
