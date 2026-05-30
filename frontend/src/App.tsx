import { useEffect, useState } from "react";
import { getHealth, type Health } from "./api/client";

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch((e) => setError(String(e)));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem", maxWidth: 720 }}>
      <h1>FinSight</h1>
      <p>Multi-Agent Financial Research Assistant</p>
      <section style={{ marginTop: "1.5rem" }}>
        <h2>Backend status</h2>
        {error && <pre style={{ color: "crimson" }}>{error}</pre>}
        {health ? (
          <pre>{JSON.stringify(health, null, 2)}</pre>
        ) : (
          !error && <p>Checking…</p>
        )}
      </section>
      {/* Chat UI, document upload, task panel and citation viewer land in milestone M5. */}
    </main>
  );
}
