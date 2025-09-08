import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function GET() {
  try {
    // Test if the analyzer is working with a simple command
    const testCommand = `wsl -e bash -c "cd /mnt/c/Users/juuba/claude-sdk-project-summarizer && source venv/bin/activate && python -m github_repo_analyzer.cli --help"`
    
    console.log(`Testing analyzer with: ${testCommand}`)

    const { stdout, stderr } = await execAsync(testCommand, {
      timeout: 30000, // 30 seconds
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
