"use client";

import Link from "next/link";
import GradientText from "@/components/GradientText";
import { ArrowRight, Github } from "lucide-react";
import { AnimatedBackground } from "@/components/backgrounds/AnimatedBackground";
import { ScrollReveal } from "@/components/animations/ScrollReveal";
import { FeatureShowcase } from "@/components/sections/FeatureShowcase";
import { Footer } from "@/components/sections/Footer";
import { HowItWorksSection } from "@/components/sections/HowItWorksSection";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 relative overflow-hidden">
      {/* Animated gradient background orbs - similar to Numa */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div 
          className="absolute top-0 -left-1/4 w-[800px] h-[800px] bg-gradient-to-br from-teal-500/25 via-cyan-400/20 to-teal-400/25 rounded-full blur-3xl" 
          style={{ animation: 'pulse-slow 4s ease-in-out infinite' }}
        />
        <div 
          className="absolute top-1/3 -right-1/4 w-[700px] h-[700px] bg-gradient-to-br from-cyan-500/25 via-teal-400/20 to-cyan-400/25 rounded-full blur-3xl" 
          style={{ animation: 'pulse-slow-delay-1 5s ease-in-out infinite 1s' }}
        />
        <div 
          className="absolute bottom-0 left-1/3 w-[600px] h-[600px] bg-gradient-to-br from-teal-400/20 via-cyan-400/25 to-teal-300/20 rounded-full blur-3xl" 
          style={{ animation: 'pulse-slow-delay-2 6s ease-in-out infinite 2s' }}
        />
      </div>

      {/* Prism Background */}
      <AnimatedBackground />

      {/* Navigation */}
      <nav className="relative px-6 py-6 z-20">
        <div className="max-w-7xl mx-auto">
          <div className="bg-black/90 backdrop-blur-sm rounded-2xl border border-slate-800/50 px-6 py-3 flex items-center relative">
            {/* Logo - Top Left */}
            <div className="flex items-center gap-3 flex-shrink-0 absolute left-6">
              <GradientText
                colors={["#5eead4", "#67e8f9", "#40ffaa", "#67e8f9", "#5eead4"]}
                animationSpeed={4}
                showBorder={false}
                className="text-xl font-semibold tracking-tight"
              >
                ResoPrism
              </GradientText>
            </div>
            
            {/* Centered Navigation Links */}
            <div className="flex items-center gap-8 mx-auto">
              <Link href="#" className="text-sm text-slate-300 hover:text-teal-400 transition-colors">
                Home
              </Link>
              <Link href="#how-it-works" className="text-sm text-slate-300 hover:text-teal-400 transition-colors">
                How It Works
              </Link>
              <Link href="#features" className="text-sm text-slate-300 hover:text-teal-400 transition-colors">
                Features
              </Link>
              <Link href="/demo" className="text-sm text-slate-300 hover:text-teal-400 transition-colors">
                Demo
              </Link>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-slate-300 hover:text-teal-400 transition-colors flex items-center gap-1"
              >
                GitHub
                <Github className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-6 py-20 md:py-32 z-10">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <ScrollReveal direction="fade" delay={0.1}>
              <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-teal-500/15 via-cyan-500/15 to-teal-400/15 border border-teal-500/30 backdrop-blur-sm">
                <span className="w-2.5 h-2.5 rounded-full bg-gradient-to-r from-teal-400 to-cyan-400 animate-pulse shadow-lg shadow-teal-400/60" />
                <GradientText
                  colors={["#5eead4", "#67e8f9", "#40ffaa", "#67e8f9", "#5eead4"]}
                  animationSpeed={3}
                  showBorder={false}
                  className="text-sm font-medium"
                >
                  AI-Powered Research Inbox
                </GradientText>
              </div>
            </ScrollReveal>

            <ScrollReveal direction="down" delay={0.2}>
              <div className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight leading-tight">
                Your Intelligent
                <br />
                <GradientText
                  colors={["#5eead4", "#67e8f9", "#40ffaa", "#67e8f9", "#5eead4"]}
                  animationSpeed={3}
                  showBorder={false}
                  className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight"
                >
                  Research Assistant
                </GradientText>
              </div>
            </ScrollReveal>

            <ScrollReveal direction="up" delay={0.3}>
              <p className="text-xl md:text-2xl text-slate-300 max-w-2xl mx-auto leading-relaxed bg-gradient-to-r from-slate-300 to-slate-400 bg-clip-text text-transparent">
                Orchestrate data collection from grants, papers, and news sources
                with intelligent multi-agent coordination. Experience the future of research aggregation.
              </p>
            </ScrollReveal>

            <ScrollReveal direction="up" delay={0.4}>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-6">
                <Link
                  href="/demo"
                  className="glare-hover group rounded-xl bg-teal-500 px-8 py-4 text-base font-medium text-slate-950 hover:bg-teal-400 transition-all shadow-2xl shadow-teal-500/50 hover:shadow-teal-500/70 hover:scale-105 transform"
                >
                  <span className="flex items-center gap-2">
                    Explore Demo
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </Link>
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="glare-hover group rounded-xl border border-slate-700 bg-slate-900/80 px-8 py-4 text-base font-medium text-slate-100 hover:border-teal-500/50 hover:bg-slate-800/80 transition-all hover:scale-105 transform"
                >
                  <span className="flex items-center gap-2">
                    <Github className="w-5 h-5" />
                    View on GitHub
                  </span>
                </a>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <HowItWorksSection />

      {/* Features Section */}
      <section id="features" className="relative px-6 py-20 border-t border-slate-800/50 z-10">
        <FeatureShowcase />
      </section>

      {/* Footer */}
      <Footer />
    </main>
  );
}
