import { spawn } from 'child_process'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export interface SystemInfo {
  isWindows: boolean
  isLinux: boolean
  isMacOS: boolean
  platform: string
}

export interface CommandOptions {
  command: string
  args: string[]
  cwd?: string
  timeout?: number
  outputFile?: string
}

export function detectSystem(): SystemInfo {
  const platform = process.platform
  return {
    isWindows: platform === 'win32',
    isLinux: platform === 'linux',
    isMacOS: platform === 'darwin',
    platform
  }
}

export function buildCommand(options: CommandOptions): { command: string; args: string[] } {
  const system = detectSystem()
  const { command, args, cwd = process.cwd(), timeout = 1200, outputFile } = options

  if (system.isWindows) {
    // Use WSL for Windows - go to parent directory where venv is located
    const parentDir = cwd.replace(/\\/g, '/').replace(/^([A-Z]):/, '/mnt/$1').toLowerCase().replace(/\/nextjs-ui$/, '')
    const wslCommand = `wsl -e bash -c "cd ${parentDir} && source venv/bin/activate && timeout ${timeout} ${command} ${args.join(' ')}${outputFile ? ` --output-file ${outputFile}` : ''} || echo 'TIMEOUT_OR_ERROR'"`
    
    return {
      command: 'wsl',
      args: ['-e', 'bash', '-c', `cd ${parentDir} && source venv/bin/activate && timeout ${timeout} ${command} ${args.join(' ')}${outputFile ? ` --output-file ${outputFile}` : ''} || echo 'TIMEOUT_OR_ERROR'`]
    }
  } else {
    // Use direct command for Linux/macOS - go to parent directory where venv is located
    const parentDir = cwd.replace(/nextjs-ui$/, '')
    const fullCommand = `${command} ${args.join(' ')}${outputFile ? ` --output-file ${outputFile}` : ''}`
    
    return {
      command: 'bash',
      args: ['-c', `cd ${parentDir} && source venv/bin/activate && timeout ${timeout} ${fullCommand} || echo 'TIMEOUT_OR_ERROR'`]
    }
  }
}

export function buildSpawnCommand(options: CommandOptions): { command: string; args: string[]; options: any } {
  const system = detectSystem()
  const { command, args, cwd = process.cwd() } = options

  if (system.isWindows) {
    // Use WSL for Windows - go to parent directory where venv is located
    const parentDir = cwd.replace(/\\/g, '/').replace(/^([A-Z]):/, '/mnt/$1').toLowerCase().replace(/\/nextjs-ui$/, '')
    
    return {
      command: 'wsl',
      args: ['-e', 'bash', '-c', `cd ${parentDir} && source venv/bin/activate && ${command} ${args.join(' ')}`],
      options: {
        cwd: process.cwd(),
        env: { ...process.env }
      }
    }
  } else {
    // Use direct command for Linux/macOS - go to parent directory where venv is located
    const parentDir = cwd.replace(/nextjs-ui$/, '')
    
    return {
      command: 'bash',
      args: ['-c', `cd ${parentDir} && source venv/bin/activate && ${command} ${args.join(' ')}`],
      options: {
        cwd: cwd,
        env: { ...process.env }
      }
    }
  }
}

export async function executeCommand(options: CommandOptions): Promise<{ stdout: string; stderr: string }> {
  const { command, args } = buildCommand(options)
  const fullCommand = `${command} ${args.join(' ')}`
  
  console.log(`Executing command: ${fullCommand}`)
  
  return await execAsync(fullCommand, {
    timeout: (options.timeout || 1200) * 1000 + 60000, // Add 1 minute buffer
    maxBuffer: 1024 * 1024 * 50, // 50MB buffer
    killSignal: 'SIGKILL'
  })
}

export function spawnCommand(options: CommandOptions): any {
  const { command, args, options: spawnOptions } = buildSpawnCommand(options)
  
  console.log(`Spawning command: ${command} ${args.join(' ')}`)
  
  return spawn(command, args, spawnOptions)
}
