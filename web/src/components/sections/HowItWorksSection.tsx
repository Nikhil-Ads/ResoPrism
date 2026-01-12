"use client";

import { Search, Network, BarChart3 } from "lucide-react";
import { ScrollReveal } from "@/components/animations/ScrollReveal";
import GradientText from "@/components/GradientText";

const steps = [
  {
    icon: Search,
    title: "Enter Query / Lab URL",
    description: "Provide your research query or paste a lab URL. Our system automatically extracts keywords and understands your intent.",
  },
  {
    icon: Network,
    title: "AI Agents Search",
    description: "Multi-agent orchestration routes your query to specialized agents for grants, papers, and news. Agents work in parallel to gather comprehensive results.",
  },
  {
    icon: BarChart3,
    title: "Get Ranked Results",
    description: "Advanced ranking algorithm scores and organizes results by relevance, type priority, and metadata. Receive a unified inbox of curated research insights.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="relative px-6 py-20 border-t border-slate-800/50 z-10">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <ScrollReveal direction="down" delay={0.1}>
            <GradientText
              colors={["#5eead4", "#67e8f9", "#40ffaa", "#67e8f9", "#5eead4"]}
              animationSpeed={4}
              showBorder={false}
              className="text-3xl md:text-4xl font-bold mb-4 block"
            >
              How It Works
            </GradientText>
          </ScrollReveal>
          <ScrollReveal direction="up" delay={0.2}>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Three simple steps to transform your research workflow with AI-powered aggregation
            </p>
          </ScrollReveal>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {steps.map((step, index) => {
            const Icon = step.icon;
            
            return (
              <ScrollReveal key={step.title} direction="up" delay={0.1 + index * 0.1}>
                <div className="glare-hover group rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 via-slate-900/60 to-slate-950/80 backdrop-blur-sm p-8 space-y-4 hover:border-teal-500/40 hover:shadow-2xl hover:shadow-teal-500/20 transition-all hover:scale-105 transform relative overflow-hidden text-center h-full">
                  {/* Silver blur shape */}
                  <div className={`absolute -inset-3 silver-blur ${index === 0 ? 'liquid-shape' : index === 1 ? 'liquid-shape-2' : 'liquid-shape-3'} opacity-30 group-hover:opacity-50 transition-opacity -z-20`}></div>
                  {/* Liquid morphing shape */}
                  <div className={`absolute inset-0 bg-gradient-to-br from-teal-400/0 via-cyan-300/0 to-teal-300/0 group-hover:from-teal-400/10 group-hover:via-cyan-300/10 group-hover:to-teal-300/10 transition-all blur-xl ${index === 0 ? 'liquid-shape' : index === 1 ? 'liquid-shape-2' : 'liquid-shape-3'}`}></div>
                  <div className={`absolute -inset-2 bg-gradient-to-br from-teal-400/20 via-cyan-300/20 to-teal-300/20 blur-3xl opacity-0 group-hover:opacity-60 transition-opacity -z-10 ${index === 0 ? 'liquid-shape' : index === 1 ? 'liquid-shape-2' : 'liquid-shape-3'}`}></div>
                  
                  <div className="relative z-10">
                    {/* Step Number */}
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-teal-500/20 to-cyan-500/20 border border-teal-500/30 mb-4 group-hover:scale-110 group-hover:border-teal-400/50 transition-all">
                      <span className="text-2xl font-bold text-teal-400">
                        {index + 1}
                      </span>
                    </div>
                    
                    {/* Icon */}
                    <div className="mb-4 flex justify-center">
                      <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500/20 to-cyan-500/20 border border-teal-500/30 transition-all duration-300 group-hover:scale-110 group-hover:border-teal-400/50">
                        <Icon className="h-8 w-8 text-teal-400 transition-colors duration-300" />
                      </div>
                    </div>

                    <h3 className="text-xl font-bold tracking-tight text-slate-100 mb-3 group-hover:text-teal-300 transition-colors">
                      {step.title}
                    </h3>
                    <p className="text-base leading-relaxed text-slate-400">
                      {step.description}
                    </p>
                  </div>
                </div>
              </ScrollReveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}