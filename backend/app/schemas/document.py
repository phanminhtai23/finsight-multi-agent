"""Document DTOs."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    file_type: str
    company: str | None = None
    fiscal_period: str | None = None
    cloudinary_url: str | None = None
    status: str
    page_count: int | None = None
    error: str | None = None
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentOut
    task_id: uuid.UUID
