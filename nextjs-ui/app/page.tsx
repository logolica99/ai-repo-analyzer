'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Github, 
  Terminal, 
  FileText, 
  BarChart3, 
  Zap,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react'
import RepositorySelector from '@/components/RepositorySelector'
import TerminalOutput from '@/components/TerminalOutput'
import ReportViewer from '@/components/ReportViewer'
import { Repository, AnalysisResult } from '@/types'

const testRepositories: Repository[] = [
  {
    id: 'saleor',
    name: 'saleor/saleor',
    description: 'Saleor Core: the high performance, composable, headless commerce API',
    language: 'Python',
    stars: 21992,
    forks: 5782,
    topics: ['python', 'graphql', 'ecommerce', 'headless', 'commerce'],
    license: 'BSD-3-Clause',
    size: 238909,
    url: 'https://github.com/saleor/saleor'
  },
  {
    id: 'ghost',
    name: 'TryGhost/Ghost',
    description: 'Turn your audience into a business. Publishing, memberships, subscriptions and newsletters.',
    language: 'JavaScript',
    stars: 45000,
    forks: 9500,
    topics: ['javascript', 'nodejs', 'cms', 'blog', 'publishing'],
    license: 'MIT',
    size: 150000,
    url: 'https://github.com/TryGhost/Ghost'
  },
  {
    id: 'mastodon',
    name: 'mastodon/mastodon',
    description: 'Your self-hosted, globally interconnected microblogging community',
    language: 'Ruby',
    stars: 45000,
    forks: 6800,
    topics: ['ruby', 'rails', 'social', 'microblogging', 'federated'],
    license: 'AGPL-3.0',
    size: 200000,
    url: 'https://github.com/mastodon/mastodon'
  },
  {
    id: 'monica',
    name: 'monicahq/monica',
    description: 'Personal CRM. Remember everything about your friends, family and business relationships.',
    language: 'PHP',
    stars: 19000,
    forks: 1800,
    topics: ['php', 'laravel', 'crm', 'personal', 'relationships'],
    license: 'AGPL-3.0',
    size: 50000,
    url: 'https://github.com/monicahq/monica'
  },
  {
    id: 'bulletproof-react',
    name: 'alan2207/bulletproof-react',
    description: 'A simple, scalable, and powerful architecture for building production ready React applications.',
    language: 'TypeScript',
    stars: 32700,
    forks: 3000,
    topics: ['react', 'react-applications', 'react-typescript', 'react-best-practice', 'react-guidelines', 'react-architecture-patterns', 'react-project-structure'],
    license: 'MIT',
    size: 15000,
    url: 'https://github.com/alan2207/bulletproof-react'
  }
]

