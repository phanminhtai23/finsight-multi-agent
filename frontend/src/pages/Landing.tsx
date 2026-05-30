import { Link } from "react-router-dom";
import { Button } from "../components/ui";
import { ThemeToggle } from "../components/ThemeToggle";
import { useAuth } from "../context/AuthContext";

const FEATURES = [
  {
    title: "Multi-agent research",
    body: "A supervisor coordinates retrieval, analysis, writing and a critic that checks every claim.",
  },
  {
    title: "Grounded citations",
    body: "Every answer cites the exact document and page — or the live web source it came from.",
  },
  {
    title: "Your own knowledge",
    body: "Group documents into topics, upload PDFs, Word files or web links, and ask across them.",
  },
];

export default function Landing() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen bg-white dark:bg-neutral-950">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
        <span className="text-lg font-semibold tracking-tight">FinSight</span>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          {user ? (
            <Link to="/app">
              <Button>Open app</Button>
            </Link>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost">Sign in</Button>
              </Link>
              <Link to="/register">
                <Button>Get started</Button>
              </Link>
            </>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 pt-24 pb-16 text-center">
        <p className="mb-4 inline-block rounded-full border border-neutral-200 px-3 py-1 text-xs text-neutral-500 dark:border-neutral-800">
          Multi-agent financial research
        </p>
        <h1 className="text-balance text-5xl font-semibold leading-tight tracking-tight sm:text-6xl">
          Answers you can trust,
          <br />
          <span className="text-neutral-400 dark:text-neutral-500">with the receipts.</span>
        </h1>
        <p className="mx-auto mt-6 max-w-xl text-pretty text-lg text-neutral-600 dark:text-neutral-400">
          FinSight reads your documents and the live web, reasons over them with a team of
          agents, and answers every question with inline citations.
        </p>
        <div className="mt-10 flex justify-center gap-3">
          <Link to={user ? "/app" : "/register"}>
            <Button className="px-6 py-3 text-base">
              {user ? "Open the app" : "Start free"}
            </Button>
          </Link>
          <a href="https://github.com/phanminhtai23/finsight-multi-agent" target="_blank">
            <Button variant="outline" className="px-6 py-3 text-base">
              View on GitHub
            </Button>
          </a>
        </div>
      </main>

      <section className="mx-auto grid max-w-5xl gap-6 px-6 pb-28 sm:grid-cols-3">
        {FEATURES.map((f) => (
          <div key={f.title} className="rounded-2xl border border-neutral-200 p-6 dark:border-neutral-800">
            <h3 className="font-medium">{f.title}</h3>
            <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">{f.body}</p>
          </div>
        ))}
      </section>

      <footer className="border-t border-neutral-200 py-8 text-center text-sm text-neutral-500 dark:border-neutral-800">
        FinSight — built with LangGraph, Qdrant & Gemini.
      </footer>
    </div>
  );
}
