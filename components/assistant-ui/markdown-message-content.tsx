import React from 'react';
import { MessagePrimitive } from '@assistant-ui/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownMessageContentProps {
  className?: string;
}

export const MarkdownMessageContent: React.FC<MarkdownMessageContentProps> = ({ 
  className = '' 
}) => {
  return (
    <MessagePrimitive.Content
      className={className}
      components={{
        Text: ({ children }) => {
          // Check if the content looks like markdown
          const content = children as string;
          
          // Handle null/undefined content
          if (!content || typeof content !== 'string') {
            return <span className="text-gray-700">{children}</span>;
          }
          
          const hasMarkdown = content.includes('**') || 
                            content.includes('#') || 
                            content.includes('- ') ||
                            content.includes('1.') ||
                            content.includes('\n');
          
          if (hasMarkdown) {
            return (
              <div className="prose prose-gray max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({ children }) => (
                      <h1 className="text-2xl font-bold text-gray-900 mb-4 mt-6 border-b-2 border-blue-200 pb-2">
                        {children}
                      </h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-xl font-semibold text-gray-800 mb-3 mt-5 border-b border-gray-200 pb-1">
                        {children}
                      </h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-lg font-semibold text-blue-700 mb-2 mt-4">
                        {children}
                      </h3>
                    ),
                    h4: ({ children }) => (
                      <h4 className="text-base font-medium text-blue-600 mb-2 mt-3">
                        {children}
                      </h4>
                    ),
                    p: ({ children }) => (
                      <p className="text-gray-700 leading-relaxed mb-3">
                        {children}
                      </p>
                    ),
                    ul: ({ children }) => (
                      <ul className="space-y-1 mb-3">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="space-y-1 mb-3 counter-reset-list">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li className="flex items-start text-gray-700">
                        <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                        <span>{children}</span>
                      </li>
                    ),
                    strong: ({ children }) => (
                      <strong className="font-semibold text-gray-900">
                        {children}
                      </strong>
                    ),
                    em: ({ children }) => (
                      <em className="italic text-gray-800">
                        {children}
                      </em>
                    ),
                    code: ({ children, className }) => {
                      const isInline = !className;
                      if (isInline) {
                        return (
                          <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono text-gray-800 border">
                            {children}
                          </code>
                        );
                      }
                      return (
                        <pre className="bg-gray-50 p-3 rounded-lg border overflow-x-auto mb-3">
                          <code className="text-sm font-mono text-gray-800">
                            {children}
                          </code>
                        </pre>
                      );
                    },
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-blue-400 pl-4 py-2 mb-3 bg-blue-50 rounded-r-lg">
                        <div className="text-gray-700 italic">
                          {children}
                        </div>
                      </blockquote>
                    ),
                    table: ({ children }) => (
                      <div className="overflow-x-auto mb-3">
                        <table className="min-w-full border border-gray-200 rounded-lg">
                          {children}
                        </table>
                      </div>
                    ),
                    th: ({ children }) => (
                      <th className="px-3 py-2 border-b border-gray-200 text-left font-semibold text-gray-700 bg-gray-50">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="px-3 py-2 border-b border-gray-100 text-gray-700">
                        {children}
                      </td>
                    ),
                    a: ({ children, href }) => (
                      <a 
                        href={href} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 underline transition-colors"
                      >
                        {children}
                      </a>
                    ),
                    hr: () => (
                      <hr className="border-t-2 border-gray-200 my-6" />
                    ),
                  }}
                >
                  {content}
                </ReactMarkdown>
              </div>
            );
          }
          
          // For plain text, return as is
          return <span className="text-gray-700">{children}</span>;
        }
      }}
    />
  );
};