export default function Home() {
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null)
  const [analysisType, setAnalysisType] = useState<'basic' | 'comprehensive' | 'architecture' | 'tests' | 'quick'>('quick')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [terminalOutput, setTerminalOutput] = useState<string[]>([])
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [currentStep, setCurrentStep] = useState(0)

  const analysisSteps = [
    'Fetching repository information...',
    'Conducting web research...',
    'Analyzing with Claude AI...',
    'Generating comprehensive report...',
    'Creating architecture diagrams...',
    'Analysis complete!'
  ]

  const runRealAnalysis = async () => {
    if (!selectedRepo) return

    setIsAnalyzing(true)
    setTerminalOutput([])
    setAnalysisResult(null)
    setCurrentStep(0)

    // Add initial command to terminal
    setTerminalOutput([`$ github-repo-analyzer ${analysisType} "${selectedRepo.name}" --comprehensive --format json`])
    setCurrentStep(1)

    try {
      // Use streaming API for real-time output
      const apiEndpoint = selectedRepo.name === 'saleor/saleor' 
        ? '/api/analyze-stream' 
        : '/api/analyze-stream-real'
      
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo: selectedRepo.name,
          analysisType: analysisType,
          focus: 'comprehensive'
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body reader available')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep the last incomplete line in buffer
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'output') {
                setTerminalOutput(prev => [...prev, data.content])
              } else if (data.type === 'error') {
                setTerminalOutput(prev => [...prev, `❌ ${data.content}`])
              } else if (data.type === 'result') {
                if (data.data && data.data.success !== false) {
                  setCurrentStep(5)
                  
                  // Handle the result data structure from the streaming API
                  const resultData = data.data.result || data.data
                  const realResult: AnalysisResult = {
                    repository: selectedRepo,
                    analysisDate: new Date(),
                    userStories: resultData?.userStories || [],
                    systemArchitecture: resultData?.systemArchitecture,
                    apiAnalysis: resultData?.apiAnalysis,
                    technicalDeepDive: resultData?.technicalDeepDive,
                    comprehensiveReport: resultData?.comprehensiveReport || resultData?.rawOutput
                  }
                  console.log('realResult', realResult)
                  setAnalysisResult(realResult)
                } else {
                  console.log('Analysis failed:', data.data)
                  setTerminalOutput(prev => [
                    ...prev,
                    '',
                    '❌ Analysis failed',
                    `   Error: ${data.data?.error || 'Unknown error'}`,
                    data.data?.outputFile ? `   Output File: ${data.data.outputFile}` : ''
                  ])
                  setCurrentStep(5)
                }
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError)
            }
          }
        }
      }
    } catch (error) {
    
      console.error('Analysis error:', error)
      setTerminalOutput(prev => [
        ...prev,
        '',
        '❌ Analysis failed',
        `   Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        '',
        'Please check your connection and try again.'
      ])
      setCurrentStep(5)
    }

    setIsAnalyzing(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Github className="h-8 w-8 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">
                GitHub Repository Analyzer
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">AI-Powered Analysis</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-600">Ready</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel - Repository Selection & Terminal */}
          <div className="space-y-6">
            {/* Repository Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-white rounded-lg shadow-sm border p-6"
            >
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-blue-600" />
                Select Repository
              </h2>
              <RepositorySelector
                repositories={testRepositories}
                selectedRepo={selectedRepo}
                onSelectRepo={setSelectedRepo}
                disabled={isAnalyzing}
              />
            </motion.div>

            {/* Analysis Type Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="bg-white rounded-lg shadow-sm border p-6"
            >
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-green-600" />
                Analysis Type
              </h2>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: 'quick', label: 'Quick', desc: 'Fast analysis (2 stories)' },
                  { id: 'basic', label: 'Basic', desc: 'User stories only (3 stories)' },
                  { id: 'comprehensive', label: 'Comprehensive', desc: 'Full analysis + diagrams' },
                  { id: 'architecture', label: 'Architecture', desc: 'Technical diagrams only' },
                  { id: 'tests', label: 'Tests', desc: 'Test generation' }
                ].map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setAnalysisType(type.id as any)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      analysisType === type.id
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    disabled={isAnalyzing}
                  >
                    <div className="font-medium">{type.label}</div>
                    <div className="text-sm text-gray-500">{type.desc}</div>
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Terminal Output */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-white rounded-lg shadow-sm border p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Terminal className="h-5 w-5 mr-2 text-gray-600" />
                  Terminal Output
                </h2>
                <button
                  onClick={runRealAnalysis}
                  disabled={!selectedRepo || isAnalyzing}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <Zap className="h-4 w-4" />
                  <span>{isAnalyzing ? 'Analyzing...' : 'Run Real Analysis'}</span>
                </button>
              </div>
              
              <TerminalOutput 
                output={terminalOutput}
                isAnalyzing={isAnalyzing}
                currentStep={currentStep}
                steps={analysisSteps}
              />
            </motion.div>
          </div>

          {/* Right Panel - Report Viewer */}
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="bg-white rounded-lg shadow-sm border p-6"
            >
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-purple-600" />
                Analysis Report
              </h2>
              
              {analysisResult ? (
                <ReportViewer result={analysisResult} />
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">
                    Select a repository and run analysis to view the comprehensive report
                  </p>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </main>
    </div>
  )
}
