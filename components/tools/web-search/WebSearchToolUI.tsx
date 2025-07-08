"use client";

import { makeAssistantToolUI } from "@assistant-ui/react";
import { useState } from "react";

export const WebSearchToolUI = makeAssistantToolUI({
  toolName: "web_search",
  render: ({ args, result, status }) => {
    const [isCollapsed, setIsCollapsed] = useState(false);
    
    const parseSearchResults = (text: string) => {
      if (!text) return [];
      
      const lines = text.split('\n');
      const results: Array<{
        title: string;
        url: string;
        description: string;
        index: number;
      }> = [];
      
      let currentResult: any = null;
      
      for (const line of lines) {
        const titleMatch = line.match(/^(\d+)\.\s*\*\*(.*?)\*\*/);
        if (titleMatch) {
          if (currentResult) {
            results.push(currentResult);
          }
          currentResult = {
            index: parseInt(titleMatch[1]),
            title: titleMatch[2].trim(),
            url: '',
            description: ''
          };
        } else if (line.trim().startsWith('URL:') && currentResult) {
          currentResult.url = line.replace('URL:', '').trim();
        } else if (line.trim() && !line.startsWith('Search results for') && !line.startsWith('Summary:') && currentResult && !currentResult.description) {
          currentResult.description = line.trim();
        }
      }
      
      if (currentResult) {
        results.push(currentResult);
      }
      
      return results;
    };

    const searchResults = result ? parseSearchResults(result) : [];
    
    return (
      <div className="my-4 w-full max-w-2xl">
        <div className="bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-8 h-8 bg-blue-500 rounded-lg">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-gray-900">Web Search</h3>
                  {status.type === "running" && (
                    <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  )}
                  {status.type === "complete" && (
                    <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                      <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
                <p className="text-xs text-gray-600 truncate">"{args.query}"</p>
              </div>
              <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="p-1 text-gray-400 hover:text-gray-600 transition-colors rounded"
              >
                <svg 
                  className={`w-4 h-4 transform transition-transform ${isCollapsed ? 'rotate-180' : ''}`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          {!isCollapsed && (
            <div className="p-4">
              {/* Search Parameters */}
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {args.count || 2} results
                </span>
                {args.freshness && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                    </svg>
                    {args.freshness === 'd' ? 'Past Day' : 
                     args.freshness === 'w' ? 'Past Week' : 
                     args.freshness === 'm' ? 'Past Month' : 
                     args.freshness === 'y' ? 'Past Year' : args.freshness}
                  </span>
                )}
              </div>

              {/* Status Content */}
              {status.type === "running" && (
                <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-sm text-blue-700">Searching the web...</span>
                </div>
              )}

              {status.type === "complete" && result && (
                <div className="space-y-3">
                  {searchResults.length > 0 ? (
                    searchResults.map((item, idx) => (
                      <div
                        key={idx}
                        className="group p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all duration-200 bg-gray-50 hover:bg-blue-50"
                      >
                        <div className="flex gap-3">
                          <div className="flex items-center justify-center w-6 h-6 bg-blue-500 text-white text-xs font-semibold rounded flex-shrink-0">
                            {item.index}
                          </div>
                          <div className="flex-1 min-w-0">
                            <h4 className="text-sm font-medium text-gray-900 line-clamp-2 mb-1">
                              {item.title}
                            </h4>
                            {item.url && (
                              <a
                                href={item.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 hover:text-blue-800 hover:underline block truncate mb-1"
                              >
                                {item.url}
                              </a>
                            )}
                            {item.description && (
                              <p className="text-xs text-gray-600 line-clamp-2 leading-relaxed">
                                {item.description}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <svg className="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <p className="text-sm text-gray-500">No search results found</p>
                    </div>
                  )}
                </div>
              )}

              {status.type === "incomplete" && (
                <div className="flex items-center gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm text-red-700">Search failed or was interrupted</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  },
});
