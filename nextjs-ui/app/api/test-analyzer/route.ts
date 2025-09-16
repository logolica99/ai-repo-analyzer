import { NextRequest, NextResponse } from 'next/server'
import { executeCommand } from '../../../lib/system-utils'

export async function GET() {
  try {
    // Test if the analyzer is working with a simple command
    console.log(`Testing analyzer...`)

    const { stdout, stderr } = await executeCommand({
      command: 'python',
      args: ['-m', 'github_repo_analyzer.cli', '--help'],
      cwd: process.cwd(),
      timeout: 30
    })

    return NextResponse.json({
      success: true,
      stdout: stdout,
      stderr: stderr,
      message: 'Analyzer is working correctly'
    })

  } catch (error: any) {
    console.error('Test error:', error)
    
    return NextResponse.json({
      success: false,
      error: error.message,
      stderr: error.stderr,
      stdout: error.stdout,
      message: 'Analyzer test failed'
    }, { status: 500 })
  }
}
