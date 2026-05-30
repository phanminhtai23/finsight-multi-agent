import { useEffect, useRef, useState } from "react";
import { api } from "../lib/api";
import type { Conversation, Topic } from "../lib/types";
import { useAuth } from "../context/AuthContext";
import { Logo } from "./Logo";
import { ThemeToggle } from "./ThemeToggle";
import { Button, Input } from "./ui";
import { UsageBar } from "./UsageBar";

export function Sidebar({
  selectedId,
  onSelect,
  onManageData,
  dataVersion,
}: {
  selectedId: string | null;
  onSelect: (id: string) => void;
  onManageData: () => void;
  dataVersion: number;
}) {
  const { user, logout, refreshUser } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState("");
  const [topicId, setTopicId] = useState<string>("");
  const avatarRef = useRef<HTMLInputElement>(null);

  async function loadConversations() {
    const { data } = await api.get<Conversation[]>("/conversations");
    setConversations(data);
  }
  useEffect(() => {
    loadConversations();
    api.get<Topic[]>("/topics").then((r) => setTopics(r.data));
  }, [dataVersion]);

  async function createConversation() {
    const { data } = await api.post<Conversation>("/conversations", {
      title: title || "New conversation",
      topic_id: topicId || null,
    });
    setCreating(false);
    setTitle("");
    setTopicId("");
    await loadConversations();
    onSelect(data.id);
  }

  async function uploadAvatar(file: File) {
    const fd = new FormData();
    fd.append("file", file);
    await api.post("/auth/me/avatar", fd);
    await refreshUser();
  }

  return (
    <aside className="flex h-full w-72 flex-col border-r border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-950">
      <div className="flex items-center justify-between p-3">
        <div className="flex items-center gap-2">
          <Logo className="h-7 w-7" />
          <span className="font-semibold tracking-tight">FinSight</span>
        </div>
        <Button onClick={() => setCreating((v) => !v)} className="px-2 py-1 text-xs">
          + New
        </Button>
      </div>

      {creating && (
        <div className="space-y-2 border-y border-neutral-200 p-3 dark:border-neutral-800">
          <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <select
            value={topicId}
            onChange={(e) => setTopicId(e.target.value)}
            className="w-full rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          >
            <option value="">No topic (web only)</option>
            {topics.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
          <Button className="w-full" onClick={createConversation}>
            Create
          </Button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-2">
        {conversations.map((c) => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={`block w-full truncate rounded-lg px-3 py-2 text-left text-sm ${
              selectedId === c.id
                ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
                : "hover:bg-neutral-100 dark:hover:bg-neutral-800"
            }`}
          >
            {c.title ?? "Conversation"}
            {c.topic_id && <span className="ml-1 text-xs text-neutral-400">· topic</span>}
          </button>
        ))}
      </div>

      <div className="border-t border-neutral-200 dark:border-neutral-800">
        <button
          onClick={onManageData}
          className="w-full px-4 py-2 text-left text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800"
        >
          📁 Manage data (topics)
        </button>
        <UsageBar refreshKey={dataVersion} />

        <div className="flex items-center gap-2 border-t border-neutral-200 p-3 dark:border-neutral-800">
          <input
            ref={avatarRef}
            type="file"
            accept="image/*"
            hidden
            onChange={(e) => e.target.files?.[0] && uploadAvatar(e.target.files[0])}
          />
          <button onClick={() => avatarRef.current?.click()} title="Change avatar">
            {user?.avatar_url ? (
              <img src={user.avatar_url} className="h-8 w-8 rounded-full object-cover" />
            ) : (
              <div className="grid h-8 w-8 place-items-center rounded-full bg-indigo-600 text-sm text-white">
                {(user?.full_name ?? user?.email ?? "?")[0]?.toUpperCase()}
              </div>
            )}
          </button>
          <div className="min-w-0 flex-1">
            <div className="truncate text-sm font-medium">{user?.full_name ?? "Account"}</div>
            <div className="truncate text-xs text-neutral-400">{user?.email}</div>
          </div>
          <ThemeToggle />
          <Button variant="ghost" onClick={logout} className="px-2" title="Sign out">
            ⏏
          </Button>
        </div>
      </div>
    </aside>
  );
}
