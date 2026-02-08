import { useEffect, useRef, useState } from "react";
import { MATCHES } from "./lib/matchData";
import type { Match } from "./lib/matchData";
import { useAICoach } from "./hooks/useAICoach";
import type { CoachMessage } from "./hooks/useAICoach";
import { useVoiceCoach } from "./hooks/useVoiceCoach";

const C = {
  white: "rgba(255,255,255,0.95)",
  dim: "rgba(255,255,255,0.50)",
  muted: "rgba(255,255,255,0.35)",
  faint: "rgba(255,255,255,0.20)",
  ghost: "rgba(255,255,255,0.08)",
  panel: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.10)",
  blue: "rgba(96,165,250,0.85)",
  green: "rgba(74,222,128,0.80)",
  greenDim: "rgba(74,222,128,0.15)",
};

const QUICK_PROMPTS = [
  "Why do I lose long rallies?",
  "What should I change first?",
  "Compare my matches",
  "What to focus on next?",
  "Where should I place my shots?",
  "How do I fix my footwork?",
];

export function AICoachSection() {
  const [isVisible, setIsVisible] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState(0);
  const [input, setInput] = useState("");
  const sectionRef = useRef<HTMLElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const { messages, isLoading, askCoach, clearChat } = useAICoach();
  const voice = useVoiceCoach();

  const match: Match = MATCHES[selectedMatch];

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting && entry.intersectionRatio >= 0.1) setIsVisible(true); },
      { threshold: [0.1] },
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    const q = input.trim();
    if (!q || isLoading) return;
    setInput("");
    askCoach(q, match);
  };

  const handleQuickPrompt = (q: string) => {
    if (isLoading) return;
    setInput("");
    askCoach(q, match);
  };

  const anim = (delay: number) => ({
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? "translateY(0)" : "translateY(20px)",
    transition: `all 0.6s cubic-bezier(.2,.9,.2,1) ${delay}s`,
  });

  return (
    <section
      ref={sectionRef}
      id="ai-coach"
      style={{
        minHeight: "100vh",
        width: "100%",
        background: "#000",
        padding: "80px 24px 100px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: "radial-gradient(900px 400px at 50% 30%, rgba(96,165,250,0.03), transparent 60%)," +
          "radial-gradient(800px 500px at 70% 70%, rgba(74,222,128,0.02), transparent 60%)",
      }} />

      <div style={{ width: "min(1100px, 96vw)", margin: "0 auto", position: "relative" }}>

        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 40, ...anim(0) }}>
          <div style={{ fontSize: 44, fontWeight: 900, color: "#fff", lineHeight: 1.1 }}>
            Your AI Coach
          </div>
          <div style={{ marginTop: 10, fontSize: 16, color: C.dim }}>
            Ask anything about your matches. Get data-driven coaching. Hear it spoken.
          </div>
        </div>

        {/* Match selector */}
        <div style={{ display: "flex", gap: 10, justifyContent: "center", marginBottom: 32, ...anim(0.05) }}>
          {MATCHES.map((m, i) => (
            <button
              key={m.id}
              onClick={() => { setSelectedMatch(i); clearChat(); }}
              style={{
                all: "unset", cursor: "pointer",
                padding: "10px 22px", borderRadius: 10,
                fontSize: 13, fontWeight: 700,
                background: selectedMatch === i ? C.ghost : "transparent",
                color: selectedMatch === i ? "#fff" : C.dim,
                border: selectedMatch === i ? `1.5px solid ${C.white}` : `1.5px solid ${C.border}`,
                transition: "all 0.2s ease",
              }}
            >
              {m.label}
              <span style={{ fontSize: 10, color: C.muted, marginLeft: 6 }}>{m.shots_count} shots</span>
            </button>
          ))}
        </div>

        {/* Main coach card */}
        <div style={{
          background: C.panel, border: `1.5px solid ${C.border}`, borderRadius: 22,
          padding: 0, overflow: "hidden", ...anim(0.1),
        }}>

          {/* Coach header bar */}
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "18px 28px",
            borderBottom: `1px solid ${C.border}`,
            background: "rgba(255,255,255,0.02)",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{
                width: 42, height: 42, borderRadius: 999,
                background: "linear-gradient(135deg, rgba(96,165,250,0.9), rgba(74,222,128,0.7))",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 15, fontWeight: 900, color: "#000",
              }}>AI</div>
              <div>
                <div style={{ fontSize: 16, fontWeight: 800, color: "#fff" }}>Break Point Coach</div>
                <div style={{ fontSize: 10, color: C.muted, letterSpacing: "0.1em" }}>
                  POWERED BY GEMINI 2.0 FLASH + ELEVENLABS
                </div>
              </div>
            </div>
            <div style={{ fontSize: 11, color: C.muted }}>
              Context: <span style={{ color: C.white, fontWeight: 700 }}>{match.label}</span>
              <span style={{ marginLeft: 6 }}>{match.shots_count} shots &middot; {match.date}</span>
            </div>
          </div>

          {/* Chat area */}
          <div style={{
            minHeight: 360, maxHeight: 500, overflowY: "auto",
            padding: "24px 28px",
          }}>
            {messages.length === 0 ? (
              <EmptyState onPrompt={handleQuickPrompt} />
            ) : (
              <>
                {messages.map((msg, i) => (
                  <MessageBubble
                    key={i}
                    msg={msg}
                    voice={voice}
                  />
                ))}
                {isLoading && <ThinkingIndicator />}
                <div ref={chatEndRef} />
              </>
            )}
          </div>

          {/* Input bar */}
          <div style={{
            display: "flex", gap: 10,
            padding: "16px 28px 20px",
            borderTop: `1px solid ${C.border}`,
            background: "rgba(255,255,255,0.02)",
          }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter") handleSend(); }}
              placeholder="Ask anything about your match or next game..."
              style={{
                flex: 1, padding: "12px 18px",
                background: C.ghost, border: `1px solid ${C.border}`, borderRadius: 12,
                color: "#fff", fontSize: 14, outline: "none",
                transition: "border-color 0.2s ease",
              }}
              onFocus={e => e.currentTarget.style.borderColor = "rgba(96,165,250,0.5)"}
              onBlur={e => e.currentTarget.style.borderColor = C.border}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              style={{
                all: "unset", cursor: isLoading ? "wait" : "pointer",
                padding: "12px 28px", borderRadius: 12,
                background: input.trim() ? "linear-gradient(135deg, rgba(96,165,250,0.9), rgba(74,222,128,0.7))" : C.ghost,
                color: input.trim() ? "#000" : C.muted,
                fontWeight: 800, fontSize: 14,
                transition: "all 0.2s ease",
                opacity: isLoading ? 0.5 : 1,
              }}
            >
              {isLoading ? "Thinking..." : "Ask Coach"}
            </button>
          </div>
        </div>

        {/* Tech stack badges */}
        <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap", marginTop: 28, ...anim(0.2) }}>
          {["Gemini 2.0 Flash", "ElevenLabs", "Snowflake", "Kimi K2 Think", "OpenCV", "MediaPipe"].map(t => (
            <div key={t} style={{
              padding: "6px 14px", borderRadius: 999,
              background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.12)",
              fontSize: 11, fontWeight: 600, color: "rgba(255,255,255,0.55)",
              letterSpacing: "0.04em",
            }}>
              {t}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── Empty state with quick prompts ─────────────────────────── */
function EmptyState({ onPrompt }: { onPrompt: (q: string) => void }) {
  return (
    <div style={{ textAlign: "center", padding: "40px 0" }}>
      <div style={{
        width: 64, height: 64, borderRadius: 999, margin: "0 auto 18px",
        background: "linear-gradient(135deg, rgba(96,165,250,0.15), rgba(74,222,128,0.10))",
        border: `1.5px solid rgba(96,165,250,0.2)`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 28,
      }}>
        <span style={{ filter: "grayscale(0.3)" }}>&#x1F3D3;</span>
      </div>
      <div style={{ fontSize: 18, fontWeight: 800, color: "#fff", marginBottom: 6 }}>
        Ask your coach anything
      </div>
      <div style={{ fontSize: 13, color: C.dim, marginBottom: 24, maxWidth: 400, margin: "0 auto 24px" }}>
        Questions about your match data, tactics, patterns, or what to work on next
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
        {QUICK_PROMPTS.map(q => (
          <button
            key={q}
            onClick={() => onPrompt(q)}
            style={{
              all: "unset", cursor: "pointer",
              padding: "10px 18px", borderRadius: 10,
              background: C.ghost, border: `1px solid ${C.border}`,
              fontSize: 12, fontWeight: 600, color: C.dim,
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
  );
}

/* ── Message bubble ──────────────────────────────────────────── */
function MessageBubble({
  msg,
  voice,
}: {
  msg: CoachMessage;
  voice: ReturnType<typeof useVoiceCoach>;
}) {
  const isCoach = msg.role === "coach";

  return (
    <div style={{
      display: "flex",
      justifyContent: isCoach ? "flex-start" : "flex-end",
      marginBottom: 16,
    }}>
      <div style={{
        maxWidth: "80%",
        padding: "14px 18px",
        borderRadius: isCoach ? "4px 16px 16px 16px" : "16px 4px 16px 16px",
        background: isCoach ? C.panel : C.ghost,
        border: isCoach ? `1px solid ${C.border}` : `1px solid rgba(96,165,250,0.2)`,
      }}>
        {isCoach && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <div style={{
              width: 24, height: 24, borderRadius: 999,
              background: "linear-gradient(135deg, rgba(96,165,250,0.9), rgba(74,222,128,0.7))",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 9, fontWeight: 900, color: "#000",
            }}>AI</div>
            <span style={{ fontSize: 10, color: C.muted, fontWeight: 700, letterSpacing: "0.08em" }}>COACH</span>
          </div>
        )}

        <div style={{ fontSize: 14, color: isCoach ? "rgba(255,255,255,0.85)" : C.white, lineHeight: 1.6 }}>
          {msg.text}
        </div>

        {isCoach && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
            <VoiceButton text={msg.text} voice={voice} />
          </div>
        )}

        {isCoach && msg.followUps && msg.followUps.length > 0 && (
          <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 6 }}>
            {msg.followUps.map((f, i) => (
              <span
                key={i}
                style={{
                  padding: "6px 12px", borderRadius: 8,
                  background: C.ghost, border: `1px solid ${C.border}`,
                  fontSize: 11, color: C.dim, cursor: "pointer",
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
                {f}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Voice button ────────────────────────────────────────────── */
function VoiceButton({ text, voice }: { text: string; voice: ReturnType<typeof useVoiceCoach> }) {
  const handleClick = () => {
    if (voice.isPlaying) {
      voice.stop();
    } else if (voice.isGenerating) {
      return;
    } else {
      voice.speak(text);
    }
  };

  return (
    <button
      onClick={handleClick}
      style={{
        all: "unset", cursor: voice.isGenerating ? "wait" : "pointer",
        display: "flex", alignItems: "center", gap: 6,
        padding: "6px 14px", borderRadius: 8,
        background: voice.isPlaying ? C.greenDim : C.ghost,
        border: `1px solid ${voice.isPlaying ? "rgba(74,222,128,0.3)" : C.border}`,
        fontSize: 11, fontWeight: 700,
        color: voice.isPlaying ? C.green : C.muted,
        transition: "all 0.2s ease",
      }}
    >
      <span style={{ fontSize: 14 }}>{voice.isGenerating ? "\u23F3" : voice.isPlaying ? "\u23F9" : "\u25B6"}</span>
      {voice.isGenerating ? "Generating..." : voice.isPlaying ? "Stop" : "Hear Coach"}
    </button>
  );
}

/* ── Thinking indicator ──────────────────────────────────────── */
function ThinkingIndicator() {
  return (
    <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: 16 }}>
      <div style={{
        padding: "14px 18px", borderRadius: "4px 16px 16px 16px",
        background: C.panel, border: `1px solid ${C.border}`,
        display: "flex", alignItems: "center", gap: 8,
      }}>
        <div style={{
          width: 24, height: 24, borderRadius: 999,
          background: "linear-gradient(135deg, rgba(96,165,250,0.9), rgba(74,222,128,0.7))",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 9, fontWeight: 900, color: "#000",
        }}>AI</div>
        <div style={{ display: "flex", gap: 4 }}>
          {[0, 1, 2].map(i => (
            <div
              key={i}
              style={{
                width: 6, height: 6, borderRadius: 999,
                background: C.blue,
                animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
              }}
            />
          ))}
        </div>
        <style>{`@keyframes pulse { 0%, 100% { opacity: 0.3; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.2); } }`}</style>
      </div>
    </div>
  );
}
