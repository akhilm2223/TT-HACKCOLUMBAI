<<<<<<< HEAD
const WHITE = "rgba(255,255,255,0.95)";

export function GoDeeperModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.85)",
        backdropFilter: "blur(12px)",
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
        animation: "fadeIn 0.3s ease-out",
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(860px, 95vw)",
          background: "#111111",
          borderRadius: 22,
          padding: 55,
          position: "relative",
          boxShadow: "0 30px 80px rgba(0,0,0,0.40)",
          border: "1.5px solid rgba(255,255,255,0.10)",
          animation: "slideUp 0.4s cubic-bezier(.2,.9,.2,1)",
        }}
      >
        {/* Close */}
        <button
          onClick={onClose}
          style={{
            position: "absolute", top: 22, right: 22,
            width: 38, height: 38, borderRadius: 999,
            background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.12)",
            color: "rgba(255,255,255,0.50)", fontSize: 18, cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.10)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.05)"; }}
        >
          ✕
        </button>

        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 42, fontWeight: 900, color: "#ffffff", marginBottom: 14 }}>
            Level Up
          </div>
          <div style={{ fontSize: 16, color: "rgba(255,255,255,0.50)", marginBottom: 44 }}>
            Get the full breakdown and dominate your next match
          </div>

          {/* Locked preview */}
          <div style={{
            background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 18, padding: 70, marginBottom: 36, position: "relative", overflow: "hidden",
          }}>
            <div style={{
              position: "absolute", inset: 0,
              background: "radial-gradient(circle at center, rgba(0,0,0,0.3), rgba(0,0,0,0.7) 50%, rgba(0,0,0,0.9) 100%)",
              backdropFilter: "blur(8px)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <div style={{
                width: 90, height: 90, borderRadius: 999,
                background: "rgba(255,255,255,0.05)", border: "2px solid rgba(255,255,255,0.15)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 40, color: "rgba(255,255,255,0.40)",
              }}>
                🔒
              </div>
            </div>
            <div style={{ opacity: 0.25, filter: "blur(3px)" }}>
              <div style={{ fontSize: 13, color: "rgba(255,255,255,0.50)", marginBottom: 10 }}>Rally-by-Rally Breakdown</div>
              <div style={{ height: 100, background: "rgba(255,255,255,0.05)", borderRadius: 10, marginBottom: 16 }} />
              <div style={{ fontSize: 13, color: "rgba(255,255,255,0.50)", marginBottom: 10 }}>Mental State Analysis</div>
              <div style={{ height: 70, background: "rgba(255,255,255,0.05)", borderRadius: 10 }} />
            </div>
          </div>

          {/* Unlock */}
          <button style={{
            width: "100%", maxWidth: 380, padding: "16px 44px", borderRadius: 999,
            background: WHITE, border: "none", color: "#000",
            fontSize: 15, fontWeight: 700, letterSpacing: "0.05em", cursor: "pointer",
            transition: "all 0.3s ease", boxShadow: "0 6px 20px rgba(255,255,255,0.15)",
            marginBottom: 18,
          }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-2px)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; }}
          >
            Unlock Your Edge
          </button>

          <div style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", letterSpacing: "0.08em" }}>
            Powered by Flowglad
          </div>
        </div>

        <style>{`
          @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
          @keyframes slideUp { from { opacity: 0; transform: translateY(30px) scale(0.96); } to { opacity: 1; transform: translateY(0) scale(1); } }
        `}</style>
      </div>
    </div>
  );
}
=======
export function GoDeeperModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    if (!isOpen) return null;
  
    return (
      <div
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0,0,0,0.85)",
          backdropFilter: "blur(8px)",
          zIndex: 9999,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
          animation: "fadeIn 0.3s ease-out",
        }}
        onClick={onClose}
      >
        <div
          onClick={(e) => e.stopPropagation()}
          style={{
            width: "min(900px, 95vw)",
            background: "#0a0b0f",
            borderRadius: 24,
            padding: 60,
            position: "relative",
            boxShadow: "0 40px 120px rgba(0,0,0,0.80)",
            border: "1px solid rgba(255,255,255,0.08)",
            animation: "slideUp 0.4s cubic-bezier(.2,.9,.2,1)",
          }}
        >
          {/* Close button */}
          <button
            onClick={onClose}
            style={{
              position: "absolute",
              top: 24,
              right: 24,
              width: 40,
              height: 40,
              borderRadius: 999,
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.10)",
              color: "rgba(255,255,255,0.60)",
              fontSize: 20,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.10)";
              e.currentTarget.style.color = "rgba(255,255,255,0.90)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.05)";
              e.currentTarget.style.color = "rgba(255,255,255,0.60)";
            }}
          >
            ✕
          </button>
  
          {/* Content */}
          <div style={{ textAlign: "center" }}>
            {/* Header */}
            <div style={{ fontSize: 48, fontWeight: 900, color: "rgba(255,255,255,0.95)", marginBottom: 16 }}>
              Go Deeper
            </div>
            <div style={{ fontSize: 18, color: "rgba(255,255,255,0.55)", marginBottom: 50 }}>
              Unlock full match analysis and rematch strategy
            </div>
  
            {/* Locked Preview Area */}
            <div
              style={{
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 20,
                padding: 80,
                marginBottom: 40,
                position: "relative",
                overflow: "hidden",
              }}
            >
              {/* Blur overlay */}
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  background:
                    "radial-gradient(circle at center, rgba(10,11,15,0.3) 0%, rgba(10,11,15,0.7) 50%, rgba(10,11,15,0.95) 100%)",
                  backdropFilter: "blur(12px)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {/* Lock icon */}
                <div
                  style={{
                    width: 100,
                    height: 100,
                    borderRadius: 999,
                    background: "rgba(255,255,255,0.08)",
                    border: "2px solid rgba(255,255,255,0.15)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 48,
                    color: "rgba(255,255,255,0.40)",
                  }}
                >
                  🔒
                </div>
              </div>
  
              {/* Blurred background content (preview) */}
              <div style={{ opacity: 0.3, filter: "blur(4px)" }}>
                <div style={{ fontSize: 14, color: "rgba(255,255,255,0.60)", marginBottom: 12 }}>
                  Rally-by-Rally Breakdown
                </div>
                <div style={{ height: 120, background: "rgba(255,255,255,0.05)", borderRadius: 12, marginBottom: 20 }} />
                <div style={{ fontSize: 14, color: "rgba(255,255,255,0.60)", marginBottom: 12 }}>
                  Mental State Analysis
                </div>
                <div style={{ height: 80, background: "rgba(255,255,255,0.05)", borderRadius: 12 }} />
              </div>
            </div>
  
            {/* Unlock Button */}
            <button
              style={{
                width: "100%",
                maxWidth: 400,
                padding: "18px 48px",
                borderRadius: 999,
                background: "rgba(255,255,255,0.95)",
                border: "none",
                color: "#000",
                fontSize: 16,
                fontWeight: 700,
                letterSpacing: "0.05em",
                cursor: "pointer",
                transition: "all 0.3s ease",
                boxShadow: "0 8px 24px rgba(255,255,255,0.20)",
                marginBottom: 20,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "0 12px 32px rgba(255,255,255,0.30)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 8px 24px rgba(255,255,255,0.20)";
              }}
            >
              Unlock Analysis
            </button>
  
            {/* Powered by */}
            <div
              style={{
                fontSize: 12,
                color: "rgba(255,255,255,0.35)",
                letterSpacing: "0.08em",
              }}
            >
              Powered by Flowglad
            </div>
          </div>
  
          <style>
            {`
              @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
              }
  
              @keyframes slideUp {
                from { 
                  opacity: 0;
                  transform: translateY(40px) scale(0.95);
                }
                to { 
                  opacity: 1;
                  transform: translateY(0) scale(1);
                }
              }
            `}
          </style>
        </div>
      </div>
    );
  }
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
