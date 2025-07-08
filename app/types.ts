// Types for the Assistant UI integration

export interface ApiMessage {
  role: string;
  content: string;
}

export interface ChatApiRequest {
  messages: ApiMessage[];
  stream?: boolean;
  tools_enabled?: boolean;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface SSEMessage {
  type: "content" | "thinking" | "tool_calls" | "tool_start" | "tool_result" | "tool_error" | "error" | "done";
  text?: string;
  tool_calls?: ToolCallData[];
  tool_name?: string;
  args?: any;
  result?: string;
  content?: string;
  error?: string;
}

export interface ToolCallData {
  id: string;
  function: {
    name: string;
    arguments: string;
  };
}

// Environment configuration
export const config = {
  API_ENDPOINT: process.env.NEXT_PUBLIC_API_ENDPOINT || "http://localhost:8000/chat",
} as const;
