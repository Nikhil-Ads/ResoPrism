"use client";

import { AnimatedHero } from "@/components/hero/AnimatedHero";
import { FeatureShowcase } from "@/components/sections/FeatureShowcase";
import { CTASection } from "@/components/sections/CTASection";
import { Footer } from "@/components/sections/Footer";

export default function Home() {
  return (
    <div className="min-h-screen">
      <AnimatedHero />
      <FeatureShowcase />
      <CTASection />
      <Footer />
    </div>
  );
}
