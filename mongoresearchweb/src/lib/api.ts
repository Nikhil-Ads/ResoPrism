import type { InboxRequest, ResearchResponse, SummaryRequest, SummaryResponse, GrantCard, PaperCard, NewsCard } from "@/types/research";
import { LAB_PROFILE, USER_INFO } from "./labProfile";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchInbox(
  query: string,
  intent?: "grants" | "papers" | "news" | "all",
  text_chunks?: string[]
): Promise<ResearchResponse> {
  const requestBody: InboxRequest = {
    user_query: query,
    intent: intent || "all",
    lab_url: USER_INFO.lab_url,
    lab_profile: LAB_PROFILE,
    ...(text_chunks && text_chunks.length > 0 ? { text_chunks } : {}),
  };

  try {
    const response = await fetch(`${API_BASE_URL}/api/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `API request failed: ${response.status} ${response.statusText}. ${errorText}`
      );
    }

    const data: ResearchResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch inbox: ${error.message}`);
    }
    throw new Error("Failed to fetch inbox: Unknown error");
  }
}

export async function fetchInboxGet(
  query: string,
  intent?: "grants" | "papers" | "news" | "all"
): Promise<ResearchResponse> {
  const params = new URLSearchParams({
    query: query,
  });

  if (intent) {
    params.append("intent", intent);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/search?${params.toString()}`);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `API request failed: ${response.status} ${response.statusText}. ${errorText}`
      );
    }

    const data: ResearchResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to fetch inbox: ${error.message}`);
    }
    throw new Error("Failed to fetch inbox: Unknown error");
  }
}

export async function generateSummary(
  results: GrantCard[] | PaperCard[] | NewsCard[],
  sector: "grants" | "papers" | "news",
  lab_profile?: Record<string, unknown>
): Promise<string> {
  const requestBody: SummaryRequest = {
    results,
    sector,
    ...(lab_profile ? { lab_profile } : {}),
  };

  try {
    const response = await fetch(`${API_BASE_URL}/api/generate-summary`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `API request failed: ${response.status} ${response.statusText}. ${errorText}`
      );
    }

    const data: SummaryResponse = await response.json();
    return data.summary;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to generate summary: ${error.message}`);
    }
    throw new Error("Failed to generate summary: Unknown error");
  }
}
