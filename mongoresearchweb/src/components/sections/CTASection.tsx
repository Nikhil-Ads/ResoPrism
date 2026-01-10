"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollReveal } from "@/components/animations/ScrollReveal";
import { motion } from "framer-motion";
import { useRef, useState, useEffect } from "react";

function MovingBorder({ children, className }: { children: React.ReactNode; className?: string }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const buttonRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!buttonRef.current) return;
    const rect = buttonRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setMousePosition({ x, y });
  };

  return (
    <motion.div
      ref={buttonRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`group relative overflow-hidden rounded-lg border-2 border-primary/20 bg-background p-[2px] transition-all duration-300 hover:border-primary/50 ${className}`}
    >
      {/* Animated gradient border */}
      <motion.div
        className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{
          background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.3), transparent 40%)`,
        }}
        animate={{
          background: isHovered
            ? `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.4), transparent 50%)`
            : `radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.1), transparent 70%)`,
        }}
      />

      {/* Content */}
      <div className="relative z-10 rounded-md bg-background/90 backdrop-blur-sm p-4">
        {children}
      </div>

      {/* Shimmer effect */}
      <motion.div
        className="absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-100"
        style={{
          background: "linear-gradient(105deg, transparent 40%, rgba(255, 255, 255, 0.05) 50%, transparent 60%)",
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
          repeat: Infinity,
          repeatDelay: 3,
        }}
      />
    </motion.div>
  );
}

function Spotlight({ className = "" }: { className?: string }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      setMousePosition({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <motion.div
        className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 hover:opacity-100"
        style={{
          background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.15), transparent 60%)`,
        }}
        animate={{
          background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.15), transparent 60%)`,
        }}
        transition={{ type: "tween", ease: "backOut", duration: 0.5 }}
      />
    </div>
  );
}

export function CTASection() {
  return (
    <section className="relative overflow-hidden border-t py-32 text-foreground" style={{ backgroundColor: 'hsl(0 0% 3.9%)' }}>
      <Spotlight className="absolute inset-0" />

      <div className="container relative z-10 mx-auto px-4">
        <div className="mx-auto max-w-4xl text-center">
          <ScrollReveal direction="down" delay={0.1}>
            <h2 className="mb-6 text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl">
              Ready to Transform Your
              <span className="block bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Research Workflow?
              </span>
            </h2>
          </ScrollReveal>

          <ScrollReveal direction="up" delay={0.2}>
            <p className="mb-12 text-xl text-muted-foreground md:text-2xl">
              Experience the power of AI-driven research aggregation. Get started
              with our interactive demo and see how MongoResearch can revolutionize
              your research process.
            </p>
          </ScrollReveal>

          <ScrollReveal direction="up" delay={0.3}>
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-6">
              <MovingBorder className="w-full sm:w-auto">
                <Button
                  asChild
                  size="lg"
                  className="group relative w-full overflow-hidden bg-primary text-base font-semibold text-primary-foreground transition-all duration-300 hover:bg-primary/90 sm:w-auto sm:text-lg"
                >
                  <Link href="/demo">
                    <span className="relative z-10">Try Demo Now</span>
                    <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
                  </Link>
                </Button>
              </MovingBorder>

              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-full sm:w-auto"
              >
                <Button
                  asChild
                  size="lg"
                  variant="outline"
                  className="w-full border-2 text-base font-semibold backdrop-blur-sm transition-all duration-300 hover:border-primary hover:bg-primary/10 sm:w-auto sm:text-lg"
                >
                  <a
                    href="https://github.com"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View Documentation
                  </a>
                </Button>
              </motion.div>
            </div>
          </ScrollReveal>

          {/* Additional info */}
          <ScrollReveal direction="fade" delay={0.4}>
            <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-green-500" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-blue-500" />
                <span>Free to explore</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-purple-500" />
                <span>Open source</span>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  );
}
