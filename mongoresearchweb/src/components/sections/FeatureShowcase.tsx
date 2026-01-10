"use client";

import {
  Search,
  Zap,
  BarChart3,
  Shield,
  Network,
  Database,
  Sparkles,
} from "lucide-react";
import { AnimatedFeatureCard } from "@/components/cards/AnimatedFeatureCard";
import { ScrollReveal } from "@/components/animations/ScrollReveal";
import GradientText from "@/components/GradientText";

const features = [
  {
    icon: Network,
    title: "Multi-Agent Orchestration",
    description:
      "Intelligent routing to specialized agents for grants, papers, and news collection with seamless coordination.",
  },
  {
    icon: BarChart3,
    title: "Deterministic Ranking",
    description:
      "Advanced ranking algorithm that scores results by relevance, type priority, and metadata for optimal organization.",
  },
  {
    icon: Zap,
    title: "Fast API Integration",
    description:
      "RESTful API built with FastAPI for lightning-fast responses and easy integration with any frontend framework.",
  },
  {
    icon: Shield,
    title: "Error Resilience",
    description:
      "Robust error handling ensures partial results are returned even if some agents fail, maintaining system reliability.",
  },
  {
    icon: Search,
    title: "Intent-Based Routing",
    description:
      "Smart intent detection allows you to search for specific types (grants, papers, news) or get results from all sources.",
  },
  {
    icon: Database,
    title: "Structured Data",
    description:
      "Clean, typed responses with comprehensive metadata including scores, dates, authors, sources, and more.",
  },
  {
    icon: Sparkles,
    title: "LLM-Powered Extraction",
    description:
      "Advanced keyword extraction using OpenAI to understand research context and optimize search queries automatically.",
  },
  {
    icon: Database,
    title: "MongoDB Caching",
    description:
      "Intelligent caching system reduces redundant API calls and speeds up responses for frequently accessed data.",
  },
  {
    icon: Network,
    title: "URL-Based Research",
    description:
      "Automatically scrape research lab URLs, extract keywords, and find relevant grants, papers, and news in one click.",
  },
];

export function FeatureShowcase() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="text-center mb-16">
        <ScrollReveal direction="down" delay={0.1}>
          <GradientText
            colors={["#5eead4", "#67e8f9", "#40ffaa", "#67e8f9", "#5eead4"]}
            animationSpeed={4}
            showBorder={false}
            className="text-3xl md:text-4xl font-bold mb-4 block"
          >
            Everything you need to manage research
          </GradientText>
        </ScrollReveal>
        <ScrollReveal direction="up" delay={0.2}>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Powerful features designed to give you complete control over your
            research aggregation and analysis
          </p>
        </ScrollReveal>
      </div>

      {/* Feature Grid */}
      <div className="grid gap-6 md:grid-cols-3">
        {features.map((feature, index) => (
          <AnimatedFeatureCard
            key={feature.title}
            icon={feature.icon}
            title={feature.title}
            description={feature.description}
            delay={index * 0.1}
          />
        ))}
      </div>
    </div>
  );
}
