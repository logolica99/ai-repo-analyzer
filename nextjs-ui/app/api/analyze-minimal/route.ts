import { NextRequest, NextResponse } from 'next/server'
import { executeCommand } from '../../../lib/system-utils'

export async function POST(request: NextRequest) {
  try {
    const { repo } = await request.json()
    
    if (!repo) {
      return NextResponse.json({ error: 'Repository is required' }, { status: 400 })
    }

    // Special case: Use pre-existing reports for saleor/saleor
    if (repo === 'saleor/saleor') {
      console.log('Using pre-existing reports for saleor/saleor (minimal)')
      
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
        
        // Create a minimal result that matches our expected format
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
          userStories: [],
          comprehensiveReport: `# Saleor Comprehensive Analysis (Minimal View)

## 🏗️ Architecture Overview
${architectureContent.split('## 🏗️ System Architecture')[1]?.split('## 🌐 API')[0] || architectureContent.substring(0, 2000)}...

## 👥 User Stories Summary
${storiesContent.split('📝 User Stories:')[1]?.substring(0, 1000) || storiesContent.substring(0, 1000)}...

## 🧪 Test Coverage
${testsContent.split('## 📊 Test Summary')[1]?.split('## 📈 Test Coverage')[0] || testsContent.substring(0, 500)}...

*[Full reports available in comprehensive analysis]*
`
        }
        
        return NextResponse.json({
          success: true,
          result: mockResult,
          command: 'Using pre-existing reports (minimal)',
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
    
    // Create output filename for minimal analysis
    const projectName = repo.replace('/', '_')
    const outputFile = `${projectName}_minimal.json`
    
    try {
      const { stdout, stderr } = await executeCommand({
        command: 'python',
        args: ['-m', 'github_repo_analyzer.cli', 'info', repo],
        cwd: process.cwd(),
        timeout: 300,
        outputFile
      })

      if (stdout.includes('TIMEOUT')) {
        return NextResponse.json({
          success: false,
          error: 'Analysis timed out',
          message: 'The analysis took too long. Try a different repository or check your internet connection.'
        }, { status: 408 })
      }

      // Return the raw output as a simple result
      return NextResponse.json({
        success: true,
        result: {
          repository: {
            name: repo,
            description: 'Repository information retrieved',
            language: 'Unknown',
            stars: 0,
            forks: 0,
            topics: [],
            license: 'Unknown',
            size: 0,
            url: `https://github.com/${repo}`
          },
          analysisDate: new Date(),
          userStories: [],
          comprehensiveReport: stdout
        },
        command: `python -m github_repo_analyzer.cli info ${repo}`,
        outputFile: outputFile
      })

    } catch (execError: any) {
      console.error('Minimal analysis error:', execError)
      
      return NextResponse.json({
        success: false,
        error: execError.message,
        stderr: execError.stderr,
        stdout: execError.stdout,
        command: `python -m github_repo_analyzer.cli info ${repo}`
      }, { status: 500 })
    }

  } catch (error) {
    console.error('Minimal analysis error:', error)
    return NextResponse.json(
      { error: 'Failed to run minimal analysis', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}
