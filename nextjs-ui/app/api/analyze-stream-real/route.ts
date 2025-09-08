import { NextRequest } from 'next/server'
import { spawn } from 'child_process'

export async function POST(request: NextRequest) {
  const { repo, analysisType, focus } = await request.json()
  
  if (!repo) {
    return new Response('Repository is required', { status: 400 })
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

  // Create output filename based on project name and analysis type
  const projectName = repo.replace('/', '_')
  const outputFile = `${projectName}_${analysisType}.json`
  args.push('--output-file', outputFile)

  // Use WSL to run the command in the virtual environment
  const wslCommand = `wsl -e bash -c "cd /mnt/c/Users/juuba/claude-sdk-project-summarizer && source venv/bin/activate && timeout 2700 ${command} ${args.join(' ')} || echo 'TIMEOUT_OR_ERROR'"`
  
  console.log(`Running WSL command: ${wslCommand}`)

  // Create a readable stream that captures the spawn output
  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder()
      
      // Send initial message
      controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
        type: 'output', 
        content: `🚀 Starting analysis for ${repo}...`,
        timestamp: new Date().toISOString()
      })}\n\n`))
      
      controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
        type: 'output', 
        content: `📋 Command: ${wslCommand}`,
        timestamp: new Date().toISOString()
      })}\n\n`))
      
      // Spawn the WSL process
      const wslProcess = spawn('wsl', ['-e', 'bash', '-c', `cd /mnt/c/Users/juuba/claude-sdk-project-summarizer && source venv/bin/activate && timeout 2700 ${command} ${args.join(' ')} || echo 'TIMEOUT_OR_ERROR'`], {
        stdio: ['pipe', 'pipe', 'pipe']
      })
      
      let stdout = ''
      let stderr = ''
      
      // Handle stdout
      wslProcess.stdout.on('data', (data) => {
        const output = data.toString()
        stdout += output
        
        // Send each line as a separate event
        const lines = output.split('\n').filter((line: string) => line.trim())
        lines.forEach((line: string) => {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
            type: 'output', 
            content: line.trim(),
            timestamp: new Date().toISOString()
          })}\n\n`))
        })
      })
      
      // Handle stderr
      wslProcess.stderr.on('data', (data) => {
        const output = data.toString()
        stderr += output
        
        // Send error output
        const lines = output.split('\n').filter((line: string) => line.trim())
        lines.forEach((line: string) => {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
            type: 'error', 
            content: line.trim(),
            timestamp: new Date().toISOString()
          })}\n\n`))
        })
      })
      
      // Handle process completion
      wslProcess.on('close', (code) => {
        console.log(`Process exited with code ${code}`)

       
        
        if (stdout.includes('TIMEOUT_OR_ERROR')) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
            type: 'error', 
            content: '⏰ Analysis timed out after 45 minutes',
            timestamp: new Date().toISOString()
          })}\n\n`))
          
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
            type: 'result', 
            data: {
              success: false,
              error: 'Analysis timed out after 45 minutes',
              timeout: true,
              outputFile: outputFile
            },
            timestamp: new Date().toISOString()
          })}\n\n`))
        } else if (code === 0) {
          // Try to read and parse the output JSON file
          try {
            const fs = require('fs')
            const path = require('path')
            const outputFilePath = path.join(process.cwd(), '..', outputFile)
            
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
              type: 'output', 
              content: `📄 Reading output file: ${outputFile}`,
              timestamp: new Date().toISOString()
            })}\n\n`))
            
            if (fs.existsSync(outputFilePath)) {
              const fileContent = fs.readFileSync(outputFilePath, 'utf8')
              const result = JSON.parse(fileContent)
              
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
                type: 'output', 
                content: '✅ Analysis completed successfully!',
                timestamp: new Date().toISOString()
              })}\n\n`))
              
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
                type: 'result', 
                data: {
                  success: true,
                  result: result,
                  outputFile: outputFile
                },
                timestamp: new Date().toISOString()
              })}\n\n`))
            } else {
              throw new Error(`Output file ${outputFile} not found`)
            }
          } catch (parseError: any) {
            console.error('Error reading/parsing output file:', parseError)
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
              type: 'output', 
              content: `⚠️ Analysis completed but output file parsing failed: ${parseError.message}`,
              timestamp: new Date().toISOString()
            })}\n\n`))
            
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
              type: 'result', 
              data: {
                success: true,
                result: {
                  repository: {
                    name: repo,
                    description: 'Repository analysis completed',
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
                outputFile: outputFile
              },
              timestamp: new Date().toISOString()
            })}\n\n`))
          }
        } else {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
            type: 'error', 
            content: `❌ Analysis failed with exit code ${code}`,
            timestamp: new Date().toISOString()
          })}\n\n`))
          
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
            type: 'result', 
            data: {
              success: false,
              error: `Process exited with code ${code}`,
              stderr: stderr,
              stdout: stdout,
              outputFile: outputFile
            },
            timestamp: new Date().toISOString()
          })}\n\n`))
        }
        
        controller.close()
      })
      
      // Handle process errors
      wslProcess.on('error', (error) => {
        console.error('Process error:', error)
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
          type: 'error', 
          content: `❌ Process error: ${error.message}`,
          timestamp: new Date().toISOString()
        })}\n\n`))
        
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
          type: 'result', 
          data: {
            success: false,
            error: error.message,
            outputFile: outputFile
          },
          timestamp: new Date().toISOString()
        })}\n\n`))
        
        controller.close()
      })
      
      // Set a timeout to prevent hanging
      setTimeout(() => {
        if (!wslProcess.killed) {
          wslProcess.kill('SIGTERM')
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
            type: 'error', 
            content: '⏰ Process timeout - killing process',
            timestamp: new Date().toISOString()
          })}\n\n`))
        }
      }, 2700000) // 45 minutes
    }
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
