"use client";

import { useRef, useEffect, useState, ReactNode } from "react";
import { motion, useInView, useAnimation, Variants } from "framer-motion";

interface ScrollRevealProps {
  children: ReactNode;
  delay?: number;
  direction?: "up" | "down" | "left" | "right" | "fade";
  className?: string;
  amount?: number;
}

function prefersReducedMotion() {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

const variants: Record<string, Variants> = {
  up: {
    hidden: { opacity: 0, y: 75 },
    visible: { opacity: 1, y: 0 },
  },
  down: {
    hidden: { opacity: 0, y: -75 },
    visible: { opacity: 1, y: 0 },
  },
  left: {
    hidden: { opacity: 0, x: 75 },
    visible: { opacity: 1, x: 0 },
  },
  right: {
    hidden: { opacity: 0, x: -75 },
    visible: { opacity: 1, x: 0 },
  },
  fade: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  },
};

export function ScrollReveal({
  children,
  delay = 0,
  direction = "up",
  className = "",
  amount = 0.1,
}: ScrollRevealProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount });
  const controls = useAnimation();
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    setReducedMotion(prefersReducedMotion());
    if (isInView) {
      controls.start("visible");
    }
  }, [isInView, controls]);

  // For reduced motion, show immediately without animation
  if (reducedMotion && isInView) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={controls}
      variants={variants[direction]}
      transition={{
        duration: reducedMotion ? 0 : 0.6,
        delay: reducedMotion ? 0 : delay,
        ease: [0.21, 1.11, 0.81, 0.99],
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
