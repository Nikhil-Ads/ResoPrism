"use client";

import { useRef, useState, useEffect } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface AnimatedFeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  delay?: number;
}

export function AnimatedFeatureCard({
  icon: Icon,
  title,
  description,
  delay = 0,
}: AnimatedFeatureCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  // Optimized spring settings for better performance
  const [isMobile, setIsMobile] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  // Check for mobile and reduced motion on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsMobile(window.innerWidth < 768);
      setPrefersReducedMotion(
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      );
    }
  }, []);

  const springConfig = isMobile || prefersReducedMotion
    ? { stiffness: 300, damping: 80 }
    : { stiffness: 500, damping: 100 };

  const mouseXSpring = useSpring(x, springConfig);
  const mouseYSpring = useSpring(y, springConfig);

  // Reduced rotation on mobile or reduced motion for better performance
  const maxRotation = isMobile || prefersReducedMotion ? 2 : 7.5;
  
  const rotateX = useTransform(
    mouseYSpring,
    [-0.5, 0.5],
    prefersReducedMotion ? ["0deg", "0deg"] : [`${maxRotation}deg`, `-${maxRotation}deg`]
  );
  const rotateY = useTransform(
    mouseXSpring,
    [-0.5, 0.5],
    prefersReducedMotion ? ["0deg", "0deg"] : [`-${maxRotation}deg`, `${maxRotation}deg`]
  );

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;

    const rect = ref.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;

    x.set(xPct);
    y.set(yPct);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
    setIsHovered(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.5, delay }}
      className="group relative h-full"
    >
      <motion.div
        ref={ref}
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={handleMouseLeave}
        style={{
          rotateX,
          rotateY,
          transformStyle: "preserve-3d",
        }}
        className="relative h-full"
      >
        <Card className="relative h-full overflow-hidden border-2 bg-card/50 backdrop-blur-sm transition-all duration-300 hover:border-primary/50 hover:shadow-2xl hover:shadow-primary/20">
          {/* Glow effect on hover */}
          <motion.div
            className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
            style={{
              background: "radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.1), transparent 70%)",
            }}
          />

          <CardHeader className="relative z-10">
            <motion.div
              className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10 transition-all duration-300 group-hover:scale-110 group-hover:bg-primary/20"
              whileHover={{ rotate: [0, -10, 10, -10, 0] }}
              transition={{ duration: 0.5 }}
            >
              <Icon className="h-7 w-7 text-primary transition-colors duration-300 group-hover:text-primary" />
            </motion.div>

            <CardTitle className="text-xl font-bold tracking-tight transition-colors duration-300 group-hover:text-primary">
              {title}
            </CardTitle>
            <CardDescription className="mt-2 text-base leading-relaxed">
              {description}
            </CardDescription>
          </CardHeader>

          <CardContent className="relative z-10">
            {/* Spacer for content */}
          </CardContent>

          {/* Shine effect on hover */}
          <motion.div
            className="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100"
            style={{
              background: "linear-gradient(105deg, transparent 40%, rgba(255, 255, 255, 0.1) 50%, transparent 60%)",
              transform: "translateX(-100%)",
            }}
            animate={
              isHovered
                ? {
                    transform: "translateX(100%)",
                  }
                : {}
            }
            transition={{
              duration: 0.6,
              ease: "easeInOut",
            }}
          />
        </Card>
      </motion.div>
    </motion.div>
  );
}
