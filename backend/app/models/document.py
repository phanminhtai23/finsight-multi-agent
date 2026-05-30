"""Document model — a user-uploaded source file (PDF / DOCX / image)."""

import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class DocumentStatus(str, enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    user_id: Mapped[uuid.UUID | None] = mapped_column(default=None, index=True)
    title: Mapped[str]
    file_type: Mapped[str]
    company: Mapped[str | None] = mapped_column(default=None, index=True)
    fiscal_period: Mapped[str | None] = mapped_column(default=None)

    cloudinary_public_id: Mapped[str | None] = mapped_column(default=None)
    cloudinary_url: Mapped[str | None] = mapped_column(default=None)

    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus, name="document_status"), default=DocumentStatus.PROCESSING
    )
    page_count: Mapped[int | None] = mapped_column(default=None)
    error: Mapped[str | None] = mapped_column(default=None)

    chunks: Mapped[list["Chunk"]] = relationship(  # noqa: F821
        back_populates="document", cascade="all, delete-orphan"
    )
