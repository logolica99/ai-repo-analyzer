import { NextRequest, NextResponse } from 'next/server'
import { spawnCommand } from '../../../lib/system-utils'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    const { repo, analysisType, focus } = await request.json()
    
    if (!repo) {
      return NextResponse.json({ error: 'Repository is required' }, { status: 400 })
    }

    // Build the command based on analysis type
    let command = 'github-repo-analyzer'
    let args: string[] = []

    switch (analysisType) {
      case 'basic':
        args = ['analyze', repo, '--format', 'json']
        break
      case 'comprehensive':
        args = ['analyze', repo, '--comprehensive', '--format', 'json']
        break
      case 'architecture':
        args = ['architecture', repo, '--format', 'json']
        break
      case 'tests':
        args = ['tests', repo, '--format', 'json']
        break
      default:
        args = ['analyze', repo, '--comprehensive', '--format', 'json']
    }

    if (focus) {
      args.push('--focus', focus)
    }

    // Add token if available
    const token = process.env.GITHUB_TOKEN
    if (token) {
      args.push('--token', token)
    }

    console.log(`Running command: ${command} ${args.join(' ')}`)

    return new Promise<Response>((resolve) => {
      const child = spawnCommand({
        command,
        args,
        cwd: process.cwd()
      })

      let output = ''
      let errorOutput = ''
      let isComplete = false

      // Stream output in real-time
      const stream = new ReadableStream({
        start(controller) {
          child.stdout.on('data', (data: any) => {
            const chunk = data.toString()
            output += chunk
            controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ type: 'output', data: chunk })}\n\n`))
          })

          child.stderr.on('data', (data: any) => {
            const chunk = data.toString()
            errorOutput += chunk
            controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ type: 'error', data: chunk })}\n\n`))
          })

          child.on('close', (code: any) => {
            isComplete = true
            controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ type: 'complete', code, output, errorOutput })}\n\n`))
            controller.close()
          })

          child.on('error', (error: any) => {
            isComplete = true
            controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ type: 'error', error: error.message })}\n\n`))
            controller.close()
          })
        }
      })

      resolve(new Response(stream, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      }))
    })

  } catch (error) {
    console.error('Analysis error:', error)
    return NextResponse.json(
      { error: 'Failed to run analysis', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}
