import { useState } from "react";
import { GoDeeperModal } from "./GoDeeperModal";

const WHITE = "rgba(255,255,255,0.95)";

export function UploadSection() {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const handleDragOver = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => setIsDragging(false);
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("video/")) setSelectedFile(file);
  };
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setSelectedFile(file);
  };
  const handleAnalyze = () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    setTimeout(() => { setIsProcessing(false); setShowModal(true); }, 1500);
  };

  return (
    <section
      id="upload"
      style={{
        minHeight: "100vh",
        width: "100%",
        background: "#000000",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "80px 24px 100px 24px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(1000px 500px at 50% 30%, rgba(255,255,255,0.03), transparent 60%)",
          pointerEvents: "none",
        }}
      />

      <div style={{ width: "min(1400px, 96vw)", position: "relative", zIndex: 1 }}>
        {/* Hero */}
        <div style={{ textAlign: "center", marginBottom: 60 }}>
          <div style={{
            display: "inline-block", padding: "6px 16px", borderRadius: 999,
            background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.25)",
            color: WHITE, fontSize: 10, letterSpacing: "0.20em", fontWeight: 700, marginBottom: 22,
          }}>
            START WINNING NOW
          </div>

          <div style={{ fontSize: 48, fontWeight: 900, color: "#ffffff", marginBottom: 18 }}>
            Upload. Analyze. Win.
          </div>
          <div style={{ fontSize: 18, color: "rgba(255,255,255,0.50)", maxWidth: 680, margin: "0 auto", lineHeight: 1.6 }}>
            Drop your match video and get the exact fixes you need to beat your opponent next time
          </div>
        </div>

        {/* Features grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20, marginBottom: 50 }}>
          <Feature icon="👁️" title="We Watch" desc="Every shot you make" />
          <Feature icon="🔍" title="We Find" desc="Your hidden patterns" />
          <Feature icon="🧠" title="We Think" desc="Like a pro coach" />
          <Feature icon="🏆" title="You Win" desc="With our fixes" />
        </div>

        {/* Upload Area */}
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            border: isDragging
              ? `2px dashed ${WHITE}`
              : selectedFile
                ? "2px solid rgba(255,255,255,0.35)"
                : "2px dashed rgba(255,255,255,0.15)",
            borderRadius: 22,
            padding: 55,
            textAlign: "center",
            transition: "all 0.3s ease",
            boxShadow: isDragging
              ? "0 0 40px rgba(255,255,255,0.08)"
              : "0 4px 24px rgba(0,0,0,0.20)",
            position: "relative",
            overflow: "hidden",
          }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {!selectedFile ? (
            <>
              <div style={{ fontSize: 64, marginBottom: 20, opacity: isDragging ? 1 : 0.5, transition: "all 0.3s ease" }}>📤</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: "#ffffff", marginBottom: 10 }}>
                {isDragging ? "Drop your video here" : "Upload Your Match"}
              </div>
              <div style={{ fontSize: 14, color: "rgba(255,255,255,0.45)", marginBottom: 28 }}>
                Drag and drop or click to browse · MP4, MOV, AVI up to 500MB
              </div>
              <label>
                <input type="file" accept="video/*" onChange={handleFileSelect} style={{ display: "none" }} />
                <div
                  style={{
                    display: "inline-block", padding: "14px 36px", borderRadius: 999,
                    background: WHITE, color: "#000", fontSize: 14, fontWeight: 700,
                    letterSpacing: "0.06em", cursor: "pointer", transition: "all 0.3s ease",
                    boxShadow: "0 6px 20px rgba(255,255,255,0.15)",
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.transform = "translateY(-2px)"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.transform = "translateY(0)"; }}
                >
                  Choose File
                </div>
              </label>
            </>
          ) : (
            <>
              <div style={{ fontSize: 44, marginBottom: 16, color: WHITE }}>✓</div>
              <div style={{ fontSize: 18, fontWeight: 700, color: WHITE, marginBottom: 6 }}>Ready to Analyze</div>
              <div style={{ fontSize: 14, color: "rgba(255,255,255,0.55)", marginBottom: 28 }}>
                {selectedFile.name} · {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </div>
              <div style={{ display: "flex", gap: 14, justifyContent: "center" }}>
                <button
                  onClick={() => setSelectedFile(null)}
                  style={{
                    padding: "12px 28px", borderRadius: 999, background: "transparent",
                    border: "1px solid rgba(255,255,255,0.20)", color: "rgba(255,255,255,0.60)",
                    fontSize: 13, fontWeight: 600, cursor: "pointer", transition: "all 0.3s ease",
                  }}
                >
                  Change Video
                </button>
                <button
                  onClick={handleAnalyze}
                  disabled={isProcessing}
                  style={{
                    padding: "12px 40px", borderRadius: 999,
                    background: isProcessing ? "rgba(255,255,255,0.20)" : WHITE,
                    border: "none", color: "#000", fontSize: 14, fontWeight: 700,
                    letterSpacing: "0.06em", cursor: isProcessing ? "wait" : "pointer",
                    transition: "all 0.3s ease",
                    boxShadow: isProcessing ? "none" : "0 6px 20px rgba(255,255,255,0.15)",
                  }}
                >
                  {isProcessing ? "Processing..." : "Make Me Win"}
                </button>
              </div>
            </>
          )}
        </div>

        {/* Process flow */}
        <div style={{ marginTop: 50 }}>
          <div style={{ textAlign: "center", marginBottom: 30 }}>
            <div style={{ fontSize: 12, letterSpacing: "0.15em", color: "rgba(255,255,255,0.40)", fontWeight: 700 }}>
              HOW IT WORKS
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 18, position: "relative" }}>
            <div style={{
              position: "absolute", top: 26, left: "12.5%", right: "12.5%", height: 2,
              background: `linear-gradient(90deg, rgba(255,255,255,0.20), rgba(255,255,255,0.10))`, zIndex: 0,
            }} />
            <Step n="1" title="Upload" desc="Your match video" />
            <Step n="2" title="Analyze" desc="AI finds patterns" />
            <Step n="3" title="Learn" desc="Get your fixes" />
            <Step n="4" title="Win" desc="Beat your opponent" />
          </div>
        </div>

        {/* Bottom CTA */}
        <div style={{
          marginTop: 60, textAlign: "center", padding: 36,
          background: "rgba(255,255,255,0.03)", borderRadius: 18,
          border: "1.5px solid rgba(255,255,255,0.10)",
          boxShadow: "0 2px 12px rgba(0,0,0,0.15)",
        }}>
          <div style={{ fontSize: 15, color: "rgba(255,255,255,0.60)", lineHeight: 1.8 }}>
            Break Point turns your losses into lessons — finding the exact moments you choked
            and telling you <span style={{ color: WHITE, fontWeight: 700 }}>how to win next time</span>.
          </div>
        </div>
      </div>

      <GoDeeperModal isOpen={showModal} onClose={() => setShowModal(false)} />
    </section>
  );
}

