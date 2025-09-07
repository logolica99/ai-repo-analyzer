# Installation Guide

This guide will help you install and set up the GitHub Repository Analyzer tool.

## Prerequisites

Before installing the tool, make sure you have:

1. **Python 3.10 or higher** installed on your system
2. **Node.js** installed (required for Claude Code CLI)
3. **Git** installed (for cloning the repository)

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd github-repo-analyzer
```

### Step 2: Install Claude Code CLI

The tool requires Claude Code CLI to be installed globally:

```bash
npm install -g @anthropic-ai/claude-code
```

**Note:** You'll need to have Claude Code access and be authenticated. Follow the [Claude Code documentation](https://github.com/anthropics/claude-code-sdk-python) for setup instructions.

### Step 3: Install Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

### Step 4: Verify Installation

Check if the tool is properly installed:

```bash
github-repo-analyzer --help
```

You should see the help message with available commands.

## Configuration

### Option 1: Environment Variables

Set these environment variables for convenience:

```bash
# GitHub personal access token (recommended for higher rate limits)
export GITHUB_TOKEN="your_github_token_here"

# Custom Claude system prompt (optional)
export CLAUDE_SYSTEM_PROMPT="Your custom system prompt here"

# Default output format (optional)
export OUTPUT_FORMAT="markdown"
```

### Option 2: Configuration File

Create a configuration file in your home directory:

```bash
cp .github-analyzer-config.yaml ~/.github-analyzer-config.yaml
```

Then edit the file to customize your settings.

### Option 3: Command Line Options

Pass configuration options directly via command line (see usage examples below).

## Getting a GitHub Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select the following scopes:
   - `repo` (for private repositories)
   - `read:org` (if analyzing organization repositories)
4. Copy the generated token and use it with the `--token` option or set it as an environment variable

## Usage Examples

### Basic Analysis

Analyze a public repository:

```bash
github-repo-analyzer analyze facebook/react
```

### Analysis with Custom Options

```bash
github-repo-analyzer analyze microsoft/vscode \
  --focus "developer productivity" \
  --max-stories 8 \
  --format markdown \
  --output-file vscode-stories.md
```

### Quick Analysis

Use the quick command for faster analysis with defaults:

```bash
github-repo-analyzer quick django/django
```

### Check Rate Limits

Monitor your GitHub API usage:

```bash
github-repo-analyzer rate-limit --token your_token
```

### Get Repository Info

Get basic information without generating user stories:

```bash
github-repo-analyzer info facebook/react
```

## Troubleshooting

### Common Issues

**"Claude Code not found"**
- Ensure Claude Code CLI is installed: `npm install -g @anthropic-ai/claude-code`
- Check if it's in your PATH: `which claude-code`

**"GitHub API rate limit exceeded"**
- Use a GitHub token for higher rate limits
- Wait for the rate limit to reset
- Check current limits: `github-repo-analyzer rate-limit`

**"Repository not found"**
- Verify the repository name format: `owner/repo-name`
- Check if you have access to the repository
- Verify your GitHub token permissions

**"Module not found" errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)

### Getting Help

1. Check the [README.md](README.md) for detailed documentation
2. Run with verbose mode: `github-repo-analyzer --verbose analyze owner/repo`
3. Check the [examples](examples/) directory for usage examples
4. Review the configuration file for customization options

## Development Setup

If you want to contribute to the project:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black github_repo_analyzer/

# Lint code
flake8 github_repo_analyzer/

# Type checking
mypy github_repo_analyzer/
```

## Next Steps

After installation:

1. Try analyzing a simple repository: `github-repo-analyzer analyze facebook/react`
2. Experiment with different focus areas and output formats
3. Customize the system prompt for your specific needs
4. Set up a GitHub token for higher rate limits
5. Explore the configuration options

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error messages carefully
3. Try running with `--verbose` for more details
4. Check the [GitHub issues](https://github.com/yourusername/github-repo-analyzer/issues) page
5. Create a new issue with detailed error information

Happy analyzing! 🚀
