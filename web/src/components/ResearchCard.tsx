import type { InboxCard, GrantCard as GrantCardType, PaperCard as PaperCardType, NewsCard as NewsCardType } from "@/types/research";
import { GrantCard } from "./GrantCard";
import { PaperCard } from "./PaperCard";
import { NewsCard } from "./NewsCard";

interface ResearchCardProps {
  card: InboxCard;
}

export function ResearchCard({ card }: ResearchCardProps) {
  switch (card.type) {
    case "grant":
      return <GrantCard grant={card as GrantCardType} />;
    case "paper":
      return <PaperCard paper={card as PaperCardType} />;
    case "news":
      return <NewsCard news={card as NewsCardType} />;
    default:
      return null;
  }
}
