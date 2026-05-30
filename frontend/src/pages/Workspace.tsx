import { useState } from "react";
import { ChatView } from "../components/ChatView";
import { Sidebar } from "../components/Sidebar";
import { TopicsManager } from "../components/TopicsManager";
import { Button } from "../components/ui";

export default function Workspace() {
  const [selected, setSelected] = useState<string | null>(null);
  const [showTopics, setShowTopics] = useState(false);
  const [version, setVersion] = useState(0);

  return (
    <div className="flex h-screen bg-white dark:bg-neutral-950">
      <Sidebar
        selectedId={selected}
        onSelect={setSelected}
        onManageData={() => setShowTopics(true)}
        dataVersion={version}
      />
      <main className="flex-1 overflow-hidden">
        {selected ? (
          <ChatView key={selected} conversationId={selected} />
        ) : (
          <div className="grid h-full place-items-center text-center">
            <div>
              <h2 className="text-xl font-semibold">Start a conversation</h2>
              <p className="mt-1 text-sm text-neutral-500">
                Create a chat from the sidebar — pin a topic to ground answers in your data.
              </p>
              <Button className="mt-4" onClick={() => setShowTopics(true)}>
                Manage your data
              </Button>
            </div>
          </div>
        )}
      </main>

      {showTopics && (
        <TopicsManager
          onClose={() => {
            setShowTopics(false);
            setVersion((v) => v + 1);
          }}
          onChanged={() => setVersion((v) => v + 1)}
        />
      )}
    </div>
  );
}
