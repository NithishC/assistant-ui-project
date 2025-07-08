"use client";

import React, { useState } from 'react';
import { cn } from "@/lib/utils";

interface ToolConfig {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

interface ToolTogglePanelProps {
  enabledTools: string[];
  onToolToggle: (toolId: string, enabled: boolean) => void;
}

const AVAILABLE_TOOLS: ToolConfig[] = [
  {
    id: 'web_search',
    name: 'Web Search',
    description: 'Search the web and fetch article content',
    icon: '🔍',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    id: 'case_studies_search',
    name: 'Case Studies',
    description: 'Find case studies from company domains',
    icon: '📊',
    color: 'from-emerald-500 to-green-500'
  },
  {
    id: 'file_system',
    name: 'File System',
    description: 'Read, create, edit files in knowledge_base and output directories',
    icon: '📁',
    color: 'from-purple-500 to-pink-500'
  }
];

export function ToolTogglePanel({ enabledTools, onToolToggle }: ToolTogglePanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleToggle = (toolId: string) => {
    const isEnabled = enabledTools.includes(toolId);
    onToolToggle(toolId, !isEnabled);
  };

  const enabledCount = enabledTools.length;
  const currentMode = enabledCount === 0 ? 'Normal Chat' : `Agent Mode`;

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div 
        className={cn(
          "flex items-center justify-between p-6 cursor-pointer transition-all duration-300",
          enabledCount > 0 
            ? "bg-gradient-to-r from-blue-500 to-purple-600" 
            : "bg-gradient-to-r from-gray-500 to-gray-600"
        )}
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-12 h-12 bg-white/20 rounded-xl backdrop-blur-sm">
            <span className="text-2xl">🤖</span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">
              Agent Controls
            </h3>
            <p className="text-white/80 text-sm">
              {currentMode} {enabledCount > 0 && `• ${enabledCount} active`}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {enabledCount > 0 && (
            <div className="bg-white/20 px-3 py-1 rounded-full backdrop-blur-sm">
              <span className="text-white text-sm font-medium">{enabledCount}</span>
            </div>
          )}
          <button className="text-white/80 hover:text-white transition-colors p-1">
            <svg 
              className={cn("w-5 h-5 transition-transform duration-200", isCollapsed && "rotate-180")}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Tool Controls */}
      {!isCollapsed && (
        <div className="p-6">
          <div className="grid gap-4 md:grid-cols-2">
            {AVAILABLE_TOOLS.map((tool) => {
              const isEnabled = enabledTools.includes(tool.id);
              
              return (
                <div
                  key={tool.id}
                  className={cn(
                    "group relative overflow-hidden rounded-xl border-2 p-4 cursor-pointer transition-all duration-200",
                    isEnabled 
                      ? "border-blue-500 bg-blue-50 shadow-lg shadow-blue-500/20" 
                      : "border-gray-200 bg-gray-50 hover:border-gray-300 hover:bg-gray-100"
                  )}
                  onClick={() => handleToggle(tool.id)}
                >
                  {/* Background gradient overlay for enabled state */}
                  {isEnabled && (
                    <div className={cn(
                      "absolute inset-0 bg-gradient-to-r opacity-5",
                      tool.color
                    )} />
                  )}
                  
                  <div className="relative flex items-center gap-4">
                    {/* Tool Icon */}
                    <div className={cn(
                      "flex items-center justify-center w-12 h-12 rounded-xl transition-all duration-200",
                      isEnabled 
                        ? `bg-gradient-to-r ${tool.color} text-white shadow-lg` 
                        : "bg-gray-200 text-gray-600 group-hover:bg-gray-300"
                    )}>
                      <span className="text-xl">{tool.icon}</span>
                    </div>

                    {/* Tool Info */}
                    <div className="flex-1 min-w-0">
                      <h4 className={cn(
                        "font-semibold text-base mb-1",
                        isEnabled ? "text-gray-900" : "text-gray-700"
                      )}>
                        {tool.name}
                      </h4>
                      <p className={cn(
                        "text-sm",
                        isEnabled ? "text-gray-600" : "text-gray-500"
                      )}>
                        {tool.description}
                      </p>
                    </div>

                    {/* Toggle Switch */}
                    <div className={cn(
                      "relative w-12 h-6 rounded-full transition-all duration-200",
                      isEnabled ? "bg-blue-500" : "bg-gray-300"
                    )}>
                      <div className={cn(
                        "absolute top-0.5 w-5 h-5 bg-white rounded-full shadow-md transition-all duration-200",
                        isEnabled ? "left-6" : "left-0.5"
                      )} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Status Summary */}
          <div className={cn(
            "mt-6 p-4 rounded-xl text-center",
            enabledCount > 0 
              ? "bg-blue-50 border border-blue-200" 
              : "bg-gray-50 border border-gray-200"
          )}>
            <p className={cn(
              "text-sm font-medium",
              enabledCount > 0 ? "text-blue-800" : "text-gray-600"
            )}>
              {enabledCount === 0 
                ? '💬 Normal chat mode - AI responds using built-in knowledge only'
                : `🤖 Agent mode active - AI can use ${enabledCount} tool${enabledCount > 1 ? 's' : ''} to enhance responses`
              }
            </p>
          </div>
        </div>
      )}
    </div>
  );
}