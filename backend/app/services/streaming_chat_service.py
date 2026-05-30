"""Streaming chat — token-by-token answers with optional 'thinking' steps.

A focused linear pipeline (retrieve → optional web → optional thinking → answer) optimised
for streaming UX. The full critic-loop multi-agent graph remains the non-streaming path.
"""

import uuid
from collections.abc import AsyncIterator

from langchain_core.language_models import BaseChatModel
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.agents import prompts
from app.agents.nodes import RetrieverFactory, build_citations, format_evidence
from app.agents.state import EvidenceItem
from app.agents.web import WebSearch
from app.core.llm import stream_chat
from app.repositories.conversation_repository import ConversationRepository


class StreamingChatService:
    def __init__(
        self,
        make_retriever: RetrieverFactory,
        chat_model: BaseChatModel,
        web_search: WebSearch | None,
        sessionmaker: async_sessionmaker,
    ) -> None:
        self._make_retriever = make_retriever
        self._model = chat_model
        self._web = web_search
        self._sessionmaker = sessionmaker

    async def stream(
        self,
        conversation_id: uuid.UUID,
        message: str,
        *,
        collection: str | None,
        thinking: bool = False,
    ) -> AsyncIterator[dict]:
        evidence: list[EvidenceItem] = []

        retriever = self._make_retriever(collection)
        if retriever is not None:
            chunks = await retriever.retrieve(message)
            evidence += [
                EvidenceItem(
                    content=c.content,
                    document_id=c.document_id,
                    document_title=c.document_title,
                    page=c.page,
                    url=c.cloudinary_url,
                    source="documents",
                )
                for c in chunks
            ]
        # No topic attached → fall back to live web research.
        if collection is None and self._web is not None:
            evidence += list(await self._web.search(message))

        yield {"type": "evidence", "count": len(evidence)}
        evidence_str = format_evidence(evidence)

        if thinking:
            prompt = prompts.THINKING.format(question=message, evidence=evidence_str)
            async for token in stream_chat(self._model, prompt):
                yield {"type": "thinking", "token": token}

        parts: list[str] = []
        prompt = prompts.STREAM_ANSWER.format(question=message, evidence=evidence_str)
        async for token in stream_chat(self._model, prompt):
            parts.append(token)
            yield {"type": "token", "token": token}

        answer = "".join(parts).strip()
        citations = [dict(c) for c in build_citations(evidence)]
        yield {"type": "citations", "citations": citations}

        async with self._sessionmaker() as session:
            repo = ConversationRepository(session)
            await repo.add_message(conversation_id, role="user", content=message)
            await repo.add_message(
                conversation_id, role="assistant", content=answer, citations=citations
            )
            await session.commit()

        yield {"type": "done"}
