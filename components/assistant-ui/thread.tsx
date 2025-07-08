"use client";

import { forwardRef, type ComponentPropsWithoutRef } from "react";
import {
  ThreadPrimitive,
  ComposerPrimitive,
  MessagePrimitive,
  ActionBarPrimitive,
} from "@assistant-ui/react";
import { 
  Send, 
  Square, 
  ArrowDown, 
  Copy, 
  RefreshCw 
} from "lucide-react";
import { cn } from "@/lib/utils";
import { MarkdownText } from "./markdown-text";

interface ThreadProps extends ComponentPropsWithoutRef<typeof ThreadPrimitive.Root> {
  tools?: any[];
}

const Thread = forwardRef<HTMLDivElement, ThreadProps>(
  ({ className, tools, ...props }, ref) => {
    return (
      <ThreadPrimitive.Root
        ref={ref}
        className={cn(
          "aui-root aui-thread-root flex h-full flex-col bg-background",
          className
        )}
        style={{
          ["--aui-thread-max-width" as string]: "42rem",
        }}
        {...props}
      >
        <ThreadPrimitive.Viewport 
          className="aui-thread-viewport flex-1 overflow-y-auto"
          autoScroll={true}
        >
          {/* Welcome State */}
          <ThreadPrimitive.Empty>
            <div className="flex flex-col items-center justify-center min-h-[400px] px-4 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 mb-6 shadow-lg">
                <span className="text-3xl text-white">🤖</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                AI Assistant Ready
              </h2>
              <p className="text-gray-600 max-w-md mb-8 leading-relaxed">
                Start a conversation or enable tools to unlock advanced capabilities. 
                I'm here to help with research, analysis, and more.
              </p>
              
              {/* Welcome Suggestions */}
              <div className="grid gap-2 max-w-lg w-full">
                <ThreadPrimitive.Suggestion
                  prompt="What's the latest news in AI?"
                  method="replace"
                  autoSend
                  className="px-4 py-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors cursor-pointer text-left"
                >
                  <span className="text-gray-700">What's the latest news in AI?</span>
                </ThreadPrimitive.Suggestion>
                <ThreadPrimitive.Suggestion
                  prompt="Help me research a company"
                  method="replace"
                  autoSend
                  className="px-4 py-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors cursor-pointer text-left"
                >
                  <span className="text-gray-700">Help me research a company</span>
                </ThreadPrimitive.Suggestion>
                <ThreadPrimitive.Suggestion
                  prompt="How can I improve my workflow?"
                  method="replace"
                  autoSend
                  className="px-4 py-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors cursor-pointer text-left"
                >
                  <span className="text-gray-700">How can I improve my workflow?</span>
                </ThreadPrimitive.Suggestion>
              </div>
            </div>
          </ThreadPrimitive.Empty>

          {/* Messages */}
          <div className="w-full max-w-4xl mx-auto px-4">
            <ThreadPrimitive.Messages
              components={{
                UserMessage: UserMessage,
                AssistantMessage: AssistantMessage,
              }}
            />
          </div>

          {/* Spacer for when thread is not empty */}
          <ThreadPrimitive.If empty={false}>
            <div className="h-32" />
          </ThreadPrimitive.If>
        </ThreadPrimitive.Viewport>

        {/* Fixed Footer with Scroll to Bottom and Composer */}
        <div className="border-t border-gray-200 bg-white/80 backdrop-blur-sm">
          <div className="w-full max-w-4xl mx-auto p-4 space-y-3">
            {/* Scroll to Bottom Button */}
            <div className="flex justify-center">
              <ThreadPrimitive.ScrollToBottom asChild>
                <button className="inline-flex items-center gap-2 px-3 py-1.5 text-xs bg-white border border-gray-200 rounded-full shadow-sm hover:bg-gray-50 transition-colors opacity-0 data-[enabled]:opacity-100">
                  <ArrowDown className="h-3 w-3" />
                  Scroll to bottom
                </button>
              </ThreadPrimitive.ScrollToBottom>
            </div>

            {/* Composer */}
            <Composer tools={tools} />
          </div>
        </div>
      </ThreadPrimitive.Root>
    );
  }
);
Thread.displayName = "Thread";