function Feature({ icon, title, desc }: { icon: string; title: string; desc: string }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.03)", border: "1.5px solid rgba(255,255,255,0.10)",
        borderRadius: 14, padding: 22, textAlign: "center",
        transition: "all 0.25s ease", boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.25)";
        e.currentTarget.style.transform = "translateY(-3px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.10)";
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      <div style={{ fontSize: 32, marginBottom: 10 }}>{icon}</div>
      <div style={{ fontSize: 13, fontWeight: 700, color: "#ffffff", marginBottom: 4 }}>{title}</div>
      <div style={{ fontSize: 11, color: "rgba(255,255,255,0.45)", lineHeight: 1.5 }}>{desc}</div>
    </div>
  );
}

function Step({ n, title, desc }: { n: string; title: string; desc: string }) {
  return (
    <div style={{ position: "relative", zIndex: 1 }}>
      <div style={{
        width: 52, height: 52, borderRadius: 999, background: WHITE,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 20, fontWeight: 900, color: "#000", margin: "0 auto 12px",
        boxShadow: "0 6px 18px rgba(255,255,255,0.10)",
      }}>
        {n}
      </div>
      <div style={{ fontSize: 14, fontWeight: 700, color: "#ffffff", marginBottom: 4, textAlign: "center" }}>{title}</div>
      <div style={{ fontSize: 12, color: "rgba(255,255,255,0.45)", textAlign: "center", lineHeight: 1.5 }}>{desc}</div>
    </div>
  );
}
