"""Chunk model — an indexed slice of a document with citation metadata."""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.models.base import Base, TimestampMixin, UUIDMixin

EMBEDDING_DIM = get_settings().embedding_dim


class Chunk(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    # Parent-child (small-to-big): child chunks reference the larger parent returned to the LLM.
    parent_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("chunks.id", ondelete="CASCADE"), default=None
    )

    content: Mapped[str]
    # Anthropic-style contextual retrieval: content prefixed with an LLM-written context line.
    contextualized_content: Mapped[str | None] = mapped_column(default=None)

    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    # Generated full-text vector for hybrid (keyword) search.
    tsv: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', coalesce(content, ''))", persisted=True),
    )

    # Citation / filtering metadata.
    page: Mapped[int | None] = mapped_column(default=None)
    bbox: Mapped[dict | None] = mapped_column(JSONB, default=None)
    section_title: Mapped[str | None] = mapped_column(default=None)
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, default=None)

    document: Mapped["Document"] = relationship(back_populates="chunks")  # noqa: F821
