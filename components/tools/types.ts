// Tool argument and result types based on backend implementations

export interface WebSearchArgs {
  query: string;
  count?: number;
  freshness?: string;
}

export interface CaseStudiesArgs {
  company: string;
  industry?: string;
  topic?: string;
  count?: number;
}

export interface FetchUrlArgs {
  url: string;
}

// All tools return string results
export type ToolResult = string;

// Common tool UI props
export interface ToolUIProps<TArgs> {
  args: TArgs;
  result?: ToolResult;
  status: {
    type: "running" | "complete" | "incomplete" | "requires_action";
    reason?: string;
  };
  toolName: string;
  toolCallId: string;
  argsText: string;
}
