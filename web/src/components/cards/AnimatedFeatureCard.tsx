"use client";

import { motion } from "framer-motion";
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

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.5, delay }}
      className="group relative h-full"
    >
      <div className="glare-hover group rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 via-slate-900/60 to-slate-950/80 p-6 space-y-4 hover:border-teal-500/40 hover:shadow-2xl hover:shadow-teal-500/20 transition-all hover:scale-105 transform relative overflow-hidden h-full">
        {/* Liquid morphing shape */}
        <div className="absolute inset-0 bg-gradient-to-br from-teal-400/0 via-cyan-300/0 to-teal-300/0 group-hover:from-teal-400/10 group-hover:via-cyan-300/10 group-hover:to-teal-300/10 transition-all blur-xl liquid-shape" />
        <div className="absolute -inset-2 bg-gradient-to-br from-teal-400/20 via-cyan-300/20 to-teal-300/20 blur-3xl opacity-0 group-hover:opacity-60 transition-opacity -z-10 liquid-shape" />

        <div className="relative z-10">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500/20 to-cyan-500/20 border border-teal-500/30 transition-all duration-300 group-hover:scale-110 group-hover:border-teal-400/50">
            <Icon className="h-7 w-7 text-teal-400 transition-colors duration-300" />
          </div>

          <h3 className="text-xl font-bold tracking-tight text-slate-100 mb-2 group-hover:text-teal-300 transition-colors">
            {title}
          </h3>
          <p className="text-base leading-relaxed text-slate-400">
            {description}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
