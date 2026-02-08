<<<<<<< HEAD
const WHITE = "rgba(255,255,255,0.95)";

export function ThinkingSection() {
  return (
    <section
      id="thinking"
      style={{
        height: "100vh",
        width: "100%",
        background: "#000000",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 24px 80px 24px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Subtle bg */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(900px 400px at 50% 30%, rgba(255,255,255,0.02), transparent 60%)",
          pointerEvents: "none",
        }}
      />

      <div style={{ width: "min(1100px, 96vw)", position: "relative" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 45 }}>
          <div style={{ fontSize: 44, fontWeight: 900, color: "#ffffff" }}>
            How We Make You Win
          </div>
          <div style={{ marginTop: 10, fontSize: 16, color: "rgba(255,255,255,0.50)" }}>
            Our AI watches, learns, and coaches you to victory
          </div>
        </div>

        {/* Engine Card */}
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            border: "1.5px solid rgba(255,255,255,0.10)",
            borderRadius: 22,
            padding: 36,
            boxShadow: "0 4px 24px rgba(0,0,0,0.20)",
          }}
        >
          {/* Engine Header */}
          <div style={{ textAlign: "center", marginBottom: 36 }}>
            <div style={{ fontSize: 26, fontWeight: 800, color: "#ffffff", marginBottom: 8 }}>
              Break Point Engine
            </div>
            <div style={{
              display: "inline-block", fontSize: 10, letterSpacing: "0.18em",
              color: WHITE, fontWeight: 700,
              padding: "5px 14px", borderRadius: 999,
              background: "rgba(255,255,255,0.08)",
            }}>
              KIMI K2 THINK + GEMINI + SNOWFLAKE
            </div>
          </div>

          {/* Pipeline boxes - 5 steps */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 14, marginBottom: 30 }}>
            <PipelineBox
              step="1"
              label="Watch"
              detail="Your Match"
              sub="We capture every move you make"
            />
            <PipelineBox
              step="2"
              label="Detect"
              detail="Court + Players"
              sub="AI identifies the playing field"
            />
            <PipelineBox
              step="3"
              label="Track"
              detail="Every Shot"
              sub="Ball trajectory + body movement"
            />
            <PipelineBox
              step="4"
              label="Analyze"
              detail="Your Patterns"
              sub="Find what's holding you back"
            />
            <PipelineBox
              step="5"
              label="Coach"
              detail="Your Win"
              sub="Specific fixes that work"
            />
          </div>

          {/* Arrow */}
          <div style={{ textAlign: "center", margin: "16px 0" }}>
            <div style={{ fontSize: 28, color: "rgba(255,255,255,0.25)" }}>↓</div>
          </div>

          {/* Output */}
          <div
            style={{
              background: "rgba(255,255,255,0.05)",
              border: `1px solid rgba(255,255,255,0.15)`,
              borderRadius: 14,
              padding: 28,
              textAlign: "center",
              marginBottom: 24,
            }}
          >
            <div style={{ fontSize: 22, fontWeight: 700, color: "#ffffff", marginBottom: 6 }}>
              "Step in and drive after pushing."
            </div>
            <div style={{ fontSize: 12, letterSpacing: "0.10em", color: "rgba(255,255,255,0.45)" }}>
              One clear fix. Instant improvement.
            </div>
          </div>

          {/* Tech stack badges */}
          <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap" }}>
            {["OpenCV", "MediaPipe", "Kimi K2 Think", "Snowflake", "Gemini 2.0 Flash", "Flowglad"].map(t => (
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
      </div>
    </section>
  );
}

function PipelineBox({ step, label, detail, sub }: { step: string; label: string; detail: string; sub: string }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.03)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 12,
        padding: "18px 14px",
        textAlign: "center",
        transition: "all 0.25s ease",
        cursor: "default",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.30)";
        e.currentTarget.style.background = "rgba(255,255,255,0.06)";
        e.currentTarget.style.transform = "translateY(-3px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)";
        e.currentTarget.style.background = "rgba(255,255,255,0.03)";
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      <div style={{
        width: 30, height: 30, borderRadius: 999, margin: "0 auto 10px",
        background: WHITE, color: "#000", fontSize: 14, fontWeight: 900,
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        {step}
      </div>
      <div style={{ fontSize: 12, fontWeight: 700, color: "#ffffff", marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 11, fontWeight: 600, color: WHITE, marginBottom: 5 }}>{detail}</div>
      <div style={{ fontSize: 10, color: "rgba(255,255,255,0.40)", lineHeight: 1.4 }}>{sub}</div>
    </div>
  );
}
=======
export function ThinkingSection() {
    return (
      <section
        id="thinking"
        style={{
          height: "100vh",
          width: "100%",
          background: "#050506",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "40px 24px 80px 24px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Background glow */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(900px 400px at 50% 30%, rgba(100,100,255,0.06), transparent 60%)," +
              "radial-gradient(800px 500px at 50% 70%, rgba(255,255,255,0.03), transparent 60%)",
            pointerEvents: "none",
          }}
        />
  
        <div style={{ width: "min(1100px, 96vw)", position: "relative" }}>
          {/* Header */}
          <div style={{ textAlign: "center", marginBottom: 50 }}>
            <div style={{ fontSize: 52, fontWeight: 900, color: "rgba(255,255,255,0.92)" }}>
              The Thinking
            </div>
            <div style={{ marginTop: 12, fontSize: 18, color: "rgba(255,255,255,0.50)" }}>
              How Break Point knows what to change
            </div>
          </div>
  
          {/* Main Engine Card */}
          <div
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 24,
              padding: 40,
              boxShadow: "0 30px 80px rgba(0,0,0,0.60)",
            }}
          >
            {/* Engine Header */}
            <div style={{ textAlign: "center", marginBottom: 40 }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: "rgba(255,255,255,0.90)", marginBottom: 10 }}>
                Break Point Engine
              </div>
              <div
                style={{
                  display: "inline-block",
                  fontSize: 11,
                  letterSpacing: "0.18em",
                  color: "rgba(150,150,200,0.70)",
                  fontWeight: 700,
                }}
              >
                REASONED WITH K2 THINK
              </div>
            </div>
  
            {/* Input Boxes - 3 columns */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: 20,
                marginBottom: 35,
              }}
            >
              {/* Match Behavior */}
              <InputBox
                label="Match Behavior"
                value="Defensive patterns detected"
              />
  
              {/* Opponent Tendencies */}
              <InputBox
                label="Opponent Tendencies"
                value="Counter-puncher profile"
              />
  
              {/* Pressure Context */}
              <InputBox
                label="Pressure Context"
                value="Break point, 10-9"
              />
            </div>
  
            {/* Arrow Down */}
            <div style={{ textAlign: "center", margin: "20px 0" }}>
              <div
                style={{
                  fontSize: 32,
                  color: "rgba(255,255,255,0.25)",
                }}
              >
                ↓
              </div>
            </div>
  
            {/* Output Recommendation */}
            <div
              style={{
                background: "rgba(20,15,25,0.60)",
                border: "1px solid rgba(255,255,255,0.10)",
                borderRadius: 16,
                padding: 32,
                textAlign: "center",
                marginBottom: 30,
              }}
            >
              <div
                style={{
                  fontSize: 24,
                  fontWeight: 700,
                  color: "rgba(255,255,255,0.88)",
                  marginBottom: 8,
                }}
              >
                Attack the middle. Don't push.
              </div>
              <div
                style={{
                  fontSize: 12,
                  letterSpacing: "0.12em",
                  color: "rgba(255,255,255,0.40)",
                }}
              >
                Recommended tactical adjustment
              </div>
            </div>
  
            {/* Show Reasoning Button */}
            <div style={{ textAlign: "center" }}>
              <button
                style={{
                  padding: "16px 40px",
                  borderRadius: 999,
                  background: "transparent",
                  border: "1px solid rgba(255,255,255,0.22)",
                  color: "rgba(255,255,255,0.85)",
                  fontSize: 15,
                  fontWeight: 600,
                  letterSpacing: "0.08em",
                  cursor: "pointer",
                  transition: "all 0.3s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "rgba(255,255,255,0.08)";
                  e.currentTarget.style.borderColor = "rgba(255,255,255,0.40)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "transparent";
                  e.currentTarget.style.borderColor = "rgba(255,255,255,0.22)";
                }}
              >
                Show Reasoning
              </button>
            </div>
          </div>
  
          {/* Bottom hint */}
          <div
            style={{
              position: "fixed",
              bottom: 20,
              left: 0,
              right: 0,
              textAlign: "center",
              fontSize: 12,
              letterSpacing: "0.35em",
              opacity: 0.42,
              userSelect: "none",
              color: "rgba(255,255,255,0.45)",
              zIndex: 100,
            }}
          >
            END OF ANALYSIS
          </div>
        </div>
      </section>
    );
  }
  
  // Input Box Component
  function InputBox({ label, value }: { label: string; value: string }) {
    return (
      <div
        style={{
          background: "rgba(255,255,255,0.02)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 12,
          padding: 20,
          textAlign: "center",
          cursor: "pointer",
          transition: "all 0.3s ease",
          opacity: 0.6,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.opacity = "1";
          e.currentTarget.style.transform = "translateY(-4px)";
          e.currentTarget.style.background = "rgba(255,255,255,0.04)";
          e.currentTarget.style.borderColor = "rgba(255,255,255,0.18)";
          e.currentTarget.style.boxShadow = "0 12px 40px rgba(0,0,0,0.40)";
          const valueElement = e.currentTarget.querySelector('.input-value') as HTMLElement;
          if (valueElement) {
            valueElement.style.fontWeight = "700";
            valueElement.style.color = "rgba(255,255,255,0.92)";
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.opacity = "0.6";
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.background = "rgba(255,255,255,0.02)";
          e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)";
          e.currentTarget.style.boxShadow = "none";
          const valueElement = e.currentTarget.querySelector('.input-value') as HTMLElement;
          if (valueElement) {
            valueElement.style.fontWeight = "600";
            valueElement.style.color = "rgba(255,255,255,0.75)";
          }
        }}
      >
        <div
          style={{
            fontSize: 11,
            letterSpacing: "0.12em",
            color: "rgba(255,255,255,0.40)",
            marginBottom: 10,
            fontWeight: 600,
          }}
        >
          {label}
        </div>
        <div
          className="input-value"
          style={{
            fontSize: 15,
            fontWeight: 600,
            color: "rgba(255,255,255,0.75)",
            lineHeight: 1.4,
            transition: "all 0.3s ease",
          }}
        >
          {value}
        </div>
      </div>
    );
  }
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
