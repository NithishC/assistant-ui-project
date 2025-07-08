import type { ThreadMessage } from "@assistant-ui/react";
import type { ApiMessage } from "./types";

/**
 * Convert Assistant UI messages to API format
 */
export function convertToApiMessages(messages: ThreadMessage[]): ApiMessage[] {
  return messages.map((msg) => ({
    role: msg.role,
    content: msg.content
      .filter((c) => c.type === "text")
      .map((c) => (c as any).text)
      .join("\n"),
  }));
}

/**
 * Parse SSE line data
 */
export function parseSSEData(line: string): any | null {
  const trimmed = line.trim();
  if (!trimmed || !trimmed.startsWith("data: ")) {
    return null;
  }
  
  const data = trimmed.slice(6);
  if (data === "[DONE]") {
    return { type: "done" };
  }
  
  try {
    return JSON.parse(data);
  } catch {
    return null;
  }
}

/**
 * Check if error is an abort error
 */
export function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === "AbortError";
}
