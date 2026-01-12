"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface TextGenerateEffectProps {
  words: string;
  className?: string;
  filter?: boolean;
  duration?: number;
}

export function TextGenerateEffect({
  words,
  className = "",
  filter = false,
  duration = 0.5,
}: TextGenerateEffectProps) {
  const [visibleCount, setVisibleCount] = useState(0);

  useEffect(() => {
    const wordsArray = words.split(" ");
    let currentIndex = 0;

    const interval = setInterval(() => {
      if (currentIndex < wordsArray.length) {
        currentIndex++;
        setVisibleCount(currentIndex);
      } else {
        clearInterval(interval);
      }
    }, duration * 1000);

    return () => clearInterval(interval);
  }, [words, duration]);

  return (
    <div className={className}>
      <div className="flex flex-wrap">
        {words.split(" ").map((word, idx) => {
          const isDisplayed = idx < visibleCount;
          return (
            <motion.span
              key={`${word}-${idx}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: isDisplayed ? 1 : 0 }}
              transition={{ duration: 0.3 }}
              className={`inline-block mr-1.5 ${
                filter && !isDisplayed ? "blur-sm" : ""
              }`}
            >
              {word}
            </motion.span>
          );
        })}
      </div>
    </div>
  );
}
