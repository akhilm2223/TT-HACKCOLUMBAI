import * as THREE from "three";
import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Environment } from "@react-three/drei";

type PlayerSide = "near" | "far";

function clamp01(x: number) {
  return Math.max(0, Math.min(1, x));
}

function BallRally() {
  const ballRef = useRef<THREE.Mesh>(null);
  const nearPaddleRef = useRef<THREE.Group>(null);
  const farPaddleRef = useRef<THREE.Group>(null);

  const curves = useMemo(() => {
    const nearToFar = new THREE.CatmullRomCurve3(
      [
        new THREE.Vector3(0.08, 0.10, 0.55),
        new THREE.Vector3(0.15, 0.22, 0.25),
        new THREE.Vector3(-0.18, 0.26, -0.10),
        new THREE.Vector3(-0.10, 0.12, -0.55),
      ],
      false, "catmullrom", 0.35
    );
    const farToNear = new THREE.CatmullRomCurve3(
      [
        new THREE.Vector3(-0.10, 0.12, -0.55),
        new THREE.Vector3(-0.18, 0.23, -0.20),
        new THREE.Vector3(0.22, 0.28, 0.05),
        new THREE.Vector3(0.10, 0.11, 0.55),
      ],
      false, "catmullrom", 0.35
    );
    return { nearToFar, farToNear };
  }, []);

  const speed = 0.38;

  useFrame((state) => {
    const t = (state.clock.elapsedTime * speed) % 1;
    const isFirstHalf = t < 0.5;
    const u = isFirstHalf ? t / 0.5 : (t - 0.5) / 0.5;
    const curve = isFirstHalf ? curves.nearToFar : curves.farToNear;
    const p = curve.getPoint(clamp01(u));
    const wobble = Math.sin(state.clock.elapsedTime * 7.0) * 0.005;
    const heightPulse = Math.sin(u * Math.PI) * 0.03;
    p.y = p.y + heightPulse + wobble;
    if (ballRef.current) ballRef.current.position.copy(p);

    const hitWindow = 0.10;
    const hitStrength = 0.85;
    const hitPhase = 1 - Math.min(1, u / hitWindow);
    const swing = Math.sin(hitPhase * Math.PI) * hitStrength;

    if (nearPaddleRef.current) {
      const s = isFirstHalf ? swing : 0;
      nearPaddleRef.current.rotation.y = 0.25 + s * 0.55;
      nearPaddleRef.current.rotation.x = -0.10 + s * 0.15;
    }
    if (farPaddleRef.current) {
      const s = !isFirstHalf ? swing : 0;
      farPaddleRef.current.rotation.y = -0.25 - s * 0.55;
      farPaddleRef.current.rotation.x = -0.10 + s * 0.15;
    }
  });

  return (
    <>
      <mesh ref={ballRef} castShadow>
        <sphereGeometry args={[0.018, 24, 24]} />
        <meshStandardMaterial color={"#ffffff"} roughness={0.25} metalness={0.05} />
      </mesh>

      {/* Near paddle - teal */}
      <group ref={nearPaddleRef} position={[0.22, 0.16, 0.62]}>
        <mesh castShadow>
          <boxGeometry args={[0.06, 0.08, 0.01]} />
          <meshStandardMaterial color={"#10b9a0"} roughness={0.35} />
        </mesh>
        <mesh position={[0, -0.06, 0]} castShadow>
          <cylinderGeometry args={[0.008, 0.008, 0.07, 16]} />
          <meshStandardMaterial color={"#cfcfd2"} roughness={0.55} />
        </mesh>
      </group>

      {/* Far paddle - lighter teal */}
      <group ref={farPaddleRef} position={[-0.20, 0.18, -0.62]}>
        <mesh castShadow>
          <boxGeometry args={[0.06, 0.08, 0.01]} />
          <meshStandardMaterial color={"#2b8ccc"} roughness={0.35} />
        </mesh>
        <mesh position={[0, -0.06, 0]} castShadow>
          <cylinderGeometry args={[0.008, 0.008, 0.07, 16]} />
          <meshStandardMaterial color={"#cfcfd2"} roughness={0.55} />
        </mesh>
      </group>
    </>
  );
}

