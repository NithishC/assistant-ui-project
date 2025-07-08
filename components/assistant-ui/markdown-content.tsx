import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownContentProps {
  content: string;
  className?: string;
}

export const MarkdownContent: React.FC<MarkdownContentProps> = ({ 
  content, 
  className = '' 
}) => {
  return (
    <div className={`prose prose-gray max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Enhanced heading styles
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold text-gray-900 mb-6 border-b-2 border-blue-200 pb-2">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 mt-8 border-b border-gray-200 pb-2">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-xl font-semibold text-blue-700 mb-3 mt-6">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-lg font-medium text-blue-600 mb-2 mt-4">
              {children}
            </h4>
          ),
          h5: ({ children }) => (
            <h5 className="text-base font-medium text-gray-700 mb-2 mt-3">
              {children}
            </h5>
          ),
          h6: ({ children }) => (
            <h6 className="text-sm font-medium text-gray-600 mb-2 mt-3">
              {children}
            </h6>
          ),
          
          // Enhanced paragraph styling
          p: ({ children }) => (
            <p className="text-gray-700 leading-relaxed mb-4">
              {children}
            </p>
          ),
          
          // Beautiful unordered lists
          ul: ({ children }) => (
            <ul className="space-y-2 mb-4 ml-6">
              {children}
            </ul>
          ),
          li: ({ children, ...props }) => {
            // Check if this is a nested list item
            const isNested = props.node?.parent?.tagName === 'li';
            return (
              <li className={`flex items-start ${isNested ? 'ml-4' : ''}`}>
                <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                <span className="text-gray-700">{children}</span>
              </li>
            );
          },
          
          // Enhanced ordered lists
          ol: ({ children }) => (
            <ol className="space-y-2 mb-4 ml-6 counter-reset-[list-counter]">
              {children}
            </ol>
          ),
          
          // Strong text styling
          strong: ({ children }) => (
            <strong className="font-semibold text-gray-900">
              {children}
            </strong>
          ),
          
          // Emphasis styling
          em: ({ children }) => (
            <em className="italic text-gray-800">
              {children}
            </em>
          ),
          
          // Code blocks
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
              <pre className="bg-gray-50 p-4 rounded-lg border overflow-x-auto mb-4">
                <code className="text-sm font-mono text-gray-800">
                  {children}
                </code>
              </pre>
            );
          },
          
          // Blockquote styling
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-400 pl-4 py-2 mb-4 bg-blue-50 rounded-r-lg">
              <div className="text-gray-700 italic">
                {children}
              </div>
            </blockquote>
          ),
          
          // Table styling
          table: ({ children }) => (
            <div className="overflow-x-auto mb-4">
              <table className="min-w-full border border-gray-200 rounded-lg">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-gray-50">
              {children}
            </thead>
          ),
          th: ({ children }) => (
            <th className="px-4 py-2 border-b border-gray-200 text-left font-semibold text-gray-700">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-2 border-b border-gray-100 text-gray-700">
              {children}
            </td>
          ),
          
          // Links
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
          
          // Horizontal rule
          hr: () => (
            <hr className="border-t-2 border-gray-200 my-8" />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
