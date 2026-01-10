"use client";

import { useEffect, useRef, useState } from "react";

interface GradientTextProps {
  colors: string[];
  animationSpeed?: number;
  showBorder?: boolean;
  className?: string;
  children: React.ReactNode;
}

export default function GradientText({
  colors,
  animationSpeed = 3,
  showBorder = false,
  className = "",
  children,
}: GradientTextProps) {
  const textRef = useRef<HTMLSpanElement>(null);
  const [gradientId] = useState(() => `gradient-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    if (!textRef.current) return;

    const style = document.createElement("style");
    style.textContent = `
      @keyframes gradient-shift-${gradientId} {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
      }
      
      .gradient-text-${gradientId} {
        background: linear-gradient(90deg, ${colors.join(", ")});
        background-size: 200% auto;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift-${gradientId} ${animationSpeed}s ease infinite;
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, [colors, animationSpeed, gradientId]);

  return (
    <span
      ref={textRef}
      className={`gradient-text-${gradientId} ${className} ${showBorder ? "border border-current" : ""}`}
    >
      {children}
    </span>
  );
}
