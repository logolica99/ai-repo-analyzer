'use client'

import { useEffect, useRef, useState } from 'react'
import { Copy, Check, ExternalLink, ZoomIn, ZoomOut, RotateCcw, Move } from 'lucide-react'

interface MermaidDiagramProps {
  diagram: string
  title: string
}

export default function MermaidDiagram({ diagram, title }: MermaidDiagramProps) {
  const [copied, setCopied] = useState(false)
  const [isLoaded, setIsLoaded] = useState(false)
  const [renderError, setRenderError] = useState(false)
  const [zoomLevel, setZoomLevel] = useState(1)
  const [isPanning, setIsPanning] = useState(false)
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 })
  const [lastPanPoint, setLastPanPoint] = useState({ x: 0, y: 0 })
  const diagramRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const loadMermaid = async () => {
      try {
        // Dynamic import with proper error handling
        const mermaid = await import('mermaid')
        
        // Initialize mermaid with proper configuration
        mermaid.default.initialize({
          startOnLoad: false,
          theme: 'default',
          securityLevel: 'loose',
          fontFamily: 'inherit',
          flowchart: {
            useMaxWidth: true,
            htmlLabels: true
          },
          sequence: {
            useMaxWidth: true
          },
          gantt: {
            useMaxWidth: true
          }
        })
        
        setIsLoaded(true)
        setRenderError(false)
      } catch (error) {
        console.error('Failed to load Mermaid:', error)
        setRenderError(true)
      }
    }

    loadMermaid()
  }, [])

  useEffect(() => {
    if (isLoaded && diagramRef.current && diagram && !renderError) {
      const renderDiagram = async () => {
        try {
          const mermaid = await import('mermaid')
          const element = diagramRef.current
          if (element) {
            element.innerHTML = ''
            const id = `mermaid-${title.replace(/\s+/g, '-').toLowerCase()}-${Date.now()}`
            const { svg } = await mermaid.default.render(id, diagram)
            element.innerHTML = svg
          }
        } catch (error) {
          console.error('Failed to render diagram:', error)
          setRenderError(true)
          if (diagramRef.current) {
            diagramRef.current.innerHTML = `
              <div class="text-center p-8 text-gray-500">
                <p class="text-red-600 font-medium">Failed to render diagram</p>
                <p class="text-sm mt-2">Copy the code below to view at <a href="https://mermaid.live" target="_blank" class="text-blue-600 hover:underline">mermaid.live</a></p>
              </div>
            `
          }
        }
      }

      renderDiagram()
    }
  }, [isLoaded, diagram, title, renderError])

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(diagram)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy diagram code: ', err)
    }
  }

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev * 1.2, 3))
  }

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev / 1.2, 0.3))
  }

  const handleReset = () => {
    setZoomLevel(1)
    setPanOffset({ x: 0, y: 0 })
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) { // Left mouse button
      setIsPanning(true)
      setLastPanPoint({ x: e.clientX, y: e.clientY })
    }
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      const deltaX = e.clientX - lastPanPoint.x
      const deltaY = e.clientY - lastPanPoint.y
      setPanOffset(prev => ({
        x: prev.x + deltaX,
        y: prev.y + deltaY
      }))
      setLastPanPoint({ x: e.clientX, y: e.clientY })
    }
  }

  const handleMouseUp = () => {
    setIsPanning(false)
  }

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    setZoomLevel(prev => Math.max(0.3, Math.min(3, prev * delta)))
  }

  if (renderError) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-medium text-gray-900">{title}</h4>
          <div className="flex items-center space-x-2">
            <button
              onClick={copyToClipboard}
              className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              <span>{copied ? 'Copied!' : 'Copy Code'}</span>
            </button>
            <a
              href="https://mermaid.live"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded"
            >
              <ExternalLink className="h-4 w-4" />
              <span>View Online</span>
            </a>
          </div>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="text-center">
            <p className="text-red-600 font-medium mb-2">Diagram Rendering Failed</p>
            <p className="text-sm text-red-500 mb-4">
              The Mermaid diagram could not be rendered. This might be due to a syntax error or browser compatibility issue.
            </p>
            <a
              href="https://mermaid.live"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              <ExternalLink className="h-4 w-4" />
              <span>View at Mermaid Live</span>
            </a>
          </div>
        </div>
        
        <details className="text-sm">
          <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
            View Diagram Code
          </summary>
          <pre className="mt-2 p-4 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto">
            <code>{diagram}</code>
          </pre>
        </details>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-gray-900">{title}</h4>
        <div className="flex items-center space-x-2">
          <button
            onClick={copyToClipboard}
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
          >
            {copied ? (
              <Check className="h-4 w-4 text-green-600" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
            <span>{copied ? 'Copied!' : 'Copy Code'}</span>
          </button>
          <a
            href="https://mermaid.live"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded"
          >
            <ExternalLink className="h-4 w-4" />
            <span>View Online</span>
          </a>
        </div>
      </div>

      {/* Zoom Controls */}
      <div className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Zoom & Pan:</span>
          <button
            onClick={handleZoomOut}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded"
            title="Zoom Out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <span className="text-sm font-medium text-gray-700 min-w-[3rem] text-center">
            {Math.round(zoomLevel * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded"
            title="Zoom In"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            onClick={handleReset}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded"
            title="Reset View"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Move className="h-4 w-4" />
          <span>Drag to pan • Scroll to zoom</span>
        </div>
      </div>
      
      <div 
        ref={containerRef}
        className="mermaid-container border border-gray-200 rounded-lg overflow-hidden bg-white"
        style={{ 
          height: '600px',
          cursor: isPanning ? 'grabbing' : 'grab'
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      >
        {!isLoaded ? (
          <div className="text-center p-8 text-gray-500">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p>Loading diagram...</p>
          </div>
        ) : (
          <div 
            ref={diagramRef} 
            className="w-full h-full"
            style={{
              transform: `scale(${zoomLevel}) translate(${panOffset.x / zoomLevel}px, ${panOffset.y / zoomLevel}px)`,
              transformOrigin: 'top left',
              transition: isPanning ? 'none' : 'transform 0.1s ease-out'
            }}
          />
        )}
      </div>
      
      <details className="text-sm">
        <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
          View Diagram Code
        </summary>
        <pre className="mt-2 p-4 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto">
          <code>{diagram}</code>
        </pre>
      </details>
    </div>
  )
}