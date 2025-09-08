'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  FileText, 
  BarChart3, 
  Code, 
  Database, 
  Shield, 
  Zap,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Copy,
  Check
} from 'lucide-react'
import { AnalysisResult } from '@/types'
import MermaidDiagram from './MermaidDiagram'

interface ReportViewerProps {
  result: AnalysisResult
}

export default function ReportViewer({ result }: ReportViewerProps) {
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']))
  const [copiedText, setCopiedText] = useState<string | null>(null)

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText },
    { id: 'architecture', label: 'Architecture', icon: BarChart3 },
    { id: 'api', label: 'API & Integrations', icon: Code },
    { id: 'technical', label: 'Technical Deep Dive', icon: Database },
    { id: 'stories', label: 'User Stories', icon: FileText },
    { id: 'report', label: 'Full Report', icon: FileText }
  ]

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId)
    } else {
      newExpanded.add(sectionId)
    }
    setExpandedSections(newExpanded)
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(text)
      setTimeout(() => setCopiedText(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Repository Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Repository Summary</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Description</p>
            <p className="font-medium text-gray-900">{result.repository.description}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Language</p>
            <p className="font-medium text-gray-900">{result.repository.language}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Stars</p>
            <p className="font-medium text-gray-900">{result.repository.stars.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Forks</p>
            <p className="font-medium text-gray-900">{result.repository.forks.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <span className="font-medium text-gray-900">User Stories</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">{result.userStories.length}</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-green-600" />
            <span className="font-medium text-gray-900">Architecture Diagrams</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">4</p>
        </div>
      </div>

      {/* Analysis Date */}
      <div className="text-sm text-gray-500">
        Analysis completed on {result.analysisDate.toLocaleDateString()} at {result.analysisDate.toLocaleTimeString()}
      </div>
    </div>
  )

  const renderArchitecture = () => (
    <div className="space-y-6">
      {result.systemArchitecture && (
        <>
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Architecture</h3>
            <MermaidDiagram 
              diagram={result.systemArchitecture.systemDiagram}
              title="Overall System Architecture"
            />
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">API Flow</h3>
            <MermaidDiagram 
              diagram={result.systemArchitecture.apiFlowDiagram}
              title="API Request/Response Flow"
            />
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Component Architecture</h3>
            <MermaidDiagram 
              diagram={result.systemArchitecture.componentDiagram}
              title="Internal Component Structure"
            />
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Flow</h3>
            <MermaidDiagram 
              diagram={result.systemArchitecture.dataFlowDiagram}
              title="Data Processing Flow"
            />
          </div>
        </>
      )}
    </div>
  )

  const renderApi = () => (
    <div className="space-y-6">
      {result.apiAnalysis && (
        <>
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">API Endpoints</h3>
            <div className="space-y-2">
              {result.apiAnalysis.endpoints.map((endpoint, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded">
                  <Code className="h-4 w-4 text-blue-600" />
                  <code className="text-sm font-mono text-gray-900">{endpoint}</code>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">External Services</h3>
            <div className="grid grid-cols-2 gap-3">
              {result.apiAnalysis.externalServices.map((service, index) => (
                <div key={index} className="flex items-center space-x-2 p-3 bg-green-50 rounded">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-900">{service}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Authentication Methods</h3>
            <div className="space-y-2">
              {result.apiAnalysis.authenticationMethods.map((method, index) => (
                <div key={index} className="flex items-center space-x-2 p-3 bg-yellow-50 rounded">
                  <Shield className="h-4 w-4 text-yellow-600" />
                  <span className="text-sm text-gray-900">{method}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">WebSocket Events</h3>
            <div className="space-y-2">
              {result.apiAnalysis.websocketEvents.map((event, index) => (
                <div key={index} className="flex items-center space-x-2 p-3 bg-purple-50 rounded">
                  <Zap className="h-4 w-4 text-purple-600" />
                  <span className="text-sm text-gray-900">{event}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )

  const renderTechnical = () => (
    <div className="space-y-6">
      {result.technicalDeepDive && (
        <>
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Technology Stack</h3>
            <div className="grid grid-cols-2 gap-6">
              {Object.entries(result.technicalDeepDive.technologyStack).map(([category, technologies]) => (
                <div key={category}>
                  <h4 className="font-medium text-gray-900 mb-2 capitalize">{category.replace('_', ' ')}</h4>
                  <div className="space-y-1">
                    {technologies.map((tech, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                        <span className="text-sm text-gray-700">{tech}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Build System</h3>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(result.technicalDeepDive.buildSystem).map(([key, value]) => (
                <div key={key}>
                  <p className="text-sm text-gray-600 capitalize">{key.replace('_', ' ')}</p>
                  <p className="font-medium text-gray-900">{value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Optimizations</h3>
            <div className="space-y-2">
              {result.technicalDeepDive.performanceOptimizations.map((optimization, index) => (
                <div key={index} className="flex items-center space-x-2 p-3 bg-blue-50 rounded">
                  <Zap className="h-4 w-4 text-blue-600" />
                  <span className="text-sm text-gray-900">{optimization}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Features</h3>
            <div className="space-y-2">
              {result.technicalDeepDive.securityFeatures.map((feature, index) => (
                <div key={index} className="flex items-center space-x-2 p-3 bg-green-50 rounded">
                  <Shield className="h-4 w-4 text-green-600" />
                  <span className="text-sm text-gray-900">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )

  const renderStories = () => (
    <div className="space-y-6">
      {result.userStories.map((story, index) => (
        <div key={story.id} className="bg-white border rounded-lg p-6">
          <div className="flex items-start justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Story {index + 1}: {story.title}
            </h3>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                story.priority === 'High' ? 'bg-red-100 text-red-700' :
                story.priority === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-green-100 text-green-700'
              }`}>
                {story.priority} Priority
              </span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                story.effort === 'High' ? 'bg-red-100 text-red-700' :
                story.effort === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-green-100 text-green-700'
              }`}>
                {story.effort} Effort
              </span>
            </div>
          </div>
          
          <p className="text-gray-700 mb-4">{story.description}</p>
          
          <div className="mb-4">
            <h4 className="font-medium text-gray-900 mb-2">Acceptance Criteria:</h4>
            <ul className="space-y-1">
              {story.acceptanceCriteria.map((criterion, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-sm text-gray-700">{criterion}</span>
                </li>
              ))}
            </ul>
          </div>
          
          {story.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {story.tags.map((tag, idx) => (
                <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )

  const renderFullReport = () => {
    // Parse markdown content and extract Mermaid diagrams
    const parseMarkdownContent = (content: string) => {
      if (!content) return { html: '', diagrams: [] }
      
      // Extract Mermaid diagrams from markdown
      const mermaidRegex = /```mermaid\n([\s\S]*?)\n```/g
      const diagrams: string[] = []
      let match
      
      while ((match = mermaidRegex.exec(content)) !== null) {
        diagrams.push(match[1])
      }
      
      // Replace Mermaid code blocks with placeholders
      let processedContent = content.replace(mermaidRegex, (match, diagram) => {
        const index = diagrams.length - 1
        return `\n\n<div class="mermaid-placeholder" data-diagram-index="${index}"></div>\n\n`
      })
      
      return { html: processedContent, diagrams }
    }

    const { html, diagrams } = parseMarkdownContent(result.comprehensiveReport || '')

    return (
      <div className="space-y-6">
        <div className="bg-white border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Full Technical Report</h3>
            <button
              onClick={() => copyToClipboard(result.comprehensiveReport || '')}
              className="flex items-center space-x-2 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
            >
              {copiedText === result.comprehensiveReport ? (
                <Check className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              <span>Copy Report</span>
            </button>
          </div>
          
          <div className="prose prose-slate max-w-none">
            <div 
              className="markdown-content"
              dangerouslySetInnerHTML={{ 
                __html: html.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>')
              }} 
            />
            
            {/* Render Mermaid diagrams */}
            {diagrams.map((diagram, index) => (
              <div key={index} className="my-8">
                <MermaidDiagram 
                  diagram={diagram}
                  title={`Architecture Diagram ${index + 1}`}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview()
      case 'architecture':
        return renderArchitecture()
      case 'api':
        return renderApi()
      case 'technical':
        return renderTechnical()
      case 'stories':
        return renderStories()
      case 'report':
        return renderFullReport()
      default:
        return renderOverview()
    }
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="min-h-96"
      >
        {renderTabContent()}
      </motion.div>
    </div>
  )
}
