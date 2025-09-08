# GitHub Repository Analyzer UI

A modern Next.js web interface for the GitHub Repository Analyzer tool. This UI demonstrates the capabilities of the analyzer with interactive terminal simulation and comprehensive report viewing.

## Features

- 🎯 **Repository Selection**: Choose from popular test repositories
- 🖥️ **Terminal Simulation**: Real-time command execution simulation
- 📊 **Interactive Reports**: Comprehensive analysis reports with Mermaid diagrams
- 🏗️ **Architecture Visualization**: System architecture, API flows, and data flow diagrams
- 📝 **User Story Generation**: AI-generated user stories with acceptance criteria
- 🔧 **Technical Deep Dive**: Technology stack analysis and performance insights
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Test Repositories

The UI includes sample data for these popular repositories:

- **Saleor** - Headless e-commerce platform (Python/GraphQL)
- **Ghost** - Publishing platform (JavaScript/Node.js)
- **Mastodon** - Social media platform (Ruby/Rails)
- **Monica** - Personal CRM (PHP/Laravel)

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Python 3.10+ (for the GitHub Repository Analyzer tool)
- GitHub Repository Analyzer installed and working

### Installation

1. **First, install the GitHub Repository Analyzer tool:**
   ```bash
   # Navigate to the project root
   cd ..
   
   # Install the Python tool
   pip install -e .
   ```

2. **Set up the UI:**
   ```bash
   # Navigate to the UI directory
   cd nextjs-ui
   
   # Install dependencies
   npm install
   ```

3. **Configure environment (optional):**
   ```bash
   # Copy the example environment file
   cp env.example .env.local
   
   # Edit .env.local and add your GitHub token
   GITHUB_TOKEN=your_github_token_here
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. **Open [http://localhost:3000](http://localhost:3000) in your browser**

### Real Analysis Setup

The UI now supports **real analysis** using the actual GitHub Repository Analyzer tool. To use this:

1. **Ensure the Python tool is installed and accessible**
2. **Set up a GitHub token** (optional but recommended for higher rate limits)
3. **Select a repository and click "Run Real Analysis"**

The UI will:
- Execute the actual `github-repo-analyzer` command
- Show real terminal output
- Display actual analysis results
- Render real Mermaid diagrams from the analysis

## Usage

1. **Select a Repository**: Choose from the test repositories in the left panel
2. **Choose Analysis Type**: Select from Basic, Comprehensive, Architecture, or Tests
3. **Run Analysis**: Click "Run Analysis" to simulate the terminal output
4. **View Results**: Explore the comprehensive report with interactive diagrams

## Components

### RepositorySelector
- Displays available test repositories
- Search and filter functionality
- Repository metadata display

### TerminalOutput
- Simulates command execution
- Real-time output streaming
- Progress indicators

### ReportViewer
- Tabbed interface for different report sections
- Interactive Mermaid diagram rendering
- Copy-to-clipboard functionality

### MermaidDiagram
- Renders Mermaid diagrams
- Fallback to code view
- External viewer integration

## Technologies Used

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Mermaid** - Diagram generation
- **Lucide React** - Icon library
- **React Hot Toast** - Notifications

## Architecture

The UI is built with a component-based architecture:

```
components/
├── RepositorySelector.tsx    # Repository selection interface
├── TerminalOutput.tsx        # Terminal simulation component
├── ReportViewer.tsx          # Main report display
└── MermaidDiagram.tsx        # Diagram rendering component

types/
└── index.ts                  # TypeScript type definitions

app/
├── layout.tsx                # Root layout
├── page.tsx                  # Main page component
└── globals.css               # Global styles
```

## Customization

### Adding New Repositories

Edit the `testRepositories` array in `app/page.tsx`:

```typescript
const testRepositories: Repository[] = [
  {
    id: 'new-repo',
    name: 'owner/repo-name',
    description: 'Repository description',
    language: 'JavaScript',
    stars: 1000,
    forks: 100,
    topics: ['javascript', 'react'],
    license: 'MIT',
    size: 50000,
    url: 'https://github.com/owner/repo-name'
  }
]
```

### Modifying Analysis Simulation

Update the `simulateAnalysis` function in `app/page.tsx` to customize the terminal output and analysis results.

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Deploy automatically

### Other Platforms

Build the application:

```bash
npm run build
npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