function Player({ side }: { side: PlayerSide }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (!groupRef.current) return;
    const baseZ = side === "near" ? 0.70 : -0.70;
    const baseX = side === "near" ? 0.18 : -0.18;
    const sway = Math.sin(t * 1.6 + (side === "near" ? 0 : 1)) * 0.03;
    const lean = Math.sin(t * 1.4) * 0.05;
    groupRef.current.position.set(baseX + sway * 0.6, 0.0, baseZ);
    groupRef.current.rotation.y = side === "near" ? Math.PI : 0;
    groupRef.current.rotation.x = lean * 0.08;
  });

  const color = side === "near" ? "#e8e8ea" : "#80848e";

  return (
    <group ref={groupRef}>
      <mesh position={[0.03, 0.07, 0]} castShadow>
        <capsuleGeometry args={[0.028, 0.08, 8, 16]} />
        <meshStandardMaterial color={color} roughness={0.7} />
      </mesh>
      <mesh position={[-0.03, 0.07, 0]} castShadow>
        <capsuleGeometry args={[0.028, 0.08, 8, 16]} />
        <meshStandardMaterial color={color} roughness={0.7} />
      </mesh>
      <mesh position={[0, 0.18, 0]} castShadow>
        <capsuleGeometry args={[0.05, 0.12, 8, 16]} />
        <meshStandardMaterial color={color} roughness={0.65} />
      </mesh>
      <mesh position={[0, 0.30, 0]} castShadow>
        <sphereGeometry args={[0.045, 24, 24]} />
        <meshStandardMaterial color={color} roughness={0.6} />
      </mesh>
    </group>
  );
}

function Table() {
  return (
    <group position={[0, 0, 0]}>
      {/* Table top - dark teal */}
      <mesh position={[0, 0.12, 0]} receiveShadow castShadow>
        <boxGeometry args={[1.10, 0.03, 2.00]} />
        <meshStandardMaterial color={"#0e3d3a"} roughness={0.35} metalness={0.05} />
      </mesh>
      {/* White edges */}
      <mesh position={[0, 0.135, 0]}>
        <boxGeometry args={[1.115, 0.003, 2.015]} />
        <meshStandardMaterial color={"#e9e9ea"} roughness={0.2} />
      </mesh>
      {/* Center line */}
      <mesh position={[0, 0.137, 0]}>
        <boxGeometry args={[1.08, 0.002, 0.006]} />
        <meshStandardMaterial color={"#e9e9ea"} />
      </mesh>
      {/* Net */}
      <mesh position={[0, 0.18, 0]} castShadow>
        <boxGeometry args={[1.10, 0.06, 0.01]} />
        <meshStandardMaterial color={"#2a3840"} roughness={0.85} />
      </mesh>
      {/* Legs */}
      {[[0.45, 0.80], [-0.45, 0.80], [0.45, -0.80], [-0.45, -0.80]].map(([x, z], i) => (
        <mesh key={i} position={[x, 0.05, z]} castShadow>
          <boxGeometry args={[0.04, 0.10, 0.04]} />
          <meshStandardMaterial color={"#1a2a28"} roughness={0.7} />
        </mesh>
      ))}
    </group>
  );
}

function SceneRig() {
  useFrame(({ camera, clock }) => {
    const t = clock.elapsedTime;
    camera.position.x = Math.sin(t * 0.15) * 0.06;
    camera.position.y = 0.90 + Math.sin(t * 0.12) * 0.02;
    camera.position.z = 2.20 + Math.cos(t * 0.10) * 0.03;
    camera.lookAt(0, 0.18, 0);
  });
  return null;
}

export function PingPongScene3D() {
  return (
    <Canvas
      shadows
      dpr={[1, 2]}
      camera={{ fov: 36, position: [0, 0.95, 2.25] }}
      gl={{ antialias: true }}
    >
      <ambientLight intensity={0.45} />
      <directionalLight
        position={[2.5, 3.2, 1.8]}
        intensity={1.4}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      <spotLight position={[-2, 2.8, -1.5]} intensity={0.9} angle={0.35} penumbra={0.7} />

      {/* Light floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color={"#e8eaed"} roughness={0.9} />
      </mesh>

      <Table />
      <Player side="near" />
      <Player side="far" />
      <BallRally />

      <Environment preset="city" />
      <SceneRig />
    </Canvas>
  );
}
