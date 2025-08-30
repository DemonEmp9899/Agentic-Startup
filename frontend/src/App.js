// frontend/src/App.js
import React, { useState } from "react";
import "./App.css"; // make sure this import is present

export default function App() {
  const [prompt, setPrompt] = useState("We need to build an AI-powered personal finance assistant.");
  const [rounds, setRounds] = useState(2);
  const [loading, setLoading] = useState(false);
  const [conversation, setConversation] = useState([]);

  async function runSimulation() {
    setLoading(true);
    setConversation([]);
    try {
      const res = await fetch("http://127.0.0.1:8000/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, max_rounds: rounds }),
      });
      const data = await res.json();
      setConversation(data.conversation || []);
    } catch (err) {
      setConversation([{ from: "system", to: "frontend", response: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-background">
      <div className="app-container">
        <h1 className="app-title">Agentic Startup — Simulation</h1>

        <div className="form-group">
          <label>Initial Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
          />
        </div>

        <div className="form-inline">
          <div className="form-group">
            <label>Rounds</label>
            <input
              type="number"
              value={rounds}
              onChange={(e) => setRounds(Number(e.target.value))}
              min={1}
            />
          </div>
          <button onClick={runSimulation} disabled={loading}>
            {loading ? "Running…" : "Start Simulation"}
          </button>
        </div>

        <section className="conversation">
          <h2>Conversation</h2>
          {conversation.length === 0 && <div className="no-messages">No messages yet.</div>}
          {conversation.map((m, i) => (
            <div key={i} className={`message ${m.from === "system" ? "system" : "agent"}`}>
              <div className="from-to">{m.from} → {Array.isArray(m.to) ? m.to.join(", ") : m.to}</div>
              <pre>{typeof m.response === "string" ? m.response : JSON.stringify(m.response, null, 2)}</pre>
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}
