import { useState, useEffect, useRef } from "react";
import type { Match } from "./lib/matchData";
import { MATCHES } from "./lib/matchData";
import { useAICoach } from "./hooks/useAICoach";
import type { CoachMessage } from "./hooks/useAICoach";
import { useVoiceCoach } from "./hooks/useVoiceCoach";

const C = {
  white: "rgba(255,255,255,0.95)",
  dim: "rgba(255,255,255,0.50)",
  muted: "rgba(255,255,255,0.35)",
  ghost: "rgba(255,255,255,0.08)",
  panel: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.10)",
  blue: "rgba(96,165,250,0.85)",
  green: "rgba(74,222,128,0.80)",
  greenDim: "rgba(74,222,128,0.15)",
};

export function MiniCoach({ match }: { match: Match }) {
  const [input, setInput] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);
  const { messages, isLoading, askCoach, clearChat } = useAICoach();
  const voice = useVoiceCoach();

  // Clear chat when match changes
  const matchIdRef = useRef(match.id);
  useEffect(() => {
    if (matchIdRef.current !== match.id) {
      matchIdRef.current = match.id;
      clearChat();
    }
  }, [match.id, clearChat]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    const q = input.trim();
    if (!q || isLoading) return;
    setInput("");
    askCoach(q, match);
  };

  const quickPrompts = [
    `What's wrong in ${match.label}?`,
    "How do I fix this?",
    "What drill helps?",
    "Compare with other matches",
  ];

  return (
    <div>
      {/* Chat area */}
      <div style={{
        maxHeight: 300, overflowY: "auto",
        marginBottom: 12,
      }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: "center", padding: "20px 0" }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: "#fff", marginBottom: 8 }}>
              Ask your coach about {match.label}
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, justifyContent: "center" }}>
              {quickPrompts.map(q => (
                <button
                  key={q}
                  onClick={() => { if (!isLoading) askCoach(q, match); }}
                  style={{
                    all: "unset", cursor: "pointer",
                    padding: "7px 14px", borderRadius: 8,
                    background: C.ghost, border: `1px solid ${C.border}`,
                    fontSize: 11, fontWeight: 600, color: C.dim,
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = "rgba(96,165,250,0.4)";
                    e.currentTarget.style.color = "#fff";
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = C.border;
                    e.currentTarget.style.color = C.dim;
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <MiniBubble key={i} msg={msg} voice={voice} allMatches={MATCHES} />
            ))}
            {isLoading && <MiniThinking />}
            <div ref={chatEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter") handleSend(); }}
          placeholder="Ask your coach..."
          style={{
            flex: 1, padding: "10px 14px",
            background: C.ghost, border: `1px solid ${C.border}`, borderRadius: 10,
            color: "#fff", fontSize: 13, outline: "none",
          }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          style={{
            all: "unset", cursor: isLoading ? "wait" : "pointer",
            padding: "10px 20px", borderRadius: 10,
            background: input.trim() ? "linear-gradient(135deg, rgba(96,165,250,0.9), rgba(74,222,128,0.7))" : C.ghost,
            color: input.trim() ? "#000" : C.muted,
            fontWeight: 800, fontSize: 12,
            opacity: isLoading ? 0.5 : 1,
          }}
        >
          {isLoading ? "..." : "Ask"}
        </button>
      </div>
    </div>
  );
}

/* ── Mini message bubble ─────────────────────────────────────── */
function MiniBubble({
  msg,
  voice,
  allMatches: _allMatches,
}: {
  msg: CoachMessage;
  voice: ReturnType<typeof useVoiceCoach>;
  allMatches: Match[];
}) {
  const isCoach = msg.role === "coach";

  return (
    <div style={{
      display: "flex",
      justifyContent: isCoach ? "flex-start" : "flex-end",
      marginBottom: 10,
    }}>
      <div style={{
        maxWidth: "85%",
        padding: "10px 14px",
        borderRadius: isCoach ? "4px 12px 12px 12px" : "12px 4px 12px 12px",
        background: isCoach ? C.panel : C.ghost,
        border: isCoach ? `1px solid ${C.border}` : `1px solid rgba(96,165,250,0.2)`,
      }}>
        <div style={{ fontSize: 13, color: isCoach ? "rgba(255,255,255,0.85)" : C.white, lineHeight: 1.5 }}>
          {msg.text}
        </div>

        {isCoach && (
          <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 6 }}>
            <button
              onClick={() => {
                if (voice.isPlaying) voice.stop();
                else voice.speak(msg.text);
              }}
              style={{
                all: "unset", cursor: "pointer",
                width: 28, height: 28, borderRadius: 999,
                background: voice.isPlaying ? C.greenDim : C.ghost,
                border: `1px solid ${voice.isPlaying ? "rgba(74,222,128,0.3)" : C.border}`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 12, color: voice.isPlaying ? C.green : C.muted,
              }}
            >
              {voice.isPlaying ? "\u23F9" : "\u25B6"}
            </button>
            {msg.followUps && msg.followUps.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                {msg.followUps.slice(0, 2).map((f, i) => (
                  <span key={i} style={{
                    padding: "4px 10px", borderRadius: 6,
                    background: C.ghost, border: `1px solid ${C.border}`,
                    fontSize: 10, color: C.dim, cursor: "pointer",
                  }}>
                    {f}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Mini thinking indicator ─────────────────────────────────── */
function MiniThinking() {
  return (
    <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: 10 }}>
      <div style={{
        padding: "10px 14px", borderRadius: "4px 12px 12px 12px",
        background: C.panel, border: `1px solid ${C.border}`,
        display: "flex", gap: 4,
      }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: 5, height: 5, borderRadius: 999,
            background: C.blue,
            animation: `miniPulse 1.2s ease-in-out ${i * 0.2}s infinite`,
          }} />
        ))}
        <style>{`@keyframes miniPulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }`}</style>
      </div>
    </div>
  );
}
