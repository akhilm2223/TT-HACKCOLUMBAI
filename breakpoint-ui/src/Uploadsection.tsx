import { useState } from "react";
import { GoDeeperModal } from "./GoDeeperModal";

export function UploadSection() {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("video/")) {
      setSelectedFile(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleAnalyze = () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    
    // Simulate processing
    setTimeout(() => {
      setIsProcessing(false);
      setShowModal(true); // Show Go Deeper modal
    }, 1500);
  };

  return (
    <section
      id="upload"
      style={{
        minHeight: "100vh",
        width: "100%",
        background: "linear-gradient(180deg, #050506 0%, #0a0b0f 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "80px 24px 100px 24px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Dramatic background glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(1000px 500px at 50% 30%, rgba(255,0,60,0.08), transparent 60%)," +
            "radial-gradient(900px 600px at 30% 70%, rgba(100,100,255,0.06), transparent 60%)," +
            "radial-gradient(800px 500px at 70% 60%, rgba(50,200,150,0.05), transparent 60%)",
          pointerEvents: "none",
        }}
      />

      <div style={{ width: "min(1400px, 96vw)", position: "relative", zIndex: 1 }}>
        {/* Hero Section */}
        <div style={{ textAlign: "center", marginBottom: 70 }}>
          <div
            style={{
              display: "inline-block",
              padding: "8px 18px",
              borderRadius: 999,
              background: "rgba(255,0,60,0.12)",
              border: "1px solid rgba(255,0,60,0.30)",
              color: "rgba(255,60,100,0.95)",
              fontSize: 11,
              letterSpacing: "0.20em",
              fontWeight: 700,
              marginBottom: 24,
            }}
          >
            POWERED BY AI
          </div>

          <div style={{ fontSize: 56, fontWeight: 900, color: "rgba(255,255,255,0.95)", marginBottom: 20 }}>
            Your Match. Analyzed.
          </div>
          <div style={{ fontSize: 20, color: "rgba(255,255,255,0.55)", maxWidth: 700, margin: "0 auto", lineHeight: 1.6 }}>
            Upload your match video and get AI-powered insights on pressure moments, mental errors, and tactical adjustments
          </div>
        </div>

        {/* What We Analyze - 4 Icons */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: 24,
            marginBottom: 60,
          }}
        >
          <AnalysisFeature
            icon="🎥"
            title="Computer Vision"
            description="Tracks ball, shots, footwork"
          />
          <AnalysisFeature
            icon="📊"
            title="Pattern Detection"
            description="Finds behavioral patterns"
          />
          <AnalysisFeature
            icon="🧠"
            title="K2 Reasoning"
            description="Infers mental errors"
          />
          <AnalysisFeature
            icon="🎯"
            title="Opponent Analysis"
            description="Compares match styles"
          />
        </div>

        {/* Upload Area */}
        <div
          style={{
            background: "rgba(255,255,255,0.02)",
            border: isDragging
              ? "2px dashed rgba(255,0,60,0.60)"
              : selectedFile
              ? "2px solid rgba(50,200,150,0.40)"
              : "2px dashed rgba(255,255,255,0.12)",
            borderRadius: 24,
            padding: 60,
            textAlign: "center",
            transition: "all 0.3s ease",
            boxShadow: isDragging
              ? "0 0 60px rgba(255,0,60,0.20), 0 30px 80px rgba(0,0,0,0.60)"
              : "0 30px 80px rgba(0,0,0,0.60)",
            position: "relative",
            overflow: "hidden",
          }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {/* Animated background on drag */}
          {isDragging && (
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: "rgba(255,0,60,0.05)",
                animation: "pulse 1s ease-in-out infinite",
              }}
            />
          )}

          {!selectedFile ? (
            <>
              {/* Upload Icon */}
              <div
                style={{
                  fontSize: 72,
                  marginBottom: 24,
                  opacity: isDragging ? 1 : 0.6,
                  transform: isDragging ? "scale(1.1)" : "scale(1)",
                  transition: "all 0.3s ease",
                }}
              >
                📤
              </div>

              <div style={{ fontSize: 24, fontWeight: 700, color: "rgba(255,255,255,0.90)", marginBottom: 12 }}>
                {isDragging ? "Drop your video here" : "Upload Match Video"}
              </div>
              <div style={{ fontSize: 15, color: "rgba(255,255,255,0.50)", marginBottom: 32 }}>
                Drag and drop or click to browse • MP4, MOV, AVI up to 500MB
              </div>

              {/* Browse Button */}
              <label>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleFileSelect}
                  style={{ display: "none" }}
                />
                <div
                  style={{
                    display: "inline-block",
                    padding: "16px 40px",
                    borderRadius: 999,
                    background: "linear-gradient(135deg, rgba(255,0,60,0.90), rgba(200,0,100,0.90))",
                    color: "rgba(255,255,255,0.95)",
                    fontSize: 15,
                    fontWeight: 700,
                    letterSpacing: "0.08em",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                    boxShadow: "0 8px 24px rgba(255,0,60,0.30)",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = "translateY(-2px)";
                    e.currentTarget.style.boxShadow = "0 12px 32px rgba(255,0,60,0.40)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow = "0 8px 24px rgba(255,0,60,0.30)";
                  }}
                >
                  Browse Files
                </div>
              </label>
            </>
          ) : (
            <>
              {/* Selected File */}
              <div
                style={{
                  fontSize: 48,
                  marginBottom: 20,
                }}
              >
                ✓
              </div>
              <div style={{ fontSize: 20, fontWeight: 700, color: "rgba(50,220,120,0.95)", marginBottom: 8 }}>
                Video Ready
              </div>
              <div style={{ fontSize: 15, color: "rgba(255,255,255,0.60)", marginBottom: 32 }}>
                {selectedFile.name} • {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </div>

              {/* Analyze Button */}
              <div style={{ display: "flex", gap: 16, justifyContent: "center" }}>
                <button
                  onClick={() => setSelectedFile(null)}
                  style={{
                    padding: "14px 32px",
                    borderRadius: 999,
                    background: "transparent",
                    border: "1px solid rgba(255,255,255,0.20)",
                    color: "rgba(255,255,255,0.70)",
                    fontSize: 14,
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = "rgba(255,255,255,0.05)";
                    e.currentTarget.style.borderColor = "rgba(255,255,255,0.35)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = "transparent";
                    e.currentTarget.style.borderColor = "rgba(255,255,255,0.20)";
                  }}
                >
                  Change Video
                </button>

                <button
                  onClick={handleAnalyze}
                  disabled={isProcessing}
                  style={{
                    padding: "14px 48px",
                    borderRadius: 999,
                    background: isProcessing
                      ? "rgba(100,100,100,0.40)"
                      : "linear-gradient(135deg, rgba(255,0,60,0.90), rgba(200,0,100,0.90))",
                    border: "none",
                    color: "rgba(255,255,255,0.95)",
                    fontSize: 15,
                    fontWeight: 700,
                    letterSpacing: "0.08em",
                    cursor: isProcessing ? "wait" : "pointer",
                    transition: "all 0.3s ease",
                    boxShadow: "0 8px 24px rgba(255,0,60,0.30)",
                  }}
                  onMouseEnter={(e) => {
                    if (!isProcessing) {
                      e.currentTarget.style.transform = "translateY(-2px)";
                      e.currentTarget.style.boxShadow = "0 12px 32px rgba(255,0,60,0.40)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow = "0 8px 24px rgba(255,0,60,0.30)";
                  }}
                >
                  {isProcessing ? "Processing..." : "Analyze Match"}
                </button>
              </div>
            </>
          )}
        </div>

        {/* Processing Flow */}
        <div style={{ marginTop: 60 }}>
          <div style={{ textAlign: "center", marginBottom: 40 }}>
            <div style={{ fontSize: 14, letterSpacing: "0.15em", color: "rgba(255,255,255,0.40)", fontWeight: 700 }}>
              WHAT HAPPENS NEXT
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: 20,
              position: "relative",
            }}
          >
            {/* Connection lines */}
            <div
              style={{
                position: "absolute",
                top: 30,
                left: "12.5%",
                right: "12.5%",
                height: 2,
                background: "linear-gradient(90deg, rgba(255,0,60,0.30), rgba(100,100,255,0.30), rgba(50,200,150,0.30))",
                zIndex: 0,
              }}
            />

            <ProcessStep
              number="1"
              title="Upload"
              description="Video sent to secure backend"
              color="rgba(255,0,60,0.90)"
            />
            <ProcessStep
              number="2"
              title="Analyze"
              description="AI tracks every movement"
              color="rgba(200,100,255,0.90)"
            />
            <ProcessStep
              number="3"
              title="Detect"
              description="Finds pressure moments"
              color="rgba(100,150,255,0.90)"
            />
            <ProcessStep
              number="4"
              title="Coach"
              description="Tactical recommendations"
              color="rgba(50,200,150,0.90)"
            />
          </div>
        </div>

        {/* Bottom CTA */}
        <div
          style={{
            marginTop: 80,
            textAlign: "center",
            padding: "40px",
            background: "rgba(255,255,255,0.02)",
            borderRadius: 20,
            border: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          <div style={{ fontSize: 16, color: "rgba(255,255,255,0.70)", lineHeight: 1.8 }}>
            Break Point analyzes your match like a pro coach — finding the exact moments where mental pressure affected
            your game, then telling you <span style={{ color: "rgba(255,0,60,0.95)", fontWeight: 700 }}>what to change</span> next time.
          </div>
        </div>
      </div>

      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
          }
        `}
      </style>

      {/* Go Deeper Modal */}
      <GoDeeperModal isOpen={showModal} onClose={() => setShowModal(false)} />
    </section>
  );
}

// Analysis Feature Component
function AnalysisFeature({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.02)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 16,
        padding: 24,
        textAlign: "center",
        transition: "all 0.3s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "rgba(255,255,255,0.04)";
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.15)";
        e.currentTarget.style.transform = "translateY(-4px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "rgba(255,255,255,0.02)";
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)";
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      <div style={{ fontSize: 36, marginBottom: 12 }}>{icon}</div>
      <div style={{ fontSize: 14, fontWeight: 700, color: "rgba(255,255,255,0.88)", marginBottom: 6 }}>
        {title}
      </div>
      <div style={{ fontSize: 12, color: "rgba(255,255,255,0.50)", lineHeight: 1.5 }}>
        {description}
      </div>
    </div>
  );
}

// Process Step Component
function ProcessStep({
  number,
  title,
  description,
  color,
}: {
  number: string;
  title: string;
  description: string;
  color: string;
}) {
  return (
    <div style={{ position: "relative", zIndex: 1 }}>
      {/* Number circle */}
      <div
        style={{
          width: 60,
          height: 60,
          borderRadius: 999,
          background: color,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 24,
          fontWeight: 900,
          color: "#fff",
          margin: "0 auto 16px",
          boxShadow: `0 8px 24px ${color}40`,
        }}
      >
        {number}
      </div>

      <div style={{ fontSize: 16, fontWeight: 700, color: "rgba(255,255,255,0.90)", marginBottom: 6, textAlign: "center" }}>
        {title}
      </div>
      <div style={{ fontSize: 13, color: "rgba(255,255,255,0.50)", textAlign: "center", lineHeight: 1.5 }}>
        {description}
      </div>
    </div>
  );
}