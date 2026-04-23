import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { AuthGate } from "./components/AuthGate";
import { Dashboard } from "./pages/Dashboard";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AuthGate>
      <Dashboard />
    </AuthGate>
  </StrictMode>
);
