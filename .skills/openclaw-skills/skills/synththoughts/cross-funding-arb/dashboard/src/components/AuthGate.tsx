import { useState, useEffect } from "react";

const STORAGE_KEY = "funding_dashboard_auth";

interface Props {
  children: React.ReactNode;
}

export function AuthGate({ children }: Props) {
  const [authed, setAuthed] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved === "1") setAuthed(true);
  }, []);

  if (authed) return <>{children}</>;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (input === "FundingArb2026x") {
      sessionStorage.setItem(STORAGE_KEY, "1");
      setAuthed(true);
    } else {
      setError(true);
      setInput("");
    }
  }

  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <form
        onSubmit={handleSubmit}
        className="w-80 rounded-lg border border-border bg-card p-6"
      >
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Funding Dashboard
        </h2>
        <input
          type="password"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setError(false);
          }}
          placeholder="Enter password"
          autoFocus
          className="w-full rounded-md border border-border bg-secondary/50 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        />
        {error && (
          <p className="mt-2 text-xs text-loss">Incorrect password</p>
        )}
        <button
          type="submit"
          className="mt-4 w-full rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          Enter
        </button>
      </form>
    </div>
  );
}
