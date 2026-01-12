"use client";

import { useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ResearchCard } from "@/components/ResearchCard";
import type { InboxCard } from "@/types/research";
import { cn } from "@/lib/utils";

interface ResearchCarouselProps {
  items: InboxCard[];
  className?: string;
}

export function ResearchCarousel({ items, className }: ResearchCarouselProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: "left" | "right") => {
    if (!scrollContainerRef.current) return;

    const container = scrollContainerRef.current;
    const scrollAmount = container.clientWidth * 0.75;
    const targetScrollLeft =
      direction === "left"
        ? container.scrollLeft - scrollAmount
        : container.scrollLeft + scrollAmount;

    container.scrollTo({
      left: targetScrollLeft,
      behavior: "smooth",
    });
  };

  if (items.length === 0) {
    return (
      <div className={cn("py-8 text-center text-slate-400", className)}>
        <p>No items to display</p>
      </div>
    );
  }

  return (
    <div className={cn("relative group", className)}>
      {/* Left scroll button */}
      <Button
        variant="outline"
        size="icon"
        className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-slate-900/90 backdrop-blur-sm border-slate-700 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-800 hover:border-teal-500/50 text-slate-200"
        onClick={() => scroll("left")}
        aria-label="Scroll left"
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>

      {/* Scrollable container */}
      <div
        ref={scrollContainerRef}
        className="flex gap-6 overflow-x-auto scroll-smooth pb-4 px-1 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
      >
        {items.map((item) => (
          <div
            key={item.id}
            className="flex-shrink-0 w-[320px] md:w-[360px]"
          >
            <ResearchCard card={item} />
          </div>
        ))}
      </div>

      {/* Right scroll button */}
      <Button
        variant="outline"
        size="icon"
        className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-slate-900/90 backdrop-blur-sm border-slate-700 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-800 hover:border-teal-500/50 text-slate-200"
        onClick={() => scroll("right")}
        aria-label="Scroll right"
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );
}
