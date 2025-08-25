"""
Custom exceptions for the GitHub Repository Analyzer.
"""


class GitHubRepoAnalyzerError(Exception):
    """Base exception for all GitHub Repository Analyzer errors."""
    pass


class GitHubAPIError(GitHubRepoAnalyzerError):
    """Raised when there's an error with the GitHub API."""
    pass


class RepositoryNotFoundError(GitHubRepoAnalyzerError):
    """Raised when a repository is not found."""
    pass


class ClaudeAnalysisError(GitHubRepoAnalyzerError):
    """Raised when there's an error with Claude analysis."""
    pass


class WebResearchError(GitHubRepoAnalyzerError):
    """Raised when there's an error with web research."""
    pass


class ConfigurationError(GitHubRepoAnalyzerError):
    """Raised when there's a configuration error."""
    pass


class OutputFormatError(GitHubRepoAnalyzerError):
    """Raised when there's an error with output formatting."""
    pass


class ValidationError(GitHubRepoAnalyzerError):
    """Raised when input validation fails."""
    pass


class RateLimitError(GitHubRepoAnalyzerError):
    """Raised when API rate limits are exceeded."""
    pass


class NetworkError(GitHubRepoAnalyzerError):
    """Raised when there's a network connectivity issue."""
    pass


class FileOperationError(GitHubRepoAnalyzerError):
    """Raised when there's an error with file operations."""
    pass
