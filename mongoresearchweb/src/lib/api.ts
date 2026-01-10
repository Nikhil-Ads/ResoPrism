import type { InboxRequest, ResearchResponse } from "@/types/research";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchInbox(
  query: string,
  intent?: "grants" | "papers" | "news" | "all"
): Promise<ResearchResponse> {
  const requestBody: InboxRequest = {
    user_query: query,
    intent: intent || "all",
  };

  try {
    const response = await fetch(`${API_BASE_URL}/api/inbox`, {
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
    user_query: query,
  });

  if (intent) {
    params.append("intent", intent);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/inbox?${params.toString()}`);

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
