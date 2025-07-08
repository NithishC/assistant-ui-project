import React, { useState } from 'react';
import { makeAssistantToolUI } from '@assistant-ui/react';

interface FileSystemArgs {
  operation: 'list' | 'read' | 'create' | 'edit';
  file_path?: string;
  directory?: string;
  content?: string;
  edit_mode?: 'append' | 'prepend' | 'replace';
}

interface ParsedFileResult {
  operation: string;
  success: boolean;
  file_path?: string;
  content?: string;
  truncated?: boolean;
  file_size?: number;
  error?: string;
  isFileList?: boolean;
  files?: string[];
}

export const FileSystemToolUI = makeAssistantToolUI<FileSystemArgs, string>({
  toolName: "file_system",
  render: ({ args, result, status }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [showFullContent, setShowFullContent] = useState(false);
    
    // Parse result to extract structured data
    const parseResult = (resultText: string): ParsedFileResult => {
      const isSuccess = resultText.includes('✅');
      const isError = resultText.includes('❌');
      const isFileList = resultText.includes('📂') || resultText.includes('Directory:');
      
      // Extract file list for list operations
      const files: string[] = [];
      if (isFileList) {
        const lines = resultText.split('\n');
        lines.forEach(line => {
          if (line.includes('📄') || line.includes('📁')) {
            files.push(line.trim());
          }
        });
      }
      
      return {
        operation: args.operation,
        success: isSuccess,
        error: isError ? resultText : undefined,
        content: resultText,
        isFileList,
        files
      };
    };

    const parsedResult = result ? parseResult(result) : null;

    // Operation-specific styling and configuration
    const getOperationConfig = (op: string) => {
      const configs = {
        list: { 
          bg: 'bg-blue-50', 
          border: 'border-blue-200', 
          icon: '📂',
          iconBg: 'bg-blue-100',
          name: 'List Files',
          description: 'Browse directory contents'
        },
        read: { 
          bg: 'bg-green-50', 
          border: 'border-green-200', 
          icon: '📄',
          iconBg: 'bg-green-100',
          name: 'Read File',
          description: 'View file content'
        },
        create: { 
          bg: 'bg-purple-50', 
          border: 'border-purple-200', 
          icon: '✨',
          iconBg: 'bg-purple-100',
          name: 'Create File',
          description: 'Generate new file'
        },
        edit: { 
          bg: 'bg-orange-50', 
          border: 'border-orange-200', 
          icon: '✏️',
          iconBg: 'bg-orange-100',
          name: 'Edit File',
          description: 'Modify existing file'
        }
      };
      return configs[op] || configs.read;
    };

    const opConfig = getOperationConfig(args.operation);

    // Extract content preview for read operations
    const getContentPreview = (content: string): string => {
      if (!content) return '';
      
      // Find the content section after "Content:" line
      const contentMatch = content.match(/📝 Content:\n-{40}\n([\s\S]*)/);
      if (contentMatch) {
        return contentMatch[1];
      }
      
      return content;
    };

    const contentPreview = parsedResult?.content ? getContentPreview(parsedResult.content) : '';
    const shouldShowExpandButton = contentPreview.length > 300;

    return (
      <div className={`p-4 rounded-lg border-2 ${opConfig.bg} ${opConfig.border} space-y-3 transition-all duration-200 hover:shadow-md`}>
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 ${opConfig.iconBg} rounded-full flex items-center justify-center text-lg`}>
              {opConfig.icon}
            </div>
            <div>
              <h3 className="font-semibold text-gray-800 text-lg">
                {opConfig.name}
              </h3>
              <p className="text-sm text-gray-600">
                {opConfig.description}
              </p>
            </div>
          </div>
          
          {/* Status indicator */}
          <div className="flex items-center space-x-2">
            {status.type === 'running' && (
              <div className="flex items-center space-x-2">
                <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                <span className="text-sm text-blue-600 font-medium">Processing...</span>
              </div>
            )}
            {status.type === 'complete' && parsedResult?.success && (
              <div className="flex items-center space-x-2">
                <span className="text-green-500 text-lg">✅</span>
                <span className="text-sm text-green-700 font-medium">Success</span>
              </div>
            )}
            {status.type === 'complete' && parsedResult?.error && (
              <div className="flex items-center space-x-2">
                <span className="text-red-500 text-lg">❌</span>
                <span className="text-sm text-red-700 font-medium">Error</span>
              </div>
            )}
          </div>
        </div>

        {/* Parameters Grid */}
        <div className="bg-white p-3 rounded-lg border space-y-2">
          <h4 className="font-medium text-gray-700 text-sm">Operation Parameters:</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-600">Operation:</span>
              <span className="px-2 py-1 bg-gray-100 rounded text-xs font-mono border">
                {args.operation}
              </span>
            </div>
            
            {args.file_path && (
              <div className="flex items-center space-x-2">
                <span className="font-medium text-gray-600">File:</span>
                <span className="px-2 py-1 bg-gray-100 rounded text-xs font-mono border truncate">
                  {args.file_path}
                </span>
              </div>
            )}
            
            {args.directory && (
              <div className="flex items-center space-x-2">
                <span className="font-medium text-gray-600">Directory:</span>
                <span className="px-2 py-1 bg-gray-100 rounded text-xs font-mono border">
                  {args.directory}
                </span>
              </div>
            )}
            
            {args.edit_mode && (
              <div className="flex items-center space-x-2">
                <span className="font-medium text-gray-600">Edit Mode:</span>
                <span className="px-2 py-1 bg-yellow-100 rounded text-xs font-mono border">
                  {args.edit_mode}
                </span>
              </div>
            )}

            {args.content && (
              <div className="col-span-full">
                <span className="font-medium text-gray-600">Content Length:</span>
                <span className="ml-2 px-2 py-1 bg-blue-100 rounded text-xs">
                  {args.content.length} characters
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {result && (
          <div className="space-y-3">
            {/* Results Header */}
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-700">Results:</h4>
              <div className="flex items-center space-x-2">
                {shouldShowExpandButton && (
                  <button
                    onClick={() => setShowFullContent(!showFullContent)}
                    className="text-sm text-blue-600 hover:text-blue-800 flex items-center space-x-1 transition-colors"
                  >
                    <span>{showFullContent ? 'Show Less' : 'Show More'}</span>
                    <span className={`transform transition-transform ${showFullContent ? 'rotate-180' : ''}`}>
                      ▼
                    </span>
                  </button>
                )}
                
                <button
                  onClick={() => navigator.clipboard.writeText(result)}
                  className="text-sm text-gray-600 hover:text-gray-800 flex items-center space-x-1 transition-colors"
                  title="Copy to clipboard"
                >
                  <span>📋</span>
                  <span>Copy</span>
                </button>
              </div>
            </div>
            
            {/* File List Display (for list operations) */}
            {parsedResult?.isFileList && parsedResult.files && parsedResult.files.length > 0 && (
              <div className="bg-white p-3 rounded border space-y-2">
                <h5 className="font-medium text-gray-700 text-sm">Files & Directories:</h5>
                <div className="grid grid-cols-1 gap-1">
                  {parsedResult.files.map((file, index) => (
                    <div 
                      key={index}
                      className="flex items-center p-2 bg-gray-50 rounded text-sm font-mono hover:bg-gray-100 transition-colors"
                    >
                      {file}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Content Display */}
            <div className="bg-white rounded border">
              {/* Content Preview/Full */}
              {args.operation === 'read' && contentPreview ? (
                <div className="p-3">
                  <h5 className="font-medium text-gray-700 text-sm mb-2">File Content:</h5>
                  <div className={`font-mono text-sm border rounded p-3 bg-gray-50 ${
                    showFullContent ? '' : 'max-h-40 overflow-hidden'
                  }`}>
                    <pre className="whitespace-pre-wrap break-words text-gray-800">
                      {showFullContent ? contentPreview : contentPreview.substring(0, 300) + (contentPreview.length > 300 ? '...' : '')}
                    </pre>
                  </div>
                </div>
              ) : (
                /* Full Result Display for non-read operations */
                <div className="p-3">
                  <div className="font-mono text-sm border rounded p-3 bg-gray-50 max-h-60 overflow-auto">
                    <pre className="whitespace-pre-wrap break-words text-gray-800">
                      {result}
                    </pre>
                  </div>
                </div>
              )}
            </div>

            {/* Quick Actions for Create/Edit Operations */}
            {parsedResult?.success && (args.operation === 'create' || args.operation === 'edit') && args.file_path && (
              <div className="bg-green-50 p-3 rounded border border-green-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-green-600">📄</span>
                    <span className="text-sm text-green-800 font-medium">
                      File {args.operation === 'create' ? 'created' : 'modified'}: {args.file_path}
                    </span>
                  </div>
                  <div className="text-xs text-green-600">
                    {args.operation === 'create' ? 'Ready for use' : 'Changes saved'}
                  </div>
                </div>
              </div>
            )}

            {/* Error Display */}
            {parsedResult?.error && (
              <div className="bg-red-50 p-3 rounded border border-red-200">
                <div className="flex items-start space-x-2">
                  <span className="text-red-500 text-lg flex-shrink-0">⚠️</span>
                  <div className="text-sm text-red-800">
                    <div className="font-medium mb-1">Operation Failed</div>
                    <pre className="whitespace-pre-wrap text-xs text-red-700 bg-red-100 p-2 rounded">
                      {parsedResult.error}
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Workflow Hints */}
        {!result && (
          <div className="bg-blue-50 p-3 rounded border border-blue-200">
            <div className="flex items-start space-x-2">
              <span className="text-blue-500">💡</span>
              <div className="text-sm text-blue-800">
                <div className="font-medium mb-1">File System Workflow:</div>
                <div className="text-xs space-y-1">
                  <div>• <strong>List</strong> files in knowledge_base to see available data</div>
                  <div>• <strong>Read</strong> files to analyze content</div>
                  <div>• <strong>Create</strong> reports and results in output directory</div>
                  <div>• <strong>Edit</strong> existing files to update content</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }
});