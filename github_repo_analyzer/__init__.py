"""
GitHub Repository Analyzer

A CLI tool that analyzes GitHub repositories and generates user stories using Claude Code SDK.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .analyzer import GitHubRepoAnalyzer
from .cli import main

__all__ = ["GitHubRepoAnalyzer", "main"]
