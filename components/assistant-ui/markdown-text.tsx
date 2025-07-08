"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { memo } from "react";
import { cn } from "@/lib/utils";
import { useContentPart } from "@assistant-ui/react";

interface MarkdownTextProps {
  children?: React.ReactNode;
}

const MarkdownTextImpl: React.FC<MarkdownTextProps> = ({ children }) => {
  // Get the content from the ContentPart context
  const content = useContentPart((contentPart) => {
    if (contentPart.type === "text") {
      return contentPart.text;
    }
    return "";
  });

  // Use children if provided, otherwise use content from context
  const textToRender = typeof children === "string" ? children : content;

  if (!textToRender) {
    return null;
  }

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className="prose prose-gray max-w-none"
      components={{
        h1: ({ className, ...props }) => (
          <h1 className={cn("text-2xl font-bold text-gray-900 mb-4 mt-6 border-b-2 border-blue-200 pb-2", className)} {...props} />
        ),
        h2: ({ className, ...props }) => (
          <h2 className={cn("text-xl font-semibold text-gray-800 mb-3 mt-5 border-b border-gray-200 pb-1", className)} {...props} />
        ),
        h3: ({ className, ...props }) => (
          <h3 className={cn("text-lg font-semibold text-blue-700 mb-2 mt-4", className)} {...props} />
        ),
        h4: ({ className, ...props }) => (
          <h4 className={cn("text-base font-medium text-blue-600 mb-2 mt-3", className)} {...props} />
        ),
        h5: ({ className, ...props }) => (
          <h5 className={cn("text-sm font-medium text-gray-700 mb-2 mt-3", className)} {...props} />
        ),
        h6: ({ className, ...props }) => (
          <h6 className={cn("text-xs font-medium text-gray-600 mb-2 mt-3", className)} {...props} />
        ),
        p: ({ className, ...props }) => (
          <p className={cn("text-gray-700 leading-relaxed mb-3", className)} {...props} />
        ),
        ul: ({ className, ...props }) => (
          <ul className={cn("space-y-1 mb-3 ml-4", className)} {...props} />
        ),
        ol: ({ className, ...props }) => (
          <ol className={cn("space-y-1 mb-3 ml-4 list-decimal", className)} {...props} />
        ),
        li: ({ className, ...props }) => (
          <li className={cn("flex items-start text-gray-700", className)}>
            <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
            <span {...props} />
          </li>
        ),
        strong: ({ className, ...props }) => (
          <strong className={cn("font-semibold text-gray-900", className)} {...props} />
        ),
        em: ({ className, ...props }) => (
          <em className={cn("italic text-gray-800", className)} {...props} />
        ),
        code: ({ className, inline, ...props }) => {
          if (inline) {
            return (
              <code className={cn("bg-gray-100 px-2 py-1 rounded text-sm font-mono text-gray-800 border", className)} {...props} />
            );
          }
          return (
            <pre className="bg-gray-50 p-3 rounded-lg border overflow-x-auto mb-3">
              <code className={cn("text-sm font-mono text-gray-800", className)} {...props} />
            </pre>
          );
        },
        blockquote: ({ className, ...props }) => (
          <blockquote className={cn("border-l-4 border-blue-400 pl-4 py-2 mb-3 bg-blue-50 rounded-r-lg", className)}>
            <div className="text-gray-700 italic" {...props} />
          </blockquote>
        ),
        table: ({ className, ...props }) => (
          <div className="overflow-x-auto mb-3">
            <table className={cn("min-w-full border border-gray-200 rounded-lg", className)} {...props} />
          </div>
        ),
        th: ({ className, ...props }) => (
          <th className={cn("px-3 py-2 border-b border-gray-200 text-left font-semibold text-gray-700 bg-gray-50", className)} {...props} />
        ),
        td: ({ className, ...props }) => (
          <td className={cn("px-3 py-2 border-b border-gray-100 text-gray-700", className)} {...props} />
        ),
        a: ({ className, ...props }) => (
          <a
            className={cn("text-blue-600 hover:text-blue-800 underline transition-colors", className)}
            target="_blank"
            rel="noopener noreferrer"
            {...props}
          />
        ),
        hr: ({ className, ...props }) => (
          <hr className={cn("border-t-2 border-gray-200 my-6", className)} {...props} />
        ),
      }}
    >
      {textToRender}
    </ReactMarkdown>
  );
};

export const MarkdownText = memo(MarkdownTextImpl);
