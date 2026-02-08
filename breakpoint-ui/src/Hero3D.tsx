<<<<<<< HEAD
import { Suspense, useEffect, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { useGLTF, useAnimations, Environment, OrbitControls } from "@react-three/drei";
import * as THREE from "three";

// ── Animated GLB Model ──
function PingPongModel() {
  const group = useRef<THREE.Group>(null);
  const { scene, animations } = useGLTF("/table_tennis_animation_ping_pong.glb");
  const { actions } = useAnimations(animations, group);

  useEffect(() => {
    // Play all animations in the GLB
    if (actions) {
      Object.values(actions).forEach((action) => {
        if (action) {
          action.reset().fadeIn(0.5).play();
          action.setLoop(THREE.LoopRepeat, Infinity);
        }
      });
    }
  }, [actions]);

  // No rotation - keep model straight

  return (
    <group ref={group} dispose={null}>
      <primitive object={scene} scale={0.5} position={[-0.8, -0.5, 0]} rotation={[0, Math.PI / 2, 0]} />
    </group>
  );
}

// ── Static camera ──
function CameraRig() {
  useFrame(({ camera }) => {
    camera.position.set(0, 2.0, 4.5);
    camera.lookAt(0, 0.3, 0);
  });
  return null;
}

// ── Loading spinner ──
function Loader() {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          width: 40,
          height: 40,
          border: "3px solid rgba(16,185,160,0.15)",
          borderTop: "3px solid rgba(16,185,160,0.80)",
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
        }}
      />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

// ── Main Hero ──
=======
import { PingPongScene3D } from "./scene/PingPongScene";

>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
export function Hero3D({ onNext }: { onNext: () => void }) {
  return (
    <div
      style={{
        position: "relative",
        height: "100vh",
        width: "100%",
<<<<<<< HEAD
        background: "#000000",
=======
        background: "#050506",
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
        overflow: "hidden",
      }}
    >
      {/* Subtle background glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
<<<<<<< HEAD
            "radial-gradient(700px 320px at 50% 35%, rgba(255,255,255,0.05), transparent 60%)," +
            "radial-gradient(900px 520px at 50% 70%, rgba(255,255,255,0.03), transparent 60%)",
=======
            "radial-gradient(700px 320px at 50% 35%, rgba(255,0,60,0.10), transparent 60%)," +
            "radial-gradient(900px 520px at 50% 70%, rgba(255,255,255,0.04), transparent 60%)",
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
          pointerEvents: "none",
        }}
      />

<<<<<<< HEAD
      {/* 3D Animated GLB Stage */}
=======
      {/* 3D STAGE (smaller, clipped, background) */}
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
      <div
        style={{
          position: "absolute",
          left: "50%",
<<<<<<< HEAD
          top: "45%",
          transform: "translate(-50%, -50%)",
          width: "min(1200px, 95vw)",
          height: "min(600px, 65vh)",
          borderRadius: 30,
          overflow: "hidden",
        }}
      >
        <Suspense fallback={<Loader />}>
          <Canvas
            shadows
            dpr={[1, 2]}
            camera={{ fov: 40, position: [0, 2.0, 4.5] }}
            gl={{ antialias: true, alpha: true }}
            style={{ background: "transparent" }}
          >
            <ambientLight intensity={0.5} />
            <directionalLight
              position={[3, 4, 2]}
              intensity={1.2}
              castShadow
              shadow-mapSize-width={2048}
              shadow-mapSize-height={2048}
            />
            <spotLight
              position={[-2, 3, -1]}
              intensity={0.8}
              angle={0.4}
              penumbra={0.6}
            />

            <PingPongModel />

            {/* Floor */}
            <mesh
              rotation={[-Math.PI / 2, 0, 0]}
              position={[0, -0.5, 0]}
              receiveShadow
            >
              <planeGeometry args={[20, 20]} />
              <meshStandardMaterial
                color="#000000"
                roughness={0.9}
                transparent
                opacity={0.6}
              />
            </mesh>

            <Environment preset="city" />
            <CameraRig />
          </Canvas>
        </Suspense>

        {/* Bottom fade so 3D blends into UI */}
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: 120,
            background:
              "linear-gradient(to top, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)",
=======
          top: "60%",
          transform: "translate(-50%, -50%) scale(0.98)",
          width: "min(1100px, 92vw)",
          height: "min(560px, 62vh)",
          borderRadius: 26,
          overflow: "hidden",
          opacity: 0.34, // <-- background feel
          filter: "blur(0.6px)",
          boxShadow: "0 50px 140px rgba(0,0,0,0.75)",
          border: "1px solid rgba(255,255,255,0.06)",
          pointerEvents: "none",
        }}
      >
        <PingPongScene3D />

        {/* cinematic fade/vignette so 3D blends into UI */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(to top, rgba(5,5,6,0.0) 40%, rgba(5,5,6,0.85) 85%, rgba(5,5,6,1) 100%)," +
              "radial-gradient(70% 60% at 50% 60%, rgba(0,0,0,0.0), rgba(0,0,0,0.75) 70%)",
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
            pointerEvents: "none",
          }}
        />
      </div>

      {/* UI overlay */}
<<<<<<< HEAD
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
        {/* Top center brand with animation */}
