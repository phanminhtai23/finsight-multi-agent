"""Conversation endpoints (basic CRUD; agent chat arrives in M2)."""

import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import AgentServiceDep, ConversationRepoDep
from app.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationOut,
    MessageOut,
)
from app.schemas.qa import CitationOut

router = APIRouter()


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conversation(
    body: ConversationCreate, repo: ConversationRepoDep
) -> ConversationOut:
    conversation = await repo.create(title=body.title)
    return ConversationOut.model_validate(conversation)


@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def post_message(
    conversation_id: uuid.UUID,
    body: ChatRequest,
    repo: ConversationRepoDep,
    agents: AgentServiceDep,
) -> ChatResponse:
    """Send a message; the multi-agent graph answers with grounded citations."""
    if await repo.get(conversation_id) is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    doc_ids = [str(d) for d in body.document_ids] if body.document_ids else None
    answer, citations = await agents.chat(conversation_id, body.message, document_ids=doc_ids)
    return ChatResponse(answer=answer, citations=[CitationOut(**c) for c in citations])


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(conversation_id: uuid.UUID, repo: ConversationRepoDep) -> list[MessageOut]:
    conversation = await repo.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [MessageOut.model_validate(m) for m in await repo.list_messages(conversation_id)]
