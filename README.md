# GitHub Repository Analyzer

A powerful CLI tool that analyzes GitHub repositories and generates comprehensive user stories using Claude Code SDK. This tool can understand repository structure, code patterns, and generate actionable user stories for development teams.

## Features

- 🔍 **Repository Analysis**: Deep analysis of GitHub repositories including code structure, dependencies, and patterns
- 📝 **User Story Generation**: AI-powered generation of user stories based on repository analysis
- 🏗️ **System Architecture Analysis**: Generate comprehensive Mermaid diagrams for system architecture, API flows, and data flows
- 🌐 **API Endpoint Mapping**: Automatically identify and document API endpoints, external integrations, and service communications
- 🔧 **Technical Deep Dive**: Analyze technology stack, build systems, testing frameworks, and deployment strategies
- 🧪 **Test Generation**: Generate comprehensive test cases and documentation based on user stories
- 🌐 **Internet Access**: Can research and gather additional context from the web
- 🎯 **Smart Context**: Understands project purpose, tech stack, and user needs
- 📊 **Rich Output**: Beautiful terminal output with formatted user stories and interactive architecture diagrams
- ⚡ **Fast Processing**: Efficient analysis using Claude Code SDK

## Prerequisites

- Python 3.10+
- Node.js
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
- GitHub access (for private repositories, you'll need a GitHub token)

## Installation

### From Source

```bash
git clone <your-repo-url>
cd github-repo-analyzer
pip install -e .
```

### Using pip

```bash
pip install github-repo-analyzer
```

## Testing

To run tests for the GitHub Repository Analyzer project:

### Prerequisites for Testing

- Python 3.10+
- Virtual environment activated
- All dependencies installed

### Running Tests

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate     # On Windows

# Install in development mode
pip install -e .

# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_test_generation.py -v

# Run tests with coverage
python -m pytest --cov=github_repo_analyzer

# Run tests and generate HTML coverage report
python -m pytest --cov=github_repo_analyzer --cov-report=html
```

### Test Structure

The test suite includes:
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **CLI Tests**: Test command-line interface functionality
- **Type Tests**: Validate data structures and enums

### Test Files

- `tests/test_test_generation.py` - Tests for the new test generation feature
- `tests/test_types.py` - Tests for data type definitions
- `tests/test_cli.py` - Tests for CLI functionality
- `tests/test_analyzer.py` - Tests for core analyzer functionality

## Usage

### Basic Usage

```bash
# Basic analysis - user stories only
github-repo-analyzer analyze "owner/repo-name"

# Comprehensive analysis with architecture diagrams and API mapping
github-repo-analyzer analyze "owner/repo-name" --comprehensive

# Architecture-focused analysis (no user stories, just technical analysis)
github-repo-analyzer architecture "owner/repo-name"

# Generate comprehensive test cases and documentation from user stories
github-repo-analyzer tests "owner/repo-name"

# Analyze with custom output format
github-repo-analyzer analyze "owner/repo-name" --format json

# Analyze private repository (requires GitHub token)
github-repo-analyzer analyze "owner/repo-name" --token "your-github-token"
```

### Advanced Options

```bash
# Generate comprehensive analysis with specific focus
github-repo-analyzer analyze \
  "owner/repo-name" \
  --comprehensive \
  --focus "scalability" \
  --max-stories 8 \
  --output-file "comprehensive-analysis.md"

# Architecture analysis with focus on specific area
github-repo-analyzer architecture \
  "owner/repo-name" \
  --focus "microservices" \
  --output-file "architecture-report.md"

# Full comprehensive analysis with all features
github-repo-analyzer analyze \
  "owner/repo-name" \
  --comprehensive \
  --include-architecture \
  --include-api-analysis \
  --format markdown \
  --output-file "full-analysis.md"

# Generate tests with specific focus and test types
github-repo-analyzer tests \
  "owner/repo-name" \
  --focus "user-authentication" \
  --max-tests 8 \
  --include-unit \
  --include-integration \
  --include-e2e \
  --include-api \
  --format markdown \
  --output-file "comprehensive-tests.md"
```

### Command Options

#### `analyze` Command
- `repo`: GitHub repository in format "owner/repo-name" (required)
- `--token`: GitHub personal access token for private repositories
- `--comprehensive`: Enable comprehensive analysis with architecture diagrams and technical deep dive
- `--include-architecture`: Include system architecture diagrams (default: true with --comprehensive)
- `--include-api-analysis`: Include API endpoint analysis (default: true with --comprehensive)
- `--focus`: Specific focus area (e.g., "security", "performance", "microservices")
- `--max-stories`: Maximum number of user stories to generate (default: 5)
- `--format`: Output format: text, json, markdown (default: text)
- `--output-file`: Save output to file instead of printing to terminal
- `--system-prompt`: Custom system prompt for Claude

#### `architecture` Command
- `repo`: GitHub repository in format "owner/repo-name" (required)
- `--token`: GitHub personal access token for private repositories
- `--focus`: Focus area for architecture analysis
- `--output-file`: Save architecture diagrams to file (default: auto-generated)

#### `tests` Command
- `repo`: GitHub repository in format "owner/repo-name" (required)
- `--token`: GitHub personal access token for private repositories
- `--focus`: Focus area for test generation (e.g., "security", "performance")
- `--max-tests`: Maximum number of tests per user story (default: 5)
- `--include-unit`: Include unit tests (default: true)
- `--include-integration`: Include integration tests (default: true)
- `--include-e2e`: Include end-to-end tests (default: true)
- `--include-api`: Include API tests (default: true)
- `--format`: Output format: text, json, markdown (default: markdown)
- `--output-file`: Save test documentation to file (default: auto-generated)

#### General Options
- `--verbose`: Enable verbose logging

## Examples

### Example 1: Basic Analysis

```bash
github-repo-analyzer analyze "facebook/react"
```

This will analyze the React repository and generate user stories focused on the core functionality.

### Example 2: Focused Analysis

```bash
github-repo-analyzer analyze \
  "microsoft/vscode" \
  --focus "developer-productivity" \
  --max-stories 8
```

This will analyze VS Code with a focus on developer productivity features.

### Example 3: Comprehensive Analysis

```bash
github-repo-analyzer analyze \
  "excalidraw/excalidraw" \
  --comprehensive \
  --format markdown \
  --output-file "excalidraw-full-analysis.md"
```

This generates a comprehensive analysis with system architecture diagrams, API mappings, and user stories.

### Example 4: Architecture-Only Analysis

```bash
github-repo-analyzer architecture \
  "facebook/react" \
  --focus "component-architecture"
```

This focuses purely on system architecture and technical analysis without user stories.

### Example 5: Test Enhanced Architecture Analysis

Test the comprehensive architecture analysis with Excalidraw:

```bash
github-repo-analyzer architecture \
  "excalidraw/excalidraw" \
  --output-file "excalidraw-comprehensive-architecture.md"
```

This will generate a comprehensive technical analysis including:
- **🏗️ System Architecture Diagrams**: Mermaid diagrams showing overall system, API flows, component relationships, and data flows
- **🌐 API & Integration Analysis**: Detailed API endpoints, external services, authentication methods, and WebSocket events
- **🔧 Technical Deep Dive**: Technology stack breakdown, build system details, performance optimizations, and security features
- **📋 Full Technical Report**: Professional markdown documentation ready for teams and stakeholders

### Example 6: Comprehensive Test Generation

Generate comprehensive test cases and documentation from user stories:

```bash
github-repo-analyzer tests \
  "excalidraw/excalidraw" \
  --focus "collaboration-features" \
  --max-tests 8 \
  --include-unit \
  --include-integration \
  --include-e2e \
  --include-api \
  --format markdown \
  --output-file "excalidraw-comprehensive-tests.md"
```

This will generate comprehensive test documentation including:
- **🧪 Test Cases**: Detailed test cases covering all user story acceptance criteria
- **📋 Test Suites**: Organized test suites by test type (unit, integration, e2e, API)
- **📊 Test Coverage**: Coverage analysis by test type and priority
- **📋 Testing Strategy**: Comprehensive testing approach and methodology
- **🔧 Environment Requirements**: Test environment setup and dependencies
- **▶️ Execution Instructions**: Step-by-step test execution guidance
- **🔧 Maintenance Notes**: Test maintenance and update guidelines

## Output Formats

### Text Format (Default)
```
📋 User Stories for django/django

🎯 Story 1: User Authentication
As a developer, I want to implement secure user authentication
So that I can protect my web application from unauthorized access

Acceptance Criteria:
- Users can register with email and password
- Users can log in securely
- Password reset functionality is available
- Session management is secure

Priority: High
Effort: Medium
```

### JSON Format
```json
{
  "repository": "django/django",
  "analysis_date": "2024-01-15T10:30:00Z",
  "user_stories": [
    {
      "id": 1,
      "title": "User Authentication",
      "description": "As a developer, I want to implement secure user authentication...",
      "acceptance_criteria": [...],
      "priority": "High",
      "effort": "Medium"
    }
  ]
}
```

### Markdown Format
```markdown
# User Stories for django/django

## Story 1: User Authentication

**As a** developer  
**I want to** implement secure user authentication  
**So that** I can protect my web application from unauthorized access

### Acceptance Criteria
- Users can register with email and password
- Users can log in securely
- Password reset functionality is available
- Session management is secure

**Priority:** High  
**Effort:** Medium
```

### Test Documentation Format
```markdown
# 🧪 Test Documentation for django/django

## 📊 Test Summary
- **Total Test Cases:** 15
- **Total Test Suites:** 4

## 📈 Test Coverage by Type
- **Unit:** 40.0%
- **Integration:** 33.3%
- **E2e:** 26.7%

## 🧪 Test Suites

### 📋 Suite 1: Unit Tests for User Authentication
**Description:** Test suite covering unit testing for user story: User Authentication
**Test Type:** Unit
**Total Tests:** 6
**User Stories:** 1

#### Test Cases
**1. Test User Registration with Valid Data**
*Test covering the main functionality of user registration*
- **Type:** Unit
- **Priority:** High
- **User Story:** User Authentication

**Test Steps:**
1. Set up test environment
2. Execute main functionality
3. Verify results

**Expected Results:**
- Environment is ready
- Functionality executes successfully
- Results match expectations
```

## Configuration

### Environment Variables

You can set these environment variables for convenience:

```bash
export GITHUB_TOKEN="your-github-token"
export CLAUDE_SYSTEM_PROMPT="Your custom system prompt"
```

### Configuration File

Create a `.github-analyzer-config.yaml` file in your home directory:

```yaml
github:
  token: "your-github-token"
  default_focus: "user-experience"
  
claude:
  system_prompt: "You are an expert product analyst..."
  max_stories: 5
  
output:
  default_format: "markdown"
  include_metadata: true
```

## How It Works

1. **Repository Fetching**: Downloads repository metadata, README, and key files
2. **Code Analysis**: Analyzes project structure, dependencies, and code patterns
3. **Context Gathering**: Researches project purpose and user needs from the web
4. **AI Generation**: Uses Claude Code SDK to generate user stories
5. **Test Generation**: Creates comprehensive test cases based on user stories and acceptance criteria
6. **Output Formatting**: Formats results according to user preferences

### Test Generation Process

1. **User Story Analysis**: Analyzes user stories and acceptance criteria to identify testable scenarios
2. **Test Type Mapping**: Maps user story requirements to appropriate test types (unit, integration, e2e, API)
3. **Test Case Creation**: Generates detailed test cases with steps, expected results, and prerequisites
4. **Test Suite Organization**: Groups related test cases into logical test suites
5. **Coverage Analysis**: Calculates test coverage by type and priority
6. **Documentation Generation**: Creates comprehensive testing strategy, environment requirements, and execution instructions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Troubleshooting

### Common Issues

**"Claude Code not found"**
- Install Claude Code: `npm install -g @anthropic-ai/claude-code`
- Ensure it's in your PATH

**"GitHub API rate limit exceeded"**
- Use a GitHub token for higher rate limits
- Wait for rate limit reset

**"Repository not found"**
- Check repository name format: "owner/repo-name"
- Ensure you have access to the repository
- Verify GitHub token permissions

### Getting Help

- Check the [issues page](https://github.com/yourusername/github-repo-analyzer/issues)
- Create a new issue with detailed error information
- Include your command and error output

## Roadmap

- [x] Test generation from user stories
- [x] Comprehensive test documentation
- [ ] Support for GitLab and Bitbucket repositories
- [ ] Integration with project management tools (Jira, Trello)
- [ ] Batch analysis of multiple repositories
- [ ] Custom user story templates
- [ ] Custom test case templates
- [ ] Historical analysis and trend detection
- [ ] Team collaboration features
- [ ] Test execution automation
- [ ] Test result reporting and analytics
