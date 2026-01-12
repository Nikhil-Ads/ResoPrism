"use client";

import Prism from "./Prism";

export function AnimatedBackground() {
  return (
    <div 
      className="fixed inset-0 z-0 h-screen w-screen overflow-hidden" 
      style={{ backgroundColor: 'rgb(10, 10, 15)' }}
    >
      <div style={{ width: '100%', height: '100%', position: 'relative' }}>
        <Prism
          animationType="rotate"
          timeScale={0.5}
          height={3.5}
          baseWidth={5.5}
          scale={3.6}
          hueShift={0}
          colorFrequency={1}
          noise={0}
          glow={1}
          transparent={true}
        />
      </div>
    </div>
  );
}
