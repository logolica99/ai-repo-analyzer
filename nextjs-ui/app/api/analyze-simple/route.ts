import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    const { repo, analysisType, focus } = await request.json()
    
    if (!repo) {
      return NextResponse.json({ error: 'Repository is required' }, { status: 400 })
    }

    // Build the command
    let command = `github-repo-analyzer`
    let args: string[] = []

    switch (analysisType) {
      case 'basic':
        args = ['analyze', repo, '--format', 'json', '--max-stories', '3']
        break
      case 'comprehensive':
        args = ['analyze', repo, '--comprehensive', '--format', 'json', '--max-stories', '3']
        break
      case 'architecture':
        args = ['architecture', repo, '--format', 'json']
        break
      case 'tests':
        args = ['tests', repo, '--format', 'json', '--max-tests', '3']
        break
      case 'quick':
        args = ['quick', repo, '--format', 'json', '--max-stories', '2']
        break
      default:
        args = ['quick', repo, '--format', 'json', '--max-stories', '2']
    }

    if (focus) {
      args.push('--focus', focus)
    }

    // Add token if available
    const token = process.env.GITHUB_TOKEN
    if (token) {
      args.push('--token', token)
    }

    // Special case: Use pre-existing reports for saleor/saleor
    if (repo === 'saleor/saleor') {
      console.log('Using pre-existing reports for saleor/saleor')
      
      
      try {
        // Read all three pre-existing markdown reports
        const fs = require('fs')
        const path = require('path')
        
        const architecturePath = path.join(process.cwd(), '..', 'saleor-comprehensive-architecture.md')
        const storiesPath = path.join(process.cwd(), '..', 'saleor-stories.md')
        const testsPath = path.join(process.cwd(), '..', 'saleorcomprehensive-tests.md')
        
        const architectureContent = fs.readFileSync(architecturePath, 'utf8')
        const storiesContent = fs.readFileSync(storiesPath, 'utf8')
        const testsContent = fs.readFileSync(testsPath, 'utf8')
        
        // Combine all reports into a comprehensive analysis
        const combinedReport = `# Comprehensive Technical Analysis: saleor/saleor

## 📋 Table of Contents
1. [Architecture Analysis](#architecture-analysis)
2. [User Stories](#user-stories)
3. [Test Documentation](#test-documentation)

---

## 🏗️ Architecture Analysis

${architectureContent}

---

## 👥 User Stories

${storiesContent}

---

## 🧪 Test Documentation

${testsContent}

---

## 📊 Summary

This comprehensive analysis combines:
- **Architecture Analysis**: Complete system architecture with Mermaid diagrams
- **User Stories**: 5 detailed user stories with acceptance criteria
- **Test Documentation**: 5 test suites with 5 test cases covering security features

**Total Analysis Components:**
- Architecture diagrams: 4 Mermaid diagrams
- User stories: 5 comprehensive stories
- Test suites: 5 security-focused test suites
- Test cases: 5 unit test cases
`
        
        // Create a comprehensive result that matches our expected format
        const mockResult = {
          repository: {
            name: 'saleor/saleor',
            description: 'Saleor Core: the high performance, composable, headless commerce API.',
            language: 'Python',
            stars: 21992,
            forks: 5783,
            topics: ['python', 'store', 'commerce', 'shop', 'ecommerce', 'cart', 'graphql', 'headless', 'headless-commerce', 'multichannel', 'shopping-cart', 'composable', 'oms', 'pim', 'checkout', 'payments', 'order-management', 'e-commerce'],
            license: 'BSD 3-Clause "New" or "Revised" License',
            size: 238909,
            url: 'https://github.com/saleor/saleor'
          },
          analysisDate: new Date(),
          userStories: [
            {
              id: '1',
              title: 'Multi-Channel Product Management with Variant Support',
              description: 'As a product manager, I want to create and manage products with multiple variants across different sales channels',
              priority: 'High',
              acceptanceCriteria: ['Configurable attributes', 'Channel-specific pricing', 'SEO metadata', 'Media management']
            },
            {
              id: '2',
              title: 'Flexible Checkout with Multiple Payment Gateway Support',
              description: 'As a customer, I want to complete purchases through a flexible checkout process with multiple payment methods',
              priority: 'Critical',
              acceptanceCriteria: ['Multi-step checkout', 'Multiple payment gateways', 'Payment method combination', 'Real-time updates']
            },
            {
              id: '3',
              title: 'Advanced Order Fulfillment and Inventory Management',
              description: 'As a warehouse manager, I want to track and manage inventory across multiple warehouses',
              priority: 'High',
              acceptanceCriteria: ['Real-time inventory', 'Automated fulfillment', 'Stock reservations', 'Partial fulfillments']
            },
            {
              id: '4',
              title: 'Comprehensive Promotion and Discount Engine',
              description: 'As a marketing manager, I want to create and manage complex promotional campaigns',
              priority: 'Medium',
              acceptanceCriteria: ['Flexible discount types', 'Promotion conditions', 'Voucher codes', 'Performance tracking']
            },
            {
              id: '5',
              title: 'GraphQL API Integration with Webhook-Driven Automation',
              description: 'As a developer, I want to integrate external systems with Saleor\'s GraphQL API',
              priority: 'High',
              acceptanceCriteria: ['GraphQL endpoint', 'Webhook configuration', 'JWT authentication', 'Real-time subscriptions']
            }
          ],
          systemArchitecture: {
            overview: 'Headless e-commerce platform with GraphQL API, React frontend, and Python backend',
            components: [
              { name: 'GraphQL API', description: 'Core API layer with 12+ domain modules', technology: 'Python/Django' },
              { name: 'React Dashboard', description: 'Admin interface with real-time updates', technology: 'React/TypeScript' },
              { name: 'PostgreSQL', description: 'Primary database with full-text search', technology: 'PostgreSQL' },
              { name: 'Redis', description: 'Multi-purpose caching and task queue', technology: 'Redis' },
              { name: 'Celery', description: 'Background task processing', technology: 'Python/Celery' },
              { name: 'Docker', description: 'Containerized deployment', technology: 'Docker/Kubernetes' }
            ],
            dataFlow: 'Client → GraphQL API → Business Logic → Database → Background Tasks',
            deployment: 'Docker containers with Kubernetes orchestration'
          },
          apiAnalysis: {
            endpoints: [
              { method: 'POST', path: '/graphql/', description: 'GraphQL endpoint' },
              { method: 'POST', path: '/plugins/{plugin_id}/webhooks/', description: 'Plugin webhooks' },
              { method: 'GET', path: '/digital-download/{token}/', description: 'Digital downloads' },
              { method: 'GET', path: '/thumbnail/{image_id}/{size}/', description: 'Image thumbnails' },
              { method: 'GET', path: '/.well-known/jwks.json', description: 'JWKS endpoint' }
            ],
            authentication: 'JWT tokens with OAuth2 and webhook signatures',
            rateLimiting: 'Redis-based rate limiting with query complexity analysis',
            documentation: 'GraphQL schema with auto-generated docs and introspection'
          },
          technicalDeepDive: {
            performance: 'Optimized for high-traffic e-commerce with DataLoaders, Redis caching, and CDN',
            security: 'JWT authentication, role-based access control, webhook signatures, input validation',
            scalability: 'Horizontal scaling with multi-tenant architecture and event-driven design',
            monitoring: 'OpenTelemetry, Sentry error tracking, Prometheus metrics, distributed tracing'
          },
          comprehensiveReport: combinedReport
        }

        console.log('Mock result:', mockResult)
        
        return NextResponse.json({
          success: true,
          result: mockResult,
          command: 'Using pre-existing comprehensive reports',
          outputFile: 'saleor-comprehensive-analysis.md',
          preExisting: true,
          reportSources: [
            'saleor-comprehensive-architecture.md',
            'saleor-stories.md', 
            'saleorcomprehensive-tests.md'
          ]
        })
        
      } catch (error) {
        console.error('Error reading pre-existing reports:', error)
        // Fall back to normal analysis if file reading fails
      }
    }
    
    // Create output filename based on project name and analysis type
    const projectName = repo.replace('/', '_')
    const outputFile = `${projectName}_${analysisType}.json`
    
    // Use WSL to run the command in the virtual environment with better error handling
    const wslCommand = `wsl -e bash -c "cd /mnt/c/Users/juuba/claude-sdk-project-summarizer && source venv/bin/activate && timeout 1200 ${command} ${args.join(' ')} --output-file ${outputFile} || echo 'TIMEOUT_OR_ERROR'"`
    console.log(`Running WSL command: ${wslCommand}`)

    try {
      const { stdout, stderr } = await execAsync(wslCommand, {
        timeout: 1260000, // 21 minutes timeout (slightly more than the internal timeout)
        maxBuffer: 1024 * 1024 * 50, // 50MB buffer for large outputs
        killSignal: 'SIGKILL' // Use SIGKILL instead of SIGTERM
      })

      // Check if we got a timeout or error signal
      if (stdout.includes('TIMEOUT_OR_ERROR')) {
        return NextResponse.json({
          success: false,
          error: 'Analysis timed out after 20 minutes',
          stdout: stdout.replace('TIMEOUT_OR_ERROR', '').trim(),
          stderr: stderr,
          command: wslCommand,
          timeout: true,
          outputFile: outputFile
        }, { status: 408 }) // Request Timeout status
      }

      // Try to parse JSON output
      let result
      try {
        result = JSON.parse(stdout)
      } catch (parseError) {
        // If JSON parsing fails, return the raw output
        result = {
          rawOutput: stdout,
          error: stderr,
          success: true
        }
      }

      return NextResponse.json({
        success: true,
        result,
        command: wslCommand,
        outputFile: outputFile
      })

    } catch (execError: any) {
      console.error('Command execution error:', execError)
      
      // Check if we got partial output before the timeout
      const hasPartialOutput = execError.stdout && execError.stdout.length > 0
      
      return NextResponse.json({
        success: hasPartialOutput, // Consider it successful if we got some output
        error: execError.message,
        stderr: execError.stderr,
        stdout: execError.stdout,
        command: wslCommand,
        partial: hasPartialOutput,
        timeout: execError.signal === 'SIGTERM',
        outputFile: outputFile
      }, { status: hasPartialOutput ? 200 : 500 })
    }

  } catch (error) {
    console.error('Analysis error:', error)
    return NextResponse.json(
      { error: 'Failed to run analysis', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}
