"""Conversation endpoints (basic CRUD; agent chat arrives in M2)."""

import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import ConversationRepoDep
from app.schemas.conversation import ConversationCreate, ConversationOut, MessageOut

router = APIRouter()


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conversation(
    body: ConversationCreate, repo: ConversationRepoDep
) -> ConversationOut:
    conversation = await repo.create(title=body.title)
    return ConversationOut.model_validate(conversation)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(conversation_id: uuid.UUID, repo: ConversationRepoDep) -> list[MessageOut]:
    conversation = await repo.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [MessageOut.model_validate(m) for m in await repo.list_messages(conversation_id)]
