import React, { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Box, Text } from '@react-three/drei';
import * as THREE from 'three';
import type { VolatilitySurface } from '../types/volatility';

interface VolatilitySurface3DProps {
  surface: VolatilitySurface | null;
}

function SurfaceMesh({ surface }: { surface: VolatilitySurface }) {
  const meshRef = useRef<THREE.Mesh>(null);

  const geometry = useMemo(() => {
    if (!surface?.atmVols) return null;

    const tenors = ['1W', '2W', '1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y'];
    const strikes = 21; // Number of strike points
    const timePoints = tenors.length;
    
    const geo = new THREE.PlaneGeometry(10, 8, strikes - 1, timePoints - 1);
    const positions = geo.attributes.position.array as Float32Array;
    
    // Map tenors to time values
    const timeValues: Record<string, number> = {
      '1W': 1/52, '2W': 2/52, '1M': 1/12, '2M': 2/12, '3M': 3/12,
      '6M': 6/12, '9M': 9/12, '1Y': 1, '2Y': 2, '3Y': 3, '5Y': 5
    };
    
    let vertexIndex = 0;
    for (let j = 0; j < timePoints; j++) {
      const tenor = tenors[j];
      const atmVol = surface.atmVols[tenor] || 0;
      const rr25 = surface.riskReversals['25D']?.[tenor] || 0;
      const bf25 = surface.butterflies['25D']?.[tenor] || 0;
      
      for (let i = 0; i < strikes; i++) {
        const strike = -0.3 + (0.6 * i / (strikes - 1)); // -30% to +30% moneyness
        
        // Calculate volatility using smile approximation
        let vol = atmVol;
        if (Math.abs(strike - 0.25) < 0.01) {
          vol = atmVol + bf25 + rr25/2; // 25D call
        } else if (Math.abs(strike + 0.25) < 0.01) {
          vol = atmVol + bf25 - rr25/2; // 25D put
        } else if (strike !== 0) {
          // Smooth interpolation
          const x = strike;
          const y1 = atmVol + bf25 - rr25/2; // 25D put
          const y2 = atmVol; // ATM
          const y3 = atmVol + bf25 + rr25/2; // 25D call
          
          if (x < -0.25) {
            vol = y1 + (y1 - y2) * (x + 0.25) / 0.25 * 0.5;
          } else if (x > 0.25) {
            vol = y3 + (y3 - y2) * (x - 0.25) / 0.25 * 0.5;
          } else {
            // Quadratic interpolation in the middle
            const t = (x + 0.25) / 0.5;
            if (t < 0.5) {
              const localT = t * 2;
              vol = y1 * (1 - localT) + y2 * localT;
            } else {
              const localT = (t - 0.5) * 2;
              vol = y2 * (1 - localT) + y3 * localT;
            }
          }
        }
        
        // Set Z position based on volatility
        positions[vertexIndex * 3 + 2] = (vol - 5) * 0.3;
        vertexIndex++;
      }
    }
    
    geo.computeVertexNormals();
    
    // Add vertex colors
    const colors = new Float32Array(positions.length);
    for (let i = 0; i < positions.length; i += 3) {
      const z = positions[i + 2];
      const normalized = (z + 1.5) / 3;
      
      // Color gradient: blue -> green -> yellow -> red
      const color = new THREE.Color();
      color.setHSL(0.7 - normalized * 0.7, 1, 0.5);
      
      colors[i] = color.r;
      colors[i + 1] = color.g;
      colors[i + 2] = color.b;
    }
    
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    
    return geo;
  }, [surface]);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.1) * 0.02;
    }
  });

  if (!geometry) return null;

  return (
    <mesh
      ref={meshRef}
      geometry={geometry}
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, 0, 0]}
    >
      <meshPhongMaterial
        vertexColors
        side={THREE.DoubleSide}
        shininess={100}
        wireframe={false}
      />
    </mesh>
  );
}

export function VolatilitySurface3D({ surface }: VolatilitySurface3DProps) {
  if (!surface) {
    return (
      <div style={{ 
        width: '100%', 
        height: '600px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: '#0a0a0a',
        color: '#888'
      }}>
        Loading volatility surface...
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '600px', position: 'relative' }}>
      <Canvas
        camera={{ position: [12, 10, 12], fov: 45 }}
        style={{ background: 'linear-gradient(to bottom, #0a0a0a, #1a1a2e)' }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <directionalLight position={[-10, 10, -5]} intensity={0.5} />
        
        <SurfaceMesh surface={surface} />
        
        <gridHelper args={[10, 10, 0x444444, 0x222222]} position={[0, -2, 0]} />
        <axesHelper args={[6]} />
        
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          minDistance={5}
          maxDistance={30}
        />
      </Canvas>
      
      {/* Data overlay */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        background: 'rgba(0,0,0,0.9)',
        color: '#00ff41',
        padding: '15px',
        borderRadius: '8px',
        fontSize: '12px',
        fontFamily: 'monospace',
        border: '1px solid #00ff41',
        boxShadow: '0 0 20px rgba(0, 255, 65, 0.3)'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
          {surface.pair} VOLATILITY SURFACE
        </div>
        <div>SPOT: {surface.spot?.spot.toFixed(4)}</div>
        <div>ATM 1M: {surface.atmVols['1M']?.toFixed(2)}%</div>
        <div>25Δ RR 1M: {surface.riskReversals['25D']?.['1M']?.toFixed(3)}</div>
        <div>25Δ BF 1M: {surface.butterflies['25D']?.['1M']?.toFixed(3)}</div>
        <div style={{ marginTop: '8px', fontSize: '10px', color: '#888' }}>
          Live Bloomberg Terminal Data
        </div>
      </div>
    </div>
  );
}