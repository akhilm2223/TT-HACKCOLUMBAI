import { useState, useRef } from "react";
import { LatestAnalysis } from "./LatestAnalysis";

const WHITE = "rgba(255,255,255,0.95)";

// Match data from analyzed videos
const PAST_MATCHES = [
    {
        id: "224148",
        label: "Match 1",
        date: "Feb 7",
        time: "10:41 PM",
        shots: 22,
        rallies: 17,
        videoFile: "/videos/analysis_224148.mp4",
    },
    {
        id: "153355",
        label: "Match 2",
        date: "Feb 7",
        time: "3:33 PM",
        shots: 10,
        rallies: 4,
        videoFile: "/videos/analysis_153355.mp4",
    },
    {
        id: "192747",
        label: "Match 3",
        date: "Feb 7",
        time: "7:27 PM",
        shots: 6,
        rallies: 3,
        videoFile: "/videos/analysis_192747.mp4",
    },
    {
        id: "134224",
        label: "Match 4",
        date: "Feb 7",
        time: "1:42 PM",
        shots: 6,
        rallies: 3,
        videoFile: "/videos/analysis_134224.mp4",
    },
];

export function VideoGallerySection() {
    const [showPastVideos, setShowPastVideos] = useState(false);
    const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState("");
    const [analysisOutput, setAnalysisOutput] = useState<string[]>([]);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [outputVideo, setOutputVideo] = useState<string | null>(null);
    const [latestMatchId, setLatestMatchId] = useState<string | null>(null);
    const [inputVideoUrl, setInputVideoUrl] = useState<string | null>(null);
    const [liveFrameUrl, setLiveFrameUrl] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        console.log("Starting upload for:", file.name);

        // Create blob URL for preview
        const videoUrl = URL.createObjectURL(file);
        setInputVideoUrl(videoUrl);

        setShowUploadModal(true);
        setIsUploading(true);
        setAnalysisOutput([]);
        setOutputVideo(null);
        setLatestMatchId(null);
        setUploadProgress("Analyzing...");

        // Start polling live frames with unique URL to bust cache
        let frameCounter = 0;
        const frameInterval = setInterval(() => {
            frameCounter++;
            setLiveFrameUrl(`http://localhost:5001/live-frame-latest?t=${Date.now()}`);
        }, 150); // Poll ~6-7 fps

        const formData = new FormData();
        formData.append("video", file);

        try {
            const response = await fetch("http://localhost:5001/analyze", {
                method: "POST",
                body: formData,
            });

            console.log("Response status:", response.status);

            if (!response.ok) throw new Error("Analysis failed: " + response.status);

            const reader = response.body?.getReader();
            if (!reader) throw new Error("Processing failed: No response body");
            const decoder = new TextDecoder();

            setUploadProgress("Analyzing with AI...");

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const text = decoder.decode(value, { stream: true });
                console.log("Received:", text);

                // Check for video output marker
                const videoMatch = text.match(/===VIDEO_OUTPUT===(.+?)===/);
                if (videoMatch) {
                    const videoFile = videoMatch[1];
                    setOutputVideo(`http://localhost:5001/output-videos/${videoFile}`);

                    // Extract matchId for fetching JSON analysis
                    const matchId = videoFile.match(/analysis_(\d+)\.mp4/)?.[1];
                    if (matchId) setLatestMatchId(matchId);

                    console.log("Output video:", videoFile);
                }

                // Filter out some noise from the output for cleaner display
                const cleanText = text
                    .replace(/W\d{4}.*inference_feedback_manager.*\n?/g, '')
                    .replace(/===VIDEO_OUTPUT===.+?===/g, '');

                if (cleanText.trim()) {
                    setAnalysisOutput((prev) => [...prev, cleanText]);
                }
            }

            setUploadProgress("Analysis complete!");
        } catch (err) {
            console.error("Upload error:", err);
            setUploadProgress("Error: " + (err instanceof Error ? err.message : "Could not complete analysis"));
            setAnalysisOutput((prev) => [...prev, "\n\nError occurred. Make sure the server is running on port 5001."]);
        } finally {
            clearInterval(frameInterval);
            setIsUploading(false);
            // Reset file input so same file can be re-selected
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    return (
        <section
            style={{
                height: "100vh",
                width: "100%",
                background: "#000000",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "40px 24px",
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
                        "radial-gradient(800px 400px at 50% 40%, rgba(255,255,255,0.03), transparent 60%)",
                    pointerEvents: "none",
                }}
            />

            <div style={{ width: "min(900px, 96vw)", position: "relative" }}>
                {/* Header */}
                <div style={{ textAlign: "center", marginBottom: 60 }}>
                    <div
                        style={{
                            fontSize: 52,
                            fontWeight: 900,
                            color: "#ffffff",
                            marginBottom: 14,
                        }}
                    >
                        Your Winning Edge
                    </div>
                    <div
                        style={{
                            fontSize: 20,
                            color: "rgba(255,255,255,0.50)",
                            maxWidth: 500,
                            margin: "0 auto",
                        }}
                    >
                        We find what's holding you back and fix it
                    </div>
                </div>

                {/* Latest Analysis Dashboard (replaces buttons when available) */}
                {!showPastVideos && latestMatchId && outputVideo && (
                    <LatestAnalysis videoUrl={outputVideo} matchId={latestMatchId} />
                )}

                {/* Two Main Buttons (Enhanced/Big) */}
                {!showPastVideos && !latestMatchId && (
                    <div
                        style={{
                            display: "flex",
                            gap: 40,
                            justifyContent: "center",
                            flexWrap: "wrap",
                            marginTop: 20
                        }}
                    >
                        {/* Add New Video Button */}
                        <div
                            onClick={() => fileInputRef.current?.click()}
                            style={{
                                background: "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02))",
                                border: "1px solid rgba(255,255,255,0.1)",
                                borderRadius: 32,
                                padding: "80px 60px",
                                cursor: "pointer",
                                transition: "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
                                textAlign: "center",
                                minWidth: 340,
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.borderColor = "rgba(255,255,255,0.40)";
                                e.currentTarget.style.transform = "translateY(-12px) scale(1.03)";
                                e.currentTarget.style.boxShadow = "0 30px 60px rgba(0,0,0,0.5)";
                                e.currentTarget.style.background = "linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04))";
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)";
                                e.currentTarget.style.transform = "translateY(0) scale(1)";
                                e.currentTarget.style.boxShadow = "none";
                                e.currentTarget.style.background = "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02))";
                            }}
                        >
                            <div
                                style={{
                                    width: 120,
                                    height: 120,
                                    borderRadius: "50%",
                                    background: "rgba(255,255,255,0.05)",
                                    border: "1px solid rgba(255,255,255,0.2)",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    margin: "0 auto 30px",
                                }}
                            >
                                <span style={{ fontSize: 60, color: WHITE, fontWeight: 200 }}>+</span>
                            </div>
                            <div style={{ fontSize: 32, fontWeight: 800, color: WHITE, marginBottom: 12, letterSpacing: "-0.02em" }}>
                                Add New Video
                            </div>
                            <div style={{ fontSize: 16, color: "rgba(255,255,255,0.5)", lineHeight: 1.5 }}>
                                Upload & analyze your match<br />to find your winning edge
                            </div>
                        </div>

                        {/* See Past Analysis Button */}
                        <div
                            onClick={() => setShowPastVideos(true)}
                            style={{
                                background: "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02))",
                                border: "1px solid rgba(255,255,255,0.1)",
                                borderRadius: 32,
                                padding: "80px 60px",
                                cursor: "pointer",
                                transition: "all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
                                textAlign: "center",
                                minWidth: 340,
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.borderColor = "rgba(255,255,255,0.40)";
                                e.currentTarget.style.transform = "translateY(-12px) scale(1.03)";
                                e.currentTarget.style.boxShadow = "0 30px 60px rgba(0,0,0,0.5)";
                                e.currentTarget.style.background = "linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04))";
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)";
                                e.currentTarget.style.transform = "translateY(0) scale(1)";
                                e.currentTarget.style.boxShadow = "none";
                                e.currentTarget.style.background = "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02))";
                            }}
                        >
                            <div
                                style={{
                                    width: 120,
                                    height: 120,
                                    borderRadius: "50%",
                                    background: "rgba(255,255,255,0.05)",
                                    border: "1px solid rgba(255,255,255,0.2)",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    margin: "0 auto 30px",
                                }}
                            >
                                <span style={{ fontSize: 50, color: WHITE }}>▶</span>
                            </div>
                            <div style={{ fontSize: 32, fontWeight: 800, color: WHITE, marginBottom: 12, letterSpacing: "-0.02em" }}>
                                Past Analysis
                            </div>
                            <div style={{ fontSize: 16, color: "rgba(255,255,255,0.5)", lineHeight: 1.5 }}>
                                Review styles & stats from<br />{PAST_MATCHES.length} previous matches
                            </div>
                        </div>
                    </div>
                )}

                {/* Past Videos Grid (shown when clicked) */}
                {showPastVideos && (
                    <div>
                        {/* Back button */}
                        <div
                            onClick={() => setShowPastVideos(false)}
                            style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 8,
                                color: "rgba(255,255,255,0.60)",
                                fontSize: 14,
                                cursor: "pointer",
                                marginBottom: 24,
                                padding: "8px 0",
                            }}
                        >
                            <span style={{ fontSize: 18 }}>←</span> Back
                        </div>

                        <div
                            style={{
                                display: "grid",
                                gridTemplateColumns: "repeat(2, 1fr)",
                                gap: 20,
                            }}
                        >
                            {PAST_MATCHES.map((match) => (
                                <div
                                    key={match.id}
                                    onClick={() => setSelectedVideo(match.videoFile)}
                                    style={{
                                        background: "rgba(255,255,255,0.04)",
                                        border: "1.5px solid rgba(255,255,255,0.10)",
                                        borderRadius: 14,
                                        padding: 16,
                                        cursor: "pointer",
                                        transition: "all 0.25s ease",
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.borderColor = "rgba(255,255,255,0.30)";
                                        e.currentTarget.style.transform = "translateY(-3px)";
                                        e.currentTarget.style.background = "rgba(255,255,255,0.07)";
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.borderColor = "rgba(255,255,255,0.10)";
                                        e.currentTarget.style.transform = "translateY(0)";
                                        e.currentTarget.style.background = "rgba(255,255,255,0.04)";
                                    }}
                                >
                                    <div
                                        style={{
                                            width: "100%",
                                            aspectRatio: "16/9",
                                            background: "rgba(255,255,255,0.08)",
                                            borderRadius: 8,
                                            marginBottom: 12,
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            position: "relative",
                                            overflow: "hidden",
                                        }}
                                    >
                                        <video
                                            src={match.videoFile}
                                            style={{
                                                width: "100%",
                                                height: "100%",
                                                objectFit: "cover",
                                                borderRadius: 8,
                                            }}
                                            muted
                                            preload="metadata"
                                        />
                                        <div
                                            style={{
                                                position: "absolute",
                                                width: 40,
                                                height: 40,
                                                background: "rgba(255,255,255,0.90)",
                                                borderRadius: "50%",
                                                display: "flex",
                                                alignItems: "center",
                                                justifyContent: "center",
                                            }}
                                        >
                                            <div
                                                style={{
                                                    width: 0,
                                                    height: 0,
                                                    borderTop: "8px solid transparent",
                                                    borderBottom: "8px solid transparent",
                                                    borderLeft: "12px solid #000",
                                                    marginLeft: 3,
                                                }}
                                            />
                                        </div>
                                    </div>

                                    <div style={{ fontSize: 15, fontWeight: 700, color: WHITE, marginBottom: 3 }}>
                                        {match.label}
                                    </div>
                                    <div style={{ fontSize: 11, color: "rgba(255,255,255,0.50)", marginBottom: 6 }}>
                                        {match.date} · {match.time}
                                    </div>
                                    <div style={{ fontSize: 12, color: "rgba(255,255,255,0.65)", fontWeight: 500 }}>
                                        {match.shots} shots · {match.rallies} rallies
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Hidden file input */}
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/*"
                    onChange={handleUpload}
                    style={{ display: "none" }}
                />

                {/* Upload Progress Modal */}
                {showUploadModal && (
                    <div
                        style={{
                            position: "fixed",
                            inset: 0,
                            background: "rgba(0,0,0,0.92)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            zIndex: 1000,
                        }}
                    >
                        <div
                            style={{
                                background: "rgba(15,15,15,0.98)",
                                border: "1px solid rgba(255,255,255,0.12)",
                                borderRadius: 24,
                                padding: outputVideo ? 24 : 50,
                                maxWidth: outputVideo ? 900 : 500,
                                width: "95%",
                                position: "relative",
                                transition: "all 0.3s ease",
                            }}
                        >
                            {/* Close button */}
                            {/* Close button (always visible) */}
                            <div
                                onClick={() => {
                                    setShowUploadModal(false);
                                    setIsUploading(false);
                                    if (fileInputRef.current) fileInputRef.current.value = "";
                                }}
                                style={{
                                    position: "absolute",
                                    top: 16,
                                    right: 16,
                                    width: 36,
                                    height: 36,
                                    borderRadius: "50%",
                                    background: "rgba(255,255,255,0.10)",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    cursor: "pointer",
                                    fontSize: 22,
                                    color: WHITE,
                                    zIndex: 20,
                                }}
                            >
                                ×
                            </div>

                            {/* Back button (top left) */}
                            <div
                                onClick={() => {
                                    setShowUploadModal(false);
                                    setIsUploading(false);
                                    if (fileInputRef.current) fileInputRef.current.value = "";
                                }}
                                style={{
                                    position: "absolute",
                                    top: 24,
                                    left: 24,
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 6,
                                    color: "rgba(255,255,255,0.60)",
                                    fontSize: 14,
                                    cursor: "pointer",
                                    zIndex: 20,
                                }}
                            >
                                <span style={{ fontSize: 18 }}>←</span> Back
                            </div>

                            {/* Show video player when available */}
                            {outputVideo ? (
                                <div>
                                    <div style={{
                                        fontSize: 22,
                                        fontWeight: 700,
                                        color: WHITE,
                                        marginBottom: 16,
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 10
                                    }}>
                                        🎬 Your Analysis is Ready
                                    </div>
                                    <video
                                        src={outputVideo}
                                        controls
                                        autoPlay
                                        style={{
                                            width: "100%",
                                            borderRadius: 16,
                                            background: "#000",
                                        }}
                                    />
                                </div>
                            ) : (
                                /* Show input video while analyzing */
                                <div>
                                    <div style={{
                                        fontSize: 18,
                                        fontWeight: 700,
                                        color: WHITE,
                                        marginBottom: 12,
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 8
                                    }}>
                                        {isUploading ? "🔄 Analyzing..." : "✅ Complete"}
                                    </div>

                                    {/* Video player with overlay */}
                                    <div style={{ position: "relative" }}>
                                        {/* Always render video as fallback/background */}
                                        {inputVideoUrl && (
                                            <video
                                                src={inputVideoUrl}
                                                controls
                                                autoPlay
                                                muted
                                                loop
                                                style={{
                                                    width: "100%",
                                                    borderRadius: 12,
                                                    background: "#000",
                                                    display: "block",
                                                    minHeight: 300
                                                }}
                                            // Actually, let's keep it simple:
                                            // If liveFrameUrl is set, try to show it. If it errors, hide it.
                                            />
                                        )}

                                        {liveFrameUrl && (
                                            <img
                                                src={liveFrameUrl}
                                                style={{
                                                    width: "100%",
                                                    borderRadius: 12,
                                                    background: "#000",
                                                    display: "block",
                                                    minHeight: 300,
                                                    position: inputVideoUrl ? "absolute" : "relative",
                                                    top: 0,
                                                    left: 0,
                                                    zIndex: 10
                                                }}
                                                alt="Live Analysis"
                                                onError={(e) => {
                                                    e.currentTarget.style.display = 'none';
                                                }}
                                                onLoad={(e) => {
                                                    e.currentTarget.style.display = 'block';
                                                }}
                                            />
                                        )}

                                        {/* Processing overlay */}
                                        {isUploading && (
                                            <div style={{
                                                position: "absolute",
                                                bottom: 12,
                                                left: 12,
                                                right: 12,
                                                background: "rgba(0,0,0,0.75)",
                                                borderRadius: 8,
                                                padding: "10px 14px",
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 10,
                                            }}>
                                                <div style={{
                                                    width: 8,
                                                    height: 8,
                                                    borderRadius: "50%",
                                                    background: "#4ade80",
                                                    animation: "pulse 1s infinite",
                                                }} />
                                                <span style={{
                                                    color: WHITE,
                                                    fontSize: 13,
                                                    fontWeight: 500
                                                }}>
                                                    AI is tracking poses & ball... 2-5 min
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Video Player Modal */}
                {selectedVideo && (
                    <div
                        onClick={() => setSelectedVideo(null)}
                        style={{
                            position: "fixed",
                            inset: 0,
                            background: "rgba(0,0,0,0.92)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            zIndex: 1000,
                            cursor: "pointer",
                        }}
                    >
                        <div
                            onClick={(e) => e.stopPropagation()}
                            style={{
                                maxWidth: "90vw",
                                maxHeight: "85vh",
                                borderRadius: 16,
                                overflow: "hidden",
                                boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
                            }}
                        >
                            <video
                                src={selectedVideo}
                                controls
                                autoPlay
                                style={{
                                    width: "80vw",
                                    height: "auto",
                                    maxWidth: "90vw",
                                    maxHeight: "85vh",
                                    borderRadius: 16,
                                }}
                            />
                        </div>
                        <div
                            onClick={() => setSelectedVideo(null)}
                            style={{
                                position: "absolute",
                                top: 30,
                                right: 30,
                                width: 44,
                                height: 44,
                                borderRadius: "50%",
                                background: "rgba(255,255,255,0.10)",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                cursor: "pointer",
                                fontSize: 24,
                                color: WHITE,
                            }}
                        >
                            ×
                        </div>
                    </div>
                )}
            </div>
        </section>
    );
}
