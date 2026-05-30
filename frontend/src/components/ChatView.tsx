import { useEffect, useRef, useState } from "react";
import { api, streamChat } from "../lib/api";
import type { Citation, Message } from "../lib/types";
import { Button, Spinner } from "./ui";

interface LocalMsg {
  role: string;
  content: string;
  citations?: Citation[];
  thinking?: string;
}

function Sources({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;
  return (
    <div className="mt-3 border-t border-neutral-200 pt-2 dark:border-neutral-800">
      <div className="mb-1 text-xs font-medium text-neutral-400">Sources</div>
      <ul className="space-y-1 text-xs">
        {citations.map((c) => (
          <li key={c.index} className="text-neutral-500">
            <span className="text-indigo-600">[{c.index}]</span>{" "}
            {c.url ? (
              <a href={c.url} target="_blank" className="hover:underline">
                {c.document_title ?? c.url}
              </a>
            ) : (
              (c.document_title ?? c.document_id)
            )}
            {c.page != null && <span className="text-neutral-400"> · p.{c.page}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}

function Thinking({ text }: { text: string }) {
  return (
    <details className="mb-2 rounded-lg bg-neutral-100 px-3 py-2 text-sm dark:bg-neutral-800/60">
      <summary className="cursor-pointer text-xs font-medium text-neutral-500">
        💭 Thinking
      </summary>
      <p className="mt-2 whitespace-pre-wrap text-neutral-600 dark:text-neutral-400">{text}</p>
    </details>
  );
}

export function ChatView({ conversationId }: { conversationId: string }) {
  const [messages, setMessages] = useState<LocalMsg[]>([]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [liveThinking, setLiveThinking] = useState("");
  const [liveAnswer, setLiveAnswer] = useState("");
  const [elapsed, setElapsed] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<number | null>(null);

  function stopTimer() {
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }
  useEffect(() => stopTimer, []);

  useEffect(() => {
    api.get<Message[]>(`/conversations/${conversationId}/messages`).then((r) =>
      setMessages(
        r.data.map((m) => ({ role: m.role, content: m.content, citations: m.citations ?? undefined })),
      ),
    );
    setLiveThinking("");
    setLiveAnswer("");
  }, [conversationId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, liveAnswer, liveThinking]);

  async function send() {
    const msg = input.trim();
    if (!msg || streaming) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: msg }]);
    setStreaming(true);
    setLiveThinking("");
    setLiveAnswer("");
    setElapsed(0);
    const start = Date.now();
    timerRef.current = window.setInterval(() => setElapsed((Date.now() - start) / 1000), 100);

    let answer = "";
    let think = "";
    let cites: Citation[] = [];
    try {
      await streamChat(conversationId, msg, thinking, (ev) => {
        if (ev.type === "thinking") setLiveThinking((think += ev.token));
        else if (ev.type === "token") setLiveAnswer((answer += ev.token));
        else if (ev.type === "citations") cites = ev.citations;
      });
    } catch {
      answer = answer || "⚠️ Streaming failed.";
    }
    stopTimer();
    setMessages((m) => [
      ...m,
      { role: "assistant", content: answer, citations: cites, thinking: think || undefined },
    ]);
    setLiveThinking("");
    setLiveAnswer("");
    setStreaming(false);
  }

  return (
    <div className="flex h-full flex-col">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-4 py-6">
        <div className="mx-auto max-w-2xl space-y-4">
          {messages.length === 0 && !streaming && (
            <p className="pt-20 text-center text-sm text-neutral-400">
              Ask anything about this topic's documents — or the live web.
            </p>
          )}
          {messages.map((m, i) =>
            m.role === "user" ? (
              <div key={i} className="flex justify-end">
                <div className="max-w-[85%] rounded-2xl bg-indigo-600 px-4 py-2 text-white">
                  {m.content}
                </div>
              </div>
            ) : (
              <div key={i} className="max-w-[90%]">
                {m.thinking && <Thinking text={m.thinking} />}
                <div className="whitespace-pre-wrap rounded-2xl bg-neutral-100 px-4 py-3 dark:bg-neutral-800">
                  {m.content}
                  {m.citations && <Sources citations={m.citations} />}
                </div>
              </div>
            ),
          )}

          {streaming && (
            <div className="max-w-[90%]">
              <div className="mb-2 flex items-center gap-2 text-xs text-neutral-400">
                <Spinner className="h-3.5 w-3.5" />
                <span>
                  {liveAnswer ? "Generating" : liveThinking ? "Thinking" : "Researching"}…
                </span>
                <span className="font-mono tabular-nums text-neutral-500">
                  {elapsed.toFixed(1)}s
                </span>
              </div>
              {liveThinking && (
                <div className="mb-2 rounded-lg bg-neutral-100 px-3 py-2 text-sm dark:bg-neutral-800/60">
                  <div className="text-xs font-medium text-neutral-500">💭 Thinking…</div>
                  <p className="mt-1 whitespace-pre-wrap text-neutral-600 dark:text-neutral-400">
                    {liveThinking}
                  </p>
                </div>
              )}
              {liveAnswer && (
                <div className="whitespace-pre-wrap rounded-2xl bg-neutral-100 px-4 py-3 dark:bg-neutral-800">
                  {liveAnswer}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="border-t border-neutral-200 p-3 dark:border-neutral-800">
        <div className="mx-auto flex max-w-2xl items-end gap-2">
          <label className="flex select-none items-center gap-1 text-xs text-neutral-500">
            <input
              type="checkbox"
              checked={thinking}
              onChange={(e) => setThinking(e.target.checked)}
            />
            Thinking
          </label>
          <textarea
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Send a message…"
            className="max-h-40 flex-1 resize-none rounded-xl border border-neutral-300 bg-white px-3 py-2 text-sm outline-none focus:border-indigo-500 dark:border-neutral-700 dark:bg-neutral-900"
          />
          <Button onClick={send} disabled={streaming || !input.trim()}>
            {streaming ? "…" : "Send"}
          </Button>
        </div>
      </div>
    </div>
  );
}
