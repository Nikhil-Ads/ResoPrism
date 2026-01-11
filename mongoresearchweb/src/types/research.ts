export type CardType = "grant" | "paper" | "news";

export interface InboxCard {
  id: string;
  type: CardType;
  title: string;
  score: number;
  badge?: string | null;
  meta: {
    close_date?: string;
    amount_max?: number;
    sponsor?: string;
    source?: string;
    published_date?: string;
    authors?: string[];
    outlet?: string;
    url?: string;
    [key: string]: unknown;
  };
}

export interface GrantCard extends InboxCard {
  type: "grant";
  meta: {
    close_date?: string;
    amount_max?: number;
    sponsor?: string;
    source?: string;
    [key: string]: unknown;
  };
}

export interface PaperCard extends InboxCard {
  type: "paper";
  meta: {
    published_date?: string;
    authors?: string[];
    source?: string;
    [key: string]: unknown;
  };
}

export interface NewsCard extends InboxCard {
  type: "news";
  meta: {
    published_date?: string;
    outlet?: string;
    url?: string;
    source?: string;
    [key: string]: unknown;
  };
}

export interface InboxRequest {
  user_query: string;
  intent?: "grants" | "papers" | "news" | "all";
  lab_url?: string;
  lab_profile?: Record<string, unknown>;
}

export interface ResearchResponse {
  user_query: string;
  intent?: string;
  grants: GrantCard[];
  papers: PaperCard[];
  news: NewsCard[];
  inbox_cards: InboxCard[];
  errors: string[];
}

export interface MindMapRequest {
  grants: InboxCard[];
  papers: InboxCard[];
  news: InboxCard[];
  user_query?: string;
}

export interface MindMapResponse {
  markdown: string;
  themes: string[];
  connections: {
    from_type: string;
    to_type: string;
    description: string;
  }[];
  error?: string;
}