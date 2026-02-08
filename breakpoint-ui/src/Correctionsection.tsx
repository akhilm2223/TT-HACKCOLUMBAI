import { useState, useRef, useEffect } from "react";

export function CorrectionSection() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // The text that comes from your backend
  const feedbackText = "Your feet stopped moving. Commit to the loop. Attack the middle of the court with aggressive placement. Don't let him dictate the rally from the baseline. Move forward and take control of the net position.";

  // Generate speech using ElevenLabs API
  const generateSpeech = async () => {
    if (audioUrl) {
      // If audio already generated, just play it
      playAudio();
      return;
    }

    setIsGenerating(true);

    try {
      // Replace with your ElevenLabs API key
      const ELEVENLABS_API_KEY = "sk_97c3724f934413d49670a3558cb37a43ed0c2bbb5478a092";
      const VOICE_ID = "21m00Tcm4TlvDq8ikWAM"; // Default voice, you can change this

      const response = await fetch(
        `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
        {
          method: "POST",
          headers: {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY,
          },
          body: JSON.stringify({
            text: feedbackText,
            model_id: "eleven_monolingual_v1",
            voice_settings: {
              stability: 0.5,
              similarity_boost: 0.5,
            },
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to generate speech");
      }

      const audioBlob = await response.blob();
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      // Create audio element and play
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => setIsPlaying(false);
      audio.play();
      setIsPlaying(true);
    } catch (error) {
      console.error("Error generating speech:", error);
      alert("Failed to generate speech. Please add your ElevenLabs API key.");
    } finally {
      setIsGenerating(false);
    }
  };

  const playAudio = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const pauseAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const togglePlayback = () => {
    if (isPlaying) {
      pauseAudio();
    } else {
      generateSpeech();
    }
  };

  return (
    <section
      id="correction"
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
            "radial-gradient(900px 400px at 30% 40%, rgba(50,200,100,0.06), transparent 60%)," +
            "radial-gradient(800px 500px at 70% 60%, rgba(255,255,255,0.03), transparent 60%)",
          pointerEvents: "none",
        }}
      />

      <div style={{ width: "min(1300px, 96vw)", position: "relative" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 50 }}>
          <div style={{ fontSize: 52, fontWeight: 900, color: "rgba(255,255,255,0.92)" }}>
            The Correction
          </div>
          <div style={{ marginTop: 12, fontSize: 18, color: "rgba(255,255,255,0.50)" }}>
            Hear what you should have done
          </div>
        </div>

        {/* Content Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1.1fr",
            gap: 32,
          }}
        >
          {/* Left: Voice Feedback */}
          <div
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 20,
              padding: 36,
              boxShadow: "0 30px 80px rgba(0,0,0,0.60)",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}
          >
            {/* Header */}
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 30 }}>
                {/* Play Button */}
                <button
                  onClick={togglePlayback}
                  disabled={isGenerating}
                  style={{
                    width: 70,
                    height: 70,
                    borderRadius: 999,
                    background: "rgba(255,255,255,0.95)",
                    border: "none",
                    cursor: isGenerating ? "wait" : "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 24,
                    color: "#000",
                    boxShadow: "0 8px 24px rgba(0,0,0,0.30)",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    if (!isGenerating) e.currentTarget.style.transform = "scale(1.05)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "scale(1)";
                  }}
                >
                  {isGenerating ? "..." : isPlaying ? "⏸" : "▶"}
                </button>

                <div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: "rgba(255,255,255,0.90)" }}>
                    Voice Feedback
                  </div>
                  <div
                    style={{
                      fontSize: 11,
                      letterSpacing: "0.08em",
                      color: "rgba(255,255,255,0.40)",
                      marginTop: 4,
                    }}
                  >
                    Powered by ElevenLabs
                  </div>
                </div>
              </div>

              {/* Waveform Visualization */}
              <Waveform isPlaying={isPlaying} />
            </div>

            {/* Transcript */}
            <div
              style={{
                marginTop: 30,
                padding: 20,
                background: "rgba(0,0,0,0.30)",
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.06)",
              }}
            >
              <div
                style={{
                  fontSize: 16,
                  fontStyle: "italic",
                  color: "rgba(255,255,255,0.65)",
                  lineHeight: 1.6,
                }}
              >
                "{feedbackText}"
              </div>
            </div>
          </div>

          {/* Right: Corrected Court Visualization */}
          <div
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 20,
              padding: 36,
              boxShadow: "0 30px 80px rgba(0,0,0,0.60)",
            }}
          >
            {/* Badge */}
            <div style={{ marginBottom: 20 }}>
              <div
                style={{
                  display: "inline-block",
                  padding: "8px 16px",
                  borderRadius: 999,
                  background: "rgba(50,200,100,0.15)",
                  border: "1px solid rgba(50,200,100,0.35)",
                  color: "rgba(50,220,120,0.95)",
                  fontSize: 11,
                  letterSpacing: "0.15em",
                  fontWeight: 700,
                }}
              >
                Corrected Version
              </div>
            </div>

            {/* Court Visualization */}
            <CorrectedCourt />
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

// Waveform Component
function Waveform({ isPlaying }: { isPlaying: boolean }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 3,
        height: 80,
      }}
    >
      {Array.from({ length: 40 }).map((_, i) => {
        const height = 20 + Math.random() * 40;
        const delay = i * 0.05;

        return (
          <div
            key={i}
            style={{
              width: 4,
              height: isPlaying ? `${height}%` : "20%",
              background: "rgba(255,255,255,0.30)",
              borderRadius: 2,
              transition: "height 0.3s ease",
              animation: isPlaying ? `waveform 1.2s ease-in-out ${delay}s infinite` : "none",
            }}
          />
        );
      })}

      <style>
        {`
          @keyframes waveform {
            0%, 100% { transform: scaleY(1); }
            50% { transform: scaleY(1.5); }
          }
        `}
      </style>
    </div>
  );
}

// Corrected Court Component
function CorrectedCourt() {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        background: "linear-gradient(180deg, rgba(20,30,50,0.4) 0%, rgba(10,15,25,0.6) 100%)",
        borderRadius: 16,
        border: "2px solid rgba(100,120,160,0.20)",
        height: 400,
        position: "relative",
        overflow: "hidden",
        cursor: "pointer",
        transition: "border-color 0.3s ease",
        borderColor: isHovered ? "rgba(50,220,120,0.40)" : "rgba(100,120,160,0.20)",
      }}
    >
      {/* Net line */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: "50%",
          height: 2,
          background: "rgba(200,210,230,0.25)",
          transform: "translateY(-50%)",
        }}
      />

      {/* Court lines */}
      <svg
        width="100%"
        height="100%"
        style={{ position: "absolute", inset: 0 }}
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
      >
        <path
          d="M 10,15 L 90,15 L 85,85 L 15,85 Z"
          fill="none"
          stroke="rgba(200,210,230,0.15)"
          strokeWidth="0.3"
        />
        <path
          d="M 30,15 L 70,15 L 68,50 L 32,50 Z"
          fill="none"
          stroke="rgba(200,210,230,0.12)"
          strokeWidth="0.3"
        />
        <path
          d="M 32,50 L 68,50 L 70,85 L 30,85 Z"
          fill="none"
          stroke="rgba(200,210,230,0.12)"
          strokeWidth="0.3"
        />

        {/* Trajectory path (shows on hover) */}
        {isHovered && (
          <path
            d="M 50,70 Q 48,55 50,40 Q 52,25 50,20"
            fill="none"
            stroke="rgba(50,220,120,0.40)"
            strokeWidth="0.8"
            strokeDasharray="2,2"
            style={{
              opacity: 0,
              animation: "fadeInPath 0.5s ease-out forwards",
            }}
          />
        )}
      </svg>

      {/* Animated ball (shows trajectory on hover) */}
      {isHovered ? (
        <div
          style={{
            position: "absolute",
            width: 14,
            height: 14,
            borderRadius: 999,
            background: "rgba(255,140,60,0.95)",
            boxShadow: "0 0 24px rgba(255,140,60,0.70)",
            transform: "translate(-50%, -50%)",
            zIndex: 10,
            animation: "ballTrajectory 2s ease-in-out infinite",
          }}
        />
      ) : (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "45%",
            width: 14,
            height: 14,
            borderRadius: 999,
            background: "rgba(255,140,60,0.95)",
            boxShadow: "0 0 24px rgba(255,140,60,0.70)",
            transform: "translate(-50%, -50%)",
            zIndex: 10,
          }}
        />
      )}

      {/* Corrected player position (green zone) */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: "25%",
          transform: "translateX(-50%)",
          width: 60,
          height: 80,
          background: "rgba(50,200,100,0.20)",
          border: "2px solid rgba(50,220,120,0.50)",
          borderRadius: "50% 50% 40% 40%",
          zIndex: 5,
          transition: "all 0.3s ease",
          opacity: isHovered ? 1 : 0.6,
          borderColor: isHovered ? "rgba(50,220,120,0.80)" : "rgba(50,220,120,0.50)",
        }}
      />

      {/* Player silhouette */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: "28%",
          transform: "translateX(-50%)",
          width: 40,
          height: 50,
          background: "rgba(150,160,180,0.50)",
          borderRadius: "50% 50% 40% 40%",
          zIndex: 6,
        }}
      />

      {/* Trail dots showing corrected path (on hover) */}
      {isHovered && (
        <>
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "70%",
              width: 8,
              height: 8,
              borderRadius: 999,
              background: "rgba(50,220,120,0.40)",
              border: "1px solid rgba(50,220,120,0.60)",
              transform: "translate(-50%, -50%)",
              opacity: 0,
              animation: "fadeInDot 0.3s ease-out 0.1s forwards",
              zIndex: 5,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: "48%",
              top: "55%",
              width: 8,
              height: 8,
              borderRadius: 999,
              background: "rgba(50,220,120,0.40)",
              border: "1px solid rgba(50,220,120,0.60)",
              transform: "translate(-50%, -50%)",
              opacity: 0,
              animation: "fadeInDot 0.3s ease-out 0.2s forwards",
              zIndex: 5,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "40%",
              width: 8,
              height: 8,
              borderRadius: 999,
              background: "rgba(50,220,120,0.40)",
              border: "1px solid rgba(50,220,120,0.60)",
              transform: "translate(-50%, -50%)",
              opacity: 0,
              animation: "fadeInDot 0.3s ease-out 0.3s forwards",
              zIndex: 5,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: "52%",
              top: "25%",
              width: 8,
              height: 8,
              borderRadius: 999,
              background: "rgba(50,220,120,0.40)",
              border: "1px solid rgba(50,220,120,0.60)",
              transform: "translate(-50%, -50%)",
              opacity: 0,
              animation: "fadeInDot 0.3s ease-out 0.4s forwards",
              zIndex: 5,
            }}
          />
        </>
      )}

      <style>
        {`
          @keyframes ballTrajectory {
            0% { left: 50%; top: 70%; }
            25% { left: 48%; top: 55%; }
            50% { left: 50%; top: 40%; }
            75% { left: 52%; top: 25%; }
            100% { left: 50%; top: 20%; }
          }

          @keyframes fadeInPath {
            from { opacity: 0; }
            to { opacity: 1; }
          }

          @keyframes fadeInDot {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0); }
            to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
          }
        `}
      </style>
    </div>
  );
}