=======
      <div style={{ position: "absolute", inset: 0 }}>
        {/* Top center brand */}
        <div
  style={{
    position: "absolute",
    top: 22,
    left: "50%",
    transform: "translateX(-50%)",
    fontSize: 28,                 // bigger
    fontWeight: 900,
    letterSpacing: "0.10em",
    color: "rgba(255,255,255,0.96)",
  }}
>
  Break Point
</div>

        {/* Top right pill */}
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
        <div
          style={{
            position: "absolute",
            top: 22,
<<<<<<< HEAD
            left: "50%",
            transform: "translateX(-50%)",
            fontSize: 48,
            fontWeight: 900,
            letterSpacing: "0.12em",
            color: "#ffffff",
            pointerEvents: "auto",
            animation: "fadeInDown 0.8s ease-out",
          }}
        >
          BREAK POINT
        </div>

        {/* Score positioned near the 3D model */}
        <div
          style={{
            position: "absolute",
            bottom: 220,
            left: "50%",
            transform: "translateX(-50%)",
            textAlign: "center",
            pointerEvents: "auto",
            animation: "fadeIn 1s ease-out 0.3s both",
          }}
        >
          <div
            style={{
              fontSize: 64,
              fontWeight: 900,
              opacity: 0.92,
              lineHeight: 1,
              color: "#ffffff",
=======
            right: 36,
            border: "1px solid rgba(255,0,60,0.55)",
            color: "rgba(255,0,60,0.95)",
            padding: "10px 14px",
            borderRadius: 999,
            fontSize: 12,
            letterSpacing: "0.15em",
            fontWeight: 700,
            background: "rgba(0,0,0,0.15)",
            backdropFilter: "blur(8px)",
          }}
        >
          LIVE ANALYSIS
        </div>

        {/* Center content */}
        <div
          style={{
            position: "absolute",
            top: 140,
            left: 0,
            right: 0,
            textAlign: "center",
            padding: "0 18px",
          }}
        >
          {/* Score smaller */}
          <div
            style={{
              fontSize: 84,
              fontWeight: 900,
              opacity: 0.92,
              lineHeight: 1,
              color: "rgba(255,255,255,0.94)",
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
            }}
          >
            10 <span style={{ opacity: 0.22 }}>–</span>{" "}
            <span style={{ opacity: 0.50 }}>9</span>
          </div>
<<<<<<< HEAD
        </div>

        {/* Subtitle */}
        <div
          style={{
            position: "absolute",
            top: 110,
            left: 0,
            right: 0,
            textAlign: "center",
            padding: "0 18px",
            pointerEvents: "auto",
            animation: "fadeIn 1s ease-out 0.5s both",
          }}
        >
          <div
            style={{
              fontSize: 18,
              color: "rgba(255,255,255,0.55)",
              maxWidth: 500,
              margin: "0 auto",
              lineHeight: 1.6,
            }}
          >
            AI-powered performance coaching for individual sports. We analyze match video to turn mistakes, pressure patterns, and hesitation into clear, actionable winning advice.
          </div>
=======

          {/* Break point badge */}
          <div
            style={{
              display: "inline-flex",
              marginTop: 10,
              padding: "8px 14px",
              borderRadius: 999,
              background: "rgba(255,0,60,0.92)",
              color: "rgba(255,255,255,0.95)",
              fontWeight: 900,
              letterSpacing: "0.22em",
              fontSize: 11,
            }}
          >
            BREAK POINT
          </div>

          {/* Product one-liner (judge-friendly) */}
          

          {/* Micro-metrics (optional but makes it look premium) */}
          
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
        </div>

        {/* Bottom hint */}
        <div
          onClick={onNext}
          style={{
            position: "absolute",
            bottom: 28,
            left: 0,
            right: 0,
            textAlign: "center",
            fontSize: 12,
            letterSpacing: "0.35em",
            opacity: 0.42,
            cursor: "pointer",
            userSelect: "none",
<<<<<<< HEAD
            color: "rgba(255,255,255,0.55)",
            pointerEvents: "auto",
            animation: "fadeIn 1s ease-out 0.7s both",
=======
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
          }}
        >
          SCROLL TO ANALYZE
        </div>
<<<<<<< HEAD

        {/* Animations */}
        <style>{`
          @keyframes fadeInDown {
            from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
            to { opacity: 1; transform: translateX(-50%) translateY(0); }
          }
          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }
        `}</style>
=======
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
      </div>
    </div>
  );
}

<<<<<<< HEAD
// Preload the GLB
useGLTF.preload("/table_tennis_animation_ping_pong.glb");
=======
function Metric({
  title,
  value,
  accent,
}: {
  title: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div
      style={{
        padding: "10px 14px",
        borderRadius: 14,
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.08)",
        minWidth: 175,
        textAlign: "left",
        backdropFilter: "blur(10px)",
      }}
    >
      <div
        style={{
          fontSize: 11,
          letterSpacing: "0.18em",
          color: "rgba(255,255,255,0.45)",
          fontWeight: 700,
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontSize: 16,
          fontWeight: 900,
          marginTop: 4,
          color: accent ? "rgba(255,0,60,0.95)" : "rgba(255,255,255,0.90)",
        }}
      >
        {value}
      </div>
    </div>
  );
}
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
