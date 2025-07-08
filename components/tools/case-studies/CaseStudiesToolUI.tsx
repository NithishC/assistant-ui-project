"use client";

import { makeAssistantToolUI } from "@assistant-ui/react";
import { useState } from "react";

export const CaseStudiesToolUI = makeAssistantToolUI({
  toolName: "case_studies_search",
  render: ({ args, result, status }) => {
    const [isCollapsed, setIsCollapsed] = useState(false);
    
    const parseCaseStudies = (text: string) => {
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
        } else if (line.trim() && !line.startsWith('Case studies from') && !line.startsWith('Summary:') && currentResult && !currentResult.description) {
          currentResult.description = line.trim();
        }
      }
      
      if (currentResult) {
        results.push(currentResult);
      }
      
      return results;
    };

    const caseStudies = result ? parseCaseStudies(result) : [];
    
    return (
      <div className="my-4 w-full max-w-2xl">
        <div className="bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-emerald-50 to-green-50 px-4 py-3 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-8 h-8 bg-emerald-500 rounded-lg">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-gray-900">Case Studies</h3>
                  {status.type === "running" && (
                    <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                  )}
                  {status.type === "complete" && (
                    <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                      <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
                <p className="text-xs text-gray-600 truncate">
                  {args.company}
                  {args.industry && ` • ${args.industry}`}
                  {args.topic && ` • ${args.topic}`}
                </p>
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
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-full">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z" />
                    <path fillRule="evenodd" d="M3 8a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  {args.company}
                </span>
                {args.industry && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 2a2 2 0 00-2 2v11a3 3 0 106 0V4a2 2 0 00-2-2H4zm1 14a1 1 0 100-2 1 1 0 000 2zm5-1.757l4.9-4.9a2 2 0 000-2.828L13.485 5.1a2 2 0 00-2.828 0L10 5.757v8.486zM16 18H9.071l6-6H16a2 2 0 012 2v2a2 2 0 01-2 2z" clipRule="evenodd" />
                    </svg>
                    {args.industry}
                  </span>
                )}
                {args.topic && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    {args.topic}
                  </span>
                )}
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {args.count || 2} results
                </span>
              </div>

              {/* Status Content */}
              {status.type === "running" && (
                <div className="flex items-center gap-3 p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
                  <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-sm text-emerald-700">Searching for case studies and success stories...</span>
                </div>
              )}

              {status.type === "complete" && result && (
                <div className="space-y-3">
                  {caseStudies.length > 0 ? (
                    caseStudies.map((item, idx) => (
                      <div
                        key={idx}
                        className="group p-3 border border-gray-200 rounded-lg hover:border-emerald-300 hover:shadow-sm transition-all duration-200 bg-gray-50 hover:bg-emerald-50"
                      >
                        <div className="flex gap-3">
                          <div className="flex items-center justify-center w-6 h-6 bg-emerald-500 text-white text-xs font-semibold rounded flex-shrink-0">
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
                                className="text-xs text-emerald-600 hover:text-emerald-800 hover:underline block truncate mb-1"
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
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      <p className="text-sm text-gray-500">No case studies found for the specified criteria</p>
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
