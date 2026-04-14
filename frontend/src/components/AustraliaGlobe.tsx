import { Canvas, useFrame, useLoader } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const TEX = "https://unpkg.com/three-globe@2.31.0/example/img";
const EARTH_MAP = `${TEX}/earth-blue-marble.jpg`;
const EARTH_BUMP = `${TEX}/earth-topology.png`;
const EARTH_SPEC = `${TEX}/earth-water.png`;
const CLOUDS = "https://threejs.org/examples/textures/planets/earth_clouds_1024.png";

// latitude/longitude of Australian cities
const CITIES: { name: string; lat: number; lon: number }[] = [
  { name: "SYD", lat: -33.87, lon: 151.21 },
  { name: "MEL", lat: -37.81, lon: 144.96 },
  { name: "BNE", lat: -27.47, lon: 153.03 },
  { name: "PER", lat: -31.95, lon: 115.86 },
  { name: "ADL", lat: -34.93, lon: 138.60 },
  { name: "DRW", lat: -12.46, lon: 130.84 },
];

const R = 2;

function latLonToVec3(lat: number, lon: number, radius = R) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta),
  );
}

function Earth() {
  const earthRef = useRef<THREE.Mesh>(null!);
  const cloudRef = useRef<THREE.Mesh>(null!);
  const groupRef = useRef<THREE.Group>(null!);

  const [map, bump, spec, clouds] = useLoader(THREE.TextureLoader, [
    EARTH_MAP, EARTH_BUMP, EARTH_SPEC, CLOUDS,
  ]);

  // point camera/view toward Australia: tilt group so Australia faces viewer
  const initialRotation = useMemo(() => {
    // rotate so that lon ≈ 135 (central Australia) is forward, lat ≈ -25 slightly tilted up
    return { y: -((135 + 180) * Math.PI) / 180, x: (-25 * Math.PI) / 180 };
  }, []);

  useFrame((_, d) => {
    if (earthRef.current) earthRef.current.rotation.y += d * 0.03;
    if (cloudRef.current) cloudRef.current.rotation.y += d * 0.045;
  });

  return (
    <group ref={groupRef} rotation={[initialRotation.x, 0, 0]}>
      <group rotation={[0, initialRotation.y, 0]}>
        {/* Earth */}
        <mesh ref={earthRef}>
          <sphereGeometry args={[R, 96, 96]} />
          <meshPhongMaterial
            map={map}
            bumpMap={bump}
            bumpScale={0.05}
            specularMap={spec}
            specular={new THREE.Color("#1a3a6b")}
            shininess={18}
          />
        </mesh>

        {/* Clouds */}
        <mesh ref={cloudRef}>
          <sphereGeometry args={[R * 1.01, 96, 96]} />
          <meshPhongMaterial map={clouds} transparent opacity={0.35} depthWrite={false} />
        </mesh>

        {/* City markers */}
        {CITIES.map((c) => {
          const v = latLonToVec3(c.lat, c.lon, R * 1.012);
          return (
            <group key={c.name} position={v.toArray()}>
              <mesh>
                <sphereGeometry args={[0.035, 16, 16]} />
                <meshBasicMaterial color="#22D3EE" />
              </mesh>
              <mesh>
                <sphereGeometry args={[0.07, 16, 16]} />
                <meshBasicMaterial color="#22D3EE" transparent opacity={0.25} />
              </mesh>
            </group>
          );
        })}
      </group>

      {/* Atmosphere (back-side shader-like glow via additive shell) */}
      <mesh scale={1.12}>
        <sphereGeometry args={[R, 64, 64]} />
        <shaderMaterial
          transparent
          side={THREE.BackSide}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          uniforms={{ uColor: { value: new THREE.Color("#2D7EF7") } }}
          vertexShader={`
            varying vec3 vNormal;
            void main() {
              vNormal = normalize(normalMatrix * normal);
              gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
          `}
          fragmentShader={`
            varying vec3 vNormal;
            uniform vec3 uColor;
            void main() {
              float intensity = pow(0.72 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 3.0);
              gl_FragColor = vec4(uColor, 1.0) * intensity;
            }
          `}
        />
      </mesh>
    </group>
  );
}

export function AustraliaGlobe() {
  return (
    <Canvas camera={{ position: [0, 0, 5.2], fov: 45 }} className="w-full h-full" dpr={[1, 2]}>
      <ambientLight intensity={0.25} />
      <directionalLight position={[5, 3, 5]} intensity={1.3} color="#ffffff" />
      <pointLight position={[-6, -2, -4]} intensity={0.4} color="#2D7EF7" />
      <Stars radius={80} depth={60} count={4000} factor={3} fade speed={0.6} />
      <Earth />
      <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.35} />
    </Canvas>
  );
}
