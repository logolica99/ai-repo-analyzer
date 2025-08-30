"""
Type definitions for the GitHub Repository Analyzer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pathlib import Path


class OutputFormat(Enum):
    """Output format options for user stories."""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"


class StoryPriority(Enum):
    """Priority levels for user stories."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class StoryEffort(Enum):
    """Effort estimation for user stories."""
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    EXTRA_LARGE = "Extra Large"


@dataclass
class AcceptanceCriterion:
    """A single acceptance criterion for a user story."""
    description: str
    completed: bool = False


@dataclass
class UserStory:
    """A user story generated from repository analysis."""
    id: int
    title: str
    description: str
    acceptance_criteria: List[AcceptanceCriterion]
    priority: StoryPriority
    effort: StoryEffort
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RepositoryInfo:
    """Information about a GitHub repository."""
    owner: str
    name: str
    full_name: str
    description: Optional[str]
    language: Optional[str]
    stars: int
    forks: int
    topics: List[str]
    readme_content: Optional[str]
    license: Optional[str]
    created_at: datetime
    updated_at: datetime
    size: int
    default_branch: str


@dataclass
class GitHubConfig:
    """GitHub API configuration."""
    token: Optional[str] = None
    base_url: str = "https://api.github.com"
    timeout: int = 30


@dataclass
class ClaudeConfig:
    """Claude Code SDK configuration."""
    system_prompt: str = "You are an expert product analyst and software engineer. Your task is to analyze GitHub repositories and generate comprehensive, actionable user stories that would be valuable for development teams."
    max_turns: int = 3
    allowed_tools: List[str] = field(default_factory=lambda: ["Read", "Write", "Bash"])
    permission_mode: str = "acceptEdits"


@dataclass
class AnalyzerConfig:
    """Configuration for the repository analyzer."""
    github: GitHubConfig = field(default_factory=GitHubConfig)
    claude: ClaudeConfig = field(default_factory=ClaudeConfig)
    max_stories: int = 5
    focus_area: Optional[str] = None
    output_format: OutputFormat = OutputFormat.TEXT
    output_file: Optional[Path] = None
    verbose: bool = False
    include_metadata: bool = True


@dataclass
class WebSearchResult:
    """Result from web search for additional context."""
    title: str
    url: str
    snippet: str
    relevance_score: float


@dataclass
class SystemArchitecture:
    """System architecture analysis with Mermaid diagrams."""
    system_diagram: str  # Mermaid diagram code
    api_flow_diagram: str  # API flow Mermaid diagram
    data_flow_diagram: str  # Data flow Mermaid diagram
    component_diagram: str  # Component architecture diagram
    deployment_diagram: Optional[str] = None  # Deployment architecture


@dataclass
class APIAnalysis:
    """API endpoint and integration analysis."""
    endpoints: List[Dict[str, Any]]
    external_services: List[str]
    authentication_methods: List[str]
    data_formats: List[str]
    websocket_events: List[str] = field(default_factory=list)
    database_schemas: List[str] = field(default_factory=list)


@dataclass
class TechnicalDeepDive:
    """Comprehensive technical analysis."""
    technology_stack: Dict[str, List[str]]  # Categorized by frontend, backend, etc.
    build_system: Dict[str, Any]
    testing_framework: Dict[str, Any]
    ci_cd_pipeline: Dict[str, Any]
    deployment_strategy: Dict[str, Any]
    performance_optimizations: List[str]
    security_features: List[str]


@dataclass
class CodeAnalysis:
    """Analysis of repository code structure."""
    main_languages: List[str]
    framework: Optional[str]
    dependencies: List[str]
    architecture_patterns: List[str]
    code_complexity: str
    test_coverage: Optional[str]
    documentation_quality: str
    
    # Enhanced analysis
    system_architecture: Optional[SystemArchitecture] = None
    api_analysis: Optional[APIAnalysis] = None
    technical_deep_dive: Optional[TechnicalDeepDive] = None


@dataclass
class AnalysisResult:
    """Result of repository analysis."""
    repository: RepositoryInfo
    user_stories: List[UserStory]
    analysis_date: datetime
    focus_area: Optional[str]
    tech_stack: List[str]
    key_features: List[str]
    target_users: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Enhanced analysis results
    code_analysis: Optional[CodeAnalysis] = None
    system_architecture: Optional[SystemArchitecture] = None
    api_analysis: Optional[APIAnalysis] = None
    technical_deep_dive: Optional[TechnicalDeepDive] = None
    comprehensive_report: Optional[str] = None  # Full technical report
