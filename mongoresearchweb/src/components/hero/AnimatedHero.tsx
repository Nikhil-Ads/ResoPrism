"use client";

import Link from "next/link";
import { ArrowRight, Github } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AnimatedBackground } from "@/components/backgrounds/AnimatedBackground";
import { TextGenerateEffect } from "@/components/animations/TextGenerateEffect";
import { ScrollReveal } from "@/components/animations/ScrollReveal";
import { motion } from "framer-motion";

export function AnimatedHero() {
  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden border-b text-foreground" style={{ background: 'transparent' }}>
      <AnimatedBackground />

      <div className="container relative z-30 mx-auto px-4 py-24 md:py-32">
        <div className="mx-auto max-w-5xl text-center">
          {/* Badge */}
          <ScrollReveal direction="fade" delay={0.1}>
            <Badge
              className="mb-6 border-2 border-primary/20 bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary backdrop-blur-sm"
              variant="secondary"
            >
              LangGraph Multi-Agent System
            </Badge>
          </ScrollReveal>

          {/* Main Heading */}
          <ScrollReveal direction="down" delay={0.2}>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="mb-6 text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl"
            >
              <span 
                className="inline-block bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-500 bg-clip-text text-transparent"
                style={{
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  color: 'transparent',
                  backgroundImage: 'linear-gradient(to right, rgb(96 165 250), rgb(34 211 238), rgb(59 130 246))',
                }}
              >
                MongoResearch
              </span>
            </motion.h1>
          </ScrollReveal>

          {/* Subheading with Text Generate Effect */}
          <ScrollReveal direction="up" delay={0.4}>
            <div className="mb-8">
              <TextGenerateEffect
                words="AI-Powered Research Inbox that orchestrates data collection from grants, papers, and news sources with intelligent multi-agent coordination."
                className="mx-auto max-w-3xl text-xl text-muted-foreground sm:text-2xl md:text-3xl [&>*]:text-muted-foreground"
                duration={0.08}
              />
            </div>
          </ScrollReveal>

          {/* CTA Buttons */}
          <ScrollReveal direction="up" delay={0.6}>
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  asChild
                  size="lg"
                  className="group relative overflow-hidden bg-primary text-lg font-semibold text-primary-foreground transition-all duration-300 hover:bg-primary/90"
                >
                  <Link href="/demo">
                    Explore Demo
                    <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
                  </Link>
                </Button>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  asChild
                  size="lg"
                  variant="outline"
                  className="group border-2 text-lg font-semibold backdrop-blur-sm transition-all duration-300 hover:border-primary hover:bg-primary/10"
                >
                  <a
                    href="https://github.com"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Github className="mr-2 h-5 w-5 transition-transform duration-300 group-hover:rotate-12" />
                    View on GitHub
                  </a>
                </Button>
              </motion.div>
            </div>
          </ScrollReveal>

          {/* Scroll Indicator */}
          <ScrollReveal direction="fade" delay={0.8}>
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="absolute bottom-8 left-1/2 -translate-x-1/2"
            >
              <div className="flex flex-col items-center gap-2 text-muted-foreground">
                <span className="text-sm font-medium">Scroll to explore</span>
                <motion.div
                  animate={{ y: [0, 5, 0] }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                >
                  <svg
                    className="h-6 w-6"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </motion.div>
              </div>
            </motion.div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  );
}
