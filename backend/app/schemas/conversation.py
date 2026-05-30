"""Conversation DTOs."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.qa import CitationOut


class ConversationCreate(BaseModel):
    title: str | None = None
    topic_id: uuid.UUID | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    document_ids: list[uuid.UUID] | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationOut]


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str | None = None
    topic_id: uuid.UUID | None = None
    created_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    citations: list | None = None
    created_at: datetime
