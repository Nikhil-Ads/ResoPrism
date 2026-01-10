"use client";

import { useEffect, useRef } from "react";

export function AnimatedBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size with devicePixelRatio for crisp rendering
    const dpr = window.devicePixelRatio || 1;
    let width = window.innerWidth;
    let height = window.innerHeight;

    const resizeCanvas = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Create animated gradient orbs
    const orbs: Array<{
      x: number;
      y: number;
      radius: number;
      vx: number;
      vy: number;
      color: { r: number; g: number; b: number };
    }> = [];

    // Initialize gradient orbs with beautiful colors
    const orbCount = 5;
    for (let i = 0; i < orbCount; i++) {
      orbs.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 400 + 300,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        color: {
          r: Math.floor(i % 2 === 0 ? 96 + Math.random() * 60 : 59 + Math.random() * 40), // Blue range
          g: Math.floor(i % 2 === 0 ? 165 + Math.random() * 50 : 130 + Math.random() * 50), // Cyan-blue range
          b: Math.floor(238 + Math.random() * 17), // Cyan range
        },
      });
    }

    let animationFrame: number;
    let time = 0;

    const animate = () => {
      time += 0.005;
      
      // Clear with dark background - must use scaled coordinates
      ctx.fillStyle = "rgb(10, 10, 15)";
      ctx.fillRect(0, 0, width, height);

      // Update and draw orbs
      orbs.forEach((orb, index) => {
        // Update position with smooth movement
        orb.x += orb.vx;
        orb.y += orb.vy;

        // Bounce off edges
        if (orb.x < -orb.radius) orb.vx = Math.abs(orb.vx);
        if (orb.x > width + orb.radius) orb.vx = -Math.abs(orb.vx);
        if (orb.y < -orb.radius) orb.vy = Math.abs(orb.vy);
        if (orb.y > height + orb.radius) orb.vy = -Math.abs(orb.vy);

        // Add slight oscillation for organic movement
        const oscillationX = Math.sin(time * 0.5 + index) * 30;
        const oscillationY = Math.cos(time * 0.7 + index) * 30;

        const x = orb.x + oscillationX;
        const y = orb.y + oscillationY;

        // Create radial gradient
        const gradient = ctx.createRadialGradient(
          x,
          y,
          0,
          x,
          y,
          orb.radius
        );

        // Color stops with varying opacity for smooth blending
        const centerColor = `rgba(${orb.color.r}, ${orb.color.g}, ${orb.color.b}, 0.6)`;
        const midColor = `rgba(${orb.color.r}, ${orb.color.g}, ${orb.color.b}, 0.3)`;
        const edgeColor = `rgba(${orb.color.r}, ${orb.color.g}, ${orb.color.b}, 0)`;

        gradient.addColorStop(0, centerColor);
        gradient.addColorStop(0.5, midColor);
        gradient.addColorStop(1, edgeColor);

        // Draw orb with blur effect using shadow
        ctx.save();
        ctx.shadowBlur = 100;
        ctx.shadowColor = `rgba(${orb.color.r}, ${orb.color.g}, ${orb.color.b}, 0.5)`;
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, orb.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      // Draw connecting lines between nearby orbs for mesh effect
      for (let i = 0; i < orbs.length; i++) {
        for (let j = i + 1; j < orbs.length; j++) {
          const orb1 = orbs[i];
          const orb2 = orbs[j];
          const x1 = orb1.x + Math.sin(time * 0.5 + i) * 30;
          const y1 = orb1.y + Math.cos(time * 0.7 + i) * 30;
          const x2 = orb2.x + Math.sin(time * 0.5 + j) * 30;
          const y2 = orb2.y + Math.cos(time * 0.7 + j) * 30;
          const dx = x1 - x2;
          const dy = y1 - y2;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 600) {
            const opacity = (1 - distance / 600) * 0.2;
            ctx.strokeStyle = `rgba(96, 165, 250, ${opacity})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
          }
        }
      }

      animationFrame = requestAnimationFrame(animate);
    };

    // Start animation
    animationFrame = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationFrame);
    };
  }, []);

  return (
    <div 
      className="fixed inset-0 z-0 h-screen w-screen overflow-hidden" 
      style={{ backgroundColor: 'rgb(10, 10, 15)' }}
    >
      <canvas
        ref={canvasRef}
        className="h-full w-full"
        style={{
          pointerEvents: "none",
          display: "block",
          position: "absolute",
          inset: 0,
          zIndex: 1,
        }}
      />
    </div>
  );
}
