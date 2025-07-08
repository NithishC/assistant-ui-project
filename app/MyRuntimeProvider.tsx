"use client";

import type { ReactNode } from "react";
import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  type ChatModelAdapter,
  type ChatModelRunResult,
  type ThreadAssistantContentPart,
} from "@assistant-ui/react";

import { config, type SSEMessage } from "./types";
import { convertToApiMessages, parseSSEData, isAbortError } from "./utils";

interface MyRuntimeProviderProps {
  children: ReactNode;
  enabledTools?: string[];
}

const createModelAdapter = (enabledTools: string[] = []): ChatModelAdapter => ({
  async *run({ messages, abortSignal }): AsyncGenerator<ChatModelRunResult> {
    try {
      // Convert messages to API format
      const apiMessages = convertToApiMessages(messages);

      // Make request to backend with enabled tools
      const response = await fetch(config.API_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: apiMessages,
          stream: true,
          tools_enabled: enabledTools.length > 0, // Legacy field
          enabled_tools: enabledTools, // New field for Phase 4
        }),
        signal: abortSignal,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      // Process Server-Sent Events stream
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let buffer = "";
      
      // Track the complete message state
      const contentParts: ThreadAssistantContentPart[] = [];
      let currentTextIndex = -1;
      let toolCallsIndex = -1;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete lines
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const parsed = parseSSEData(line);
          if (!parsed) continue;
          
          try {
            const message = parsed as SSEMessage;
            
            switch (message.type) {
              case "thinking":
                // Skip thinking text since we have tool UI cards
                // if (message.text) {
                //   // Add thinking as italicized text
                //   if (currentTextIndex === -1) {
                //     currentTextIndex = contentParts.length;
                //     contentParts.push({
                //       type: "text",
                //       text: `🤔 *${message.text}*\n\n`,
                //     });
                //   } else {
                //     const textPart = contentParts[currentTextIndex] as any;
                //     textPart.text = `🤔 *${message.text}*\n\n`;
                //   }
                // }
                break;
                
              case "content":
                if (message.text) {
                  console.log("📝 Content received:", message.text.substring(0, 100) + "...");
                  // Always ensure we have a text part for content
                  if (currentTextIndex === -1 || !contentParts[currentTextIndex] || contentParts[currentTextIndex].type !== "text") {
                    // Create new text part
                    console.log("📝 Creating new text part");
                    currentTextIndex = contentParts.length;
                    contentParts.push({
                      type: "text",
                      text: message.text,
                    });
                  } else {
                    // Update existing text part
                    console.log("📝 Updating existing text part");
                    const textPart = contentParts[currentTextIndex] as any;
                    textPart.text = (textPart.text || "") + message.text;
                  }
                  console.log("📝 Total content parts:", contentParts.length);
                }
                break;
                
              case "tool_calls":
                if (message.tool_calls && message.tool_calls.length > 0) {
                  // Add tool calls after any existing text
                  toolCallsIndex = contentParts.length;
                  for (const tc of message.tool_calls) {
                    contentParts.push({
                      type: "tool-call" as const,
                      toolCallId: tc.id,
                      toolName: tc.function.name,
                      args: JSON.parse(tc.function.arguments || "{}"),
                      argsText: tc.function.arguments || "{}",
                    });
                  }
                  // Reset text index for the response that will come after tool execution
                  currentTextIndex = -1;
                }
                break;
                
              case "tool_start":
                // Tool execution started - the UI should show running state
                // This is handled by the tool-call content part status
                break;
                
              case "tool_result":
                // Tool execution completed - update the corresponding tool-call with result
                if (message.tool_name && message.result) {
                  // Find the tool-call content part and update it with result
                  for (let i = 0; i < contentParts.length; i++) {
                    const part = contentParts[i];
                    if (part.type === "tool-call" && part.toolName === message.tool_name) {
                      (part as any).result = message.result;
                      break;
                    }
                  }
                }
                // Don't create text part here - let content messages handle it
                break;
                
              case "tool_error":
                if (message.error) {
                  contentParts.push({
                    type: "text",
                    text: `⚠️ Tool Error: ${message.error}\n\n`,
                  });
                }
                break;
                
              case "error":
                throw new Error(message.error || "Stream error");
                
              case "done":
                // Stream completed
                return;
            }
            
            // Yield current state with all content parts
            if (contentParts.length > 0) {
              yield {
                content: [...contentParts],
              };
            }
            
          } catch (e) {
            if (process.env.NODE_ENV === "development") {
              console.error("Error processing SSE message:", e);
            }
          }
        }
      }

      // Final yield if we have content
      if (contentParts.length > 0) {
        yield {
          content: [...contentParts],
        };
      }
    } catch (error) {
      if (isAbortError(error)) {
        return;
      }
      
      console.error("Chat API error:", error);
      throw error;
    }
  },
});

export function MyRuntimeProvider({
  children,
  enabledTools = [],
}: MyRuntimeProviderProps) {
  const runtime = useLocalRuntime(createModelAdapter(enabledTools));
  
  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  );
}
