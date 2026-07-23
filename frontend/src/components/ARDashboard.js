import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { ARCanvas, ARMarker } from '@react-three/xr';
import Portfolio3D from './Portfolio3D';

const ARDashboard = () => {
  return (
    <ARCanvas>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <Suspense fallback={null}>
        <ARMarker type="pattern" patternUrl="/data/hiro.patt">
          <Portfolio3D />
        </ARMarker>
      </Suspense>
    </ARCanvas>
  );
};

export default ARDashboard;