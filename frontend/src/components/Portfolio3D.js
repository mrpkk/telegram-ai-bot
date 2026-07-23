import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const Portfolio3D = () => {
  const group = useRef();
  
  useFrame(() => {
    if (group.current) {
      group.current.rotation.y += 0.01;
    }
  });
  
  return (
    <group ref={group}>
      {/* Ethereum */}
      <mesh position={[-2, 0, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="#627EEA" />
      </mesh>
      
      {/* Solana */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.7, 32, 32]} />
        <meshStandardMaterial color="#9945FF" />
      </mesh>
      
      {/* TON */}
      <mesh position={[2, 0, 0]}>
        <coneGeometry args={[0.7, 1, 32]} />
        <meshStandardMaterial color="#0098EA" />
      </mesh>
    </group>
  );
};

export default Portfolio3D;