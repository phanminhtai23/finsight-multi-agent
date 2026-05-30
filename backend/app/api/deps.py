"""FastAPI dependency wiring (composition root).

Keeps routers thin: they declare the service they need and the container builds it from a
request-scoped session plus the configured providers (Postgres for relational data, Qdrant
for vectors).
"""

from collections.abc import AsyncIterator
from typing import Annotated

import redis.asyncio as redis
from arq.connections import ArqRedis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import build_graph
from app.core.cache import create_redis_pool
from app.core.checkpointer import get_checkpointer
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.core.llm import get_embedder, get_text_generator
from app.core.qdrant import get_qdrant_client
from app.core.queue import get_arq_pool
from app.rag.indexing.qdrant_store import QdrantVectorStore
from app.rag.retrieval.hybrid import HybridRetriever
from app.rag.retrieval.qdrant_backend import QdrantSearchBackend
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.task_repository import TaskRepository
from app.services.agent_service import AgentService
from app.services.events import EventPublisher
from app.services.ingestion_service import IngestionService
from app.services.qa_service import QAService

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_redis_client(settings: SettingsDep) -> AsyncIterator[redis.Redis]:
    client = create_redis_pool(settings)
    try:
        yield client
    finally:
        await client.aclose()


RedisDep = Annotated[redis.Redis, Depends(get_redis_client)]
ArqDep = Annotated[ArqRedis, Depends(get_arq_pool)]


def get_document_repo(session: SessionDep) -> DocumentRepository:
    return DocumentRepository(session)


def get_conversation_repo(session: SessionDep) -> ConversationRepository:
    return ConversationRepository(session)


def get_task_repo(session: SessionDep) -> TaskRepository:
    return TaskRepository(session)


DocumentRepoDep = Annotated[DocumentRepository, Depends(get_document_repo)]
ConversationRepoDep = Annotated[ConversationRepository, Depends(get_conversation_repo)]
TaskRepoDep = Annotated[TaskRepository, Depends(get_task_repo)]


def get_event_publisher(redis_client: RedisDep) -> EventPublisher:
    return EventPublisher(redis_client)


EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]


def get_vector_store() -> QdrantVectorStore:
    settings = get_settings()
    return QdrantVectorStore(
        get_qdrant_client(settings),
        collection=settings.qdrant_collection,
        dim=settings.embedding_dim,
    )


def get_qa_service() -> QAService:
    settings = get_settings()
    backend = QdrantSearchBackend(
        get_qdrant_client(settings), collection=settings.qdrant_collection
    )
    retriever = HybridRetriever(backend, get_embedder())
    return QAService(retriever, get_text_generator())


def get_ingestion_service(document_repo: DocumentRepoDep) -> IngestionService:
    return IngestionService(
        document_repo=document_repo,
        vector_store=get_vector_store(),
        embedder=get_embedder(),
        text_generator=get_text_generator(),
    )


QAServiceDep = Annotated[QAService, Depends(get_qa_service)]
IngestionServiceDep = Annotated[IngestionService, Depends(get_ingestion_service)]


# The compiled multi-agent graph is stateless (the checkpointer holds per-thread state),
# so it is built once and shared across requests.
_compiled_graph: object | None = None


async def get_compiled_graph() -> object:
    global _compiled_graph
    if _compiled_graph is None:
        settings = get_settings()
        backend = QdrantSearchBackend(
            get_qdrant_client(settings), collection=settings.qdrant_collection
        )
        retriever = HybridRetriever(backend, get_embedder())
        checkpointer = await get_checkpointer(settings)
        _compiled_graph = build_graph(retriever, get_text_generator(), checkpointer=checkpointer)
    return _compiled_graph


async def get_agent_service(conversation_repo: ConversationRepoDep) -> AgentService:
    return AgentService(await get_compiled_graph(), conversation_repo)


AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]