interface ComposerProps {
  tools?: any[];
}

const Composer = ({ tools }: ComposerProps) => {
  return (
    <ComposerPrimitive.Root className="flex w-full items-end rounded-2xl border border-gray-200 bg-white shadow-lg focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all">
      <ComposerPrimitive.Input
        autoFocus
        placeholder="Type your message..."
        className="flex-1 resize-none bg-transparent px-4 py-4 text-sm placeholder:text-gray-500 focus:outline-none min-h-[56px] max-h-32 leading-relaxed"
      />
      
      {/* Send/Cancel Button */}
      <div className="flex items-center p-2">
        <ThreadPrimitive.If running={false}>
          <ComposerPrimitive.Send asChild>
            <button className="h-10 w-10 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white flex items-center justify-center transition-all duration-200 hover:scale-105 shadow-lg">
              <Send className="h-4 w-4" />
            </button>
          </ComposerPrimitive.Send>
        </ThreadPrimitive.If>
        
        <ThreadPrimitive.If running>
          <ComposerPrimitive.Cancel asChild>
            <button className="h-10 w-10 rounded-xl bg-red-500 hover:bg-red-600 text-white flex items-center justify-center transition-all duration-200 hover:scale-105 shadow-lg">
              <Square className="h-4 w-4" />
            </button>
          </ComposerPrimitive.Cancel>
        </ThreadPrimitive.If>
      </div>
    </ComposerPrimitive.Root>
  );
};

const UserMessage = forwardRef<
  HTMLDivElement,
  ComponentPropsWithoutRef<typeof MessagePrimitive.Root>
>(({ className, ...props }, ref) => {
  return (
    <MessagePrimitive.Root
      ref={ref}
      className={cn("group flex w-full justify-end py-4", className)}
      {...props}
    >
      <div className="flex items-start gap-3 max-w-2xl">
        <div className="flex flex-col gap-2 max-w-xs sm:max-w-md lg:max-w-lg order-2">
          <MessagePrimitive.Content className="rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-3 text-white text-sm break-words shadow-md" />
        </div>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white text-sm font-medium shadow-md order-3">
          You
        </div>
      </div>
    </MessagePrimitive.Root>
  );
});
UserMessage.displayName = "UserMessage";

const AssistantMessage = forwardRef<
  HTMLDivElement,
  ComponentPropsWithoutRef<typeof MessagePrimitive.Root>
>(({ className, ...props }, ref) => {
  return (
    <MessagePrimitive.Root
      ref={ref}
      className={cn("group flex w-full py-4", className)}
      {...props}
    >
      <div className="flex items-start gap-3 max-w-full">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-emerald-600 text-white text-sm font-medium shadow-md">
          AI
        </div>
        <div className="flex flex-col gap-2 flex-1 min-w-0 max-w-none">
          {/* Enhanced message content with markdown rendering */}
          <div className="rounded-2xl bg-gray-50 border border-gray-200 shadow-sm overflow-hidden">
            <MessagePrimitive.Content 
              className="px-4 py-3"
              components={{ Text: MarkdownText }} 
            />
          </div>
          <AssistantActionBar />
        </div>
      </div>
    </MessagePrimitive.Root>
  );
});
AssistantMessage.displayName = "AssistantMessage";

const AssistantActionBar = () => {
  return (
    <ActionBarPrimitive.Root 
      className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
      autohide="not-last"
    >
      <ActionBarPrimitive.Copy asChild>
        <button className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition-colors shadow-sm">
          <Copy className="h-3 w-3" />
          Copy
        </button>
      </ActionBarPrimitive.Copy>
      <ActionBarPrimitive.Reload asChild>
        <button className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition-colors shadow-sm">
          <RefreshCw className="h-3 w-3" />
          Retry
        </button>
      </ActionBarPrimitive.Reload>
    </ActionBarPrimitive.Root>
  );
};

export { Thread };