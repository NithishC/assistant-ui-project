"use client";

import { useState } from "react";
import { Thread } from "@/components/assistant-ui/thread";
import { 
  WebSearchToolUI, 
  CaseStudiesToolUI
} from "../components/tools";
import { FileSystemToolUI } from "../components/ui/FileSystemToolUI";
import { ToolTogglePanel } from "../components/ToolTogglePanel";
import { MyRuntimeProvider } from "./MyRuntimeProvider";

export default function Page() {
  // State for enabled tools - starts empty (normal chat mode)
  const [enabledTools, setEnabledTools] = useState<string[]>([]);

  // Handle tool toggle
  const handleToolToggle = (toolId: string, enabled: boolean) => {
    setEnabledTools(prev => {
      if (enabled) {
        // Add tool if not already present
        return prev.includes(toolId) ? prev : [...prev, toolId];
      } else {
        // Remove tool
        return prev.filter(id => id !== toolId);
      }
    });
  };

  // Get tool UIs based on enabled tools
  const getEnabledToolUIs = () => {
    const toolUIMap = {
      'web_search': WebSearchToolUI,
      'case_studies_search': CaseStudiesToolUI,
      'file_system': FileSystemToolUI
    };

    return enabledTools
      .map(toolId => toolUIMap[toolId as keyof typeof toolUIMap])
      .filter(Boolean);
  };

  const enabledToolUIs = getEnabledToolUIs();

  return (
    <MyRuntimeProvider enabledTools={enabledTools}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4 py-6">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
              AI Assistant
            </h1>
          </div>

          {/* Tool Toggle Panel */}
          <div className="mb-6">
            <ToolTogglePanel 
              enabledTools={enabledTools}
              onToolToggle={handleToolToggle}
            />
          </div>

          {/* Main Chat Interface */}
          <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 overflow-hidden">
            <div className="h-[700px] relative">
              <Thread tools={enabledToolUIs} />
              
              {/* Render tool UIs outside Thread but in the same provider context */}
              <div className="absolute -bottom-full opacity-0 pointer-events-none">
                {enabledToolUIs.map((ToolUI, index) => (
                  <ToolUI key={index} />
                ))}
              </div>
            </div>
          </div>

          {/* Footer Status */}
          <div className="text-center mt-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full shadow-md border border-gray-200">
              <div className={`w-2 h-2 rounded-full ${enabledTools.length > 0 ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
              <span className="text-sm font-medium text-gray-700">
                {enabledTools.length === 0 
                  ? 'Chat Mode' 
                  : `Agent Mode • ${enabledTools.length} tool${enabledTools.length > 1 ? 's' : ''} active`
                }
              </span>
            </div>
          </div>
        </div>
      </div>
    </MyRuntimeProvider>
  );
}