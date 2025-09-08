'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Terminal, CheckCircle, Clock, AlertCircle } from 'lucide-react'

interface TerminalOutputProps {
  output: string[]
  isAnalyzing: boolean
  currentStep: number
  steps: string[]
}

export default function TerminalOutput({
  output,
  isAnalyzing,
  currentStep,
  steps
}: TerminalOutputProps) {
  const terminalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [output])

  const getLineClass = (line: string) => {
    if (line.startsWith('$')) return 'terminal-prompt'
    if (line.startsWith('✅')) return 'terminal-success'
    if (line.startsWith('❌')) return 'terminal-error'
    if (line.startsWith('⚠️')) return 'terminal-warning'
    if (line.startsWith('🔍') || line.startsWith('📊') || line.startsWith('🏗️') || line.startsWith('🌐') || line.startsWith('🔧') || line.startsWith('📝') || line.startsWith('💾')) return 'terminal-command'
    return 'terminal-output'
  }

  return (
    <div className="space-y-4">
      {/* Progress Indicator */}
      {isAnalyzing && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-gray-700">Analysis in Progress</span>
            </div>
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / steps.length) * 100}%` }}
              />
            </div>
            <span className="text-sm text-gray-500">{currentStep}/{steps.length}</span>
          </div>
          
          <div className="space-y-2">
            {steps.map((step, index) => (
              <div
                key={index}
                className={`flex items-center space-x-2 text-sm ${
                  index < currentStep
                    ? 'text-green-600'
                    : index === currentStep
                    ? 'text-blue-600'
                    : 'text-gray-400'
                }`}
              >
                {index < currentStep ? (
                  <CheckCircle className="h-4 w-4" />
                ) : index === currentStep ? (
                  <Clock className="h-4 w-4 animate-spin" />
                ) : (
                  <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
                )}
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Terminal Output */}
      <div
        ref={terminalRef}
        className="terminal h-96 overflow-y-auto custom-scrollbar"
      >
        {output.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <Terminal className="h-8 w-8 mx-auto mb-2 text-gray-300" />
              <p>Terminal output will appear here when analysis starts...</p>
            </div>
          </div>
        ) : (
          <div className="space-y-1">
            {output.map((line, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`terminal-line ${getLineClass(line)}`}
              >
                {line}
              </motion.div>
            ))}
            
            {isAnalyzing && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="terminal-line terminal-prompt"
              >
                <span className="loading-dots">Processing</span>
              </motion.div>
            )}
          </div>
        )}
      </div>

      {/* Status Bar */}
      {output.length > 0 && (
        <div className="flex items-center justify-between text-xs text-gray-500 bg-gray-50 px-3 py-2 rounded">
          <div className="flex items-center space-x-4">
            <span>Lines: {output.length}</span>
            <span>Status: {isAnalyzing ? 'Running' : 'Complete'}</span>
          </div>
          <div className="flex items-center space-x-2">
            {isAnalyzing ? (
              <>
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <span>Running</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Ready</span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
