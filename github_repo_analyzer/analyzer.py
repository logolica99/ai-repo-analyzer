"""
Main analyzer module that orchestrates the repository analysis process.
"""

import asyncio
from typing import Optional
from pathlib import Path

from .types import (
    AnalyzerConfig, RepositoryInfo, AnalysisResult, OutputFormat,
    GitHubConfig, ClaudeConfig
)
from .github_client import GitHubClient
from .web_researcher import WebResearcher
from .claude_analyzer import ClaudeAnalyzer
from .output_formatter import OutputFormatter
from .exceptions import (
    GitHubRepoAnalyzerError, RepositoryNotFoundError, ClaudeAnalysisError,
    WebResearchError, ConfigurationError
)


class GitHubRepoAnalyzer:
    """Main analyzer class that orchestrates the repository analysis process."""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
        self.github_client = GitHubClient(config.github)
        self.web_researcher = WebResearcher()
        self.claude_analyzer = ClaudeAnalyzer(config.claude)
        self.output_formatter = OutputFormatter(config.output_format)
    
    async def analyze_repository(self, repo_owner: str, repo_name: str) -> AnalysisResult:
        """Analyze a GitHub repository and generate user stories."""
        
        try:
            # Step 1: Fetch repository information
            repo_info = await self._fetch_repository_info(repo_owner, repo_name)
            
            # Step 2: Conduct web research for additional context
            web_results = await self._conduct_web_research(repo_info)
            
            # Step 3: Analyze with Claude and generate user stories
            analysis_result = await self._analyze_with_claude(repo_info, web_results)
            
            # Step 4: Save output if specified
            if self.config.output_file:
                await self._save_output(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            raise GitHubRepoAnalyzerError(f"Analysis failed: {e}")
    
    async def _fetch_repository_info(self, repo_owner: str, repo_name: str) -> RepositoryInfo:
        """Fetch repository information from GitHub."""
        try:
            repo_info = self.github_client.get_repository_info(repo_owner, repo_name)
            return repo_info
        except RepositoryNotFoundError:
            raise
        except Exception as e:
            raise GitHubRepoAnalyzerError(f"Failed to fetch repository info: {e}")
    
    async def _conduct_web_research(self, repo_info: RepositoryInfo) -> list:
        """Conduct web research for additional context."""
        try:
            web_results = self.web_researcher.research_repository_context(
                repo_name=repo_info.name,
                description=repo_info.description or "",
                topics=repo_info.topics,
                language=repo_info.language
            )
            return web_results
        except Exception as e:
            # Web research is not critical, so we log the error but continue
            if self.config.verbose:
                print(f"Warning: Web research failed: {e}")
            return []
    
    async def _analyze_with_claude(
        self,
        repo_info: RepositoryInfo,
        web_results: list
    ) -> AnalysisResult:
        """Analyze the repository with Claude and generate user stories."""
        try:
            analysis_result = await self.claude_analyzer.analyze_repository(
                repo_info=repo_info,
                web_results=web_results,
                focus_area=self.config.focus_area,
                max_stories=self.config.max_stories
            )
            return analysis_result
        except Exception as e:
            raise ClaudeAnalysisError(f"Claude analysis failed: {e}")
    
    async def _save_output(self, analysis_result: AnalysisResult) -> None:
        """Save the analysis result to the specified output file."""
        try:
            self.output_formatter.save_to_file(analysis_result, self.config.output_file)
        except Exception as e:
            raise GitHubRepoAnalyzerError(f"Failed to save output: {e}")
    
    def get_output_content(self, analysis_result: AnalysisResult) -> str:
        """Get the formatted output content without saving to file."""
        return self.output_formatter.format_analysis_result(analysis_result)
    
    def close(self):
        """Close all resources."""
        self.github_client.close()
        self.web_researcher.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AnalyzerFactory:
    """Factory class for creating analyzer instances with different configurations."""
    
    @staticmethod
    def create_from_env() -> AnalyzerConfig:
        """Create configuration from environment variables."""
        import os
        
        config = AnalyzerConfig()
        
        # GitHub configuration
        if os.getenv("GITHUB_TOKEN"):
            config.github.token = os.getenv("GITHUB_TOKEN")
        
        # Claude configuration
        if os.getenv("CLAUDE_SYSTEM_PROMPT"):
            config.claude.system_prompt = os.getenv("CLAUDE_SYSTEM_PROMPT")
        
        # Output configuration
        if os.getenv("OUTPUT_FORMAT"):
            try:
                config.output_format = OutputFormat(os.getenv("OUTPUT_FORMAT").lower())
            except ValueError:
                pass
        
        return config
    
    @staticmethod
    def create_from_file(config_path: Path) -> AnalyzerConfig:
        """Create configuration from a YAML file."""
        try:
            import yaml
            
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            config = AnalyzerConfig()
            
            # Parse GitHub config
            if "github" in config_data:
                github_data = config_data["github"]
                if "token" in github_data:
                    config.github.token = github_data["token"]
                if "base_url" in github_data:
                    config.github.base_url = github_data["base_url"]
                if "timeout" in github_data:
                    config.github.timeout = github_data["timeout"]
            
            # Parse Claude config
            if "claude" in config_data:
                claude_data = config_data["claude"]
                if "system_prompt" in claude_data:
                    config.claude.system_prompt = claude_data["system_prompt"]
                if "max_turns" in claude_data:
                    config.claude.max_turns = claude_data["max_turns"]
                if "allowed_tools" in claude_data:
                    config.claude.allowed_tools = claude_data["allowed_tools"]
                if "permission_mode" in claude_data:
                    config.claude.permission_mode = claude_data["permission_mode"]
            
            # Parse analyzer config
            if "max_stories" in config_data:
                config.max_stories = config_data["max_stories"]
            if "focus_area" in config_data:
                config.focus_area = config_data["focus_area"]
            if "output_format" in config_data:
                try:
                    config.output_format = OutputFormat(config_data["output_format"].lower())
                except ValueError:
                    pass
            if "include_metadata" in config_data:
                config.include_metadata = config_data["include_metadata"]
            
            return config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {config_path}: {e}")
    
    @staticmethod
    def create_default() -> AnalyzerConfig:
        """Create a default configuration."""
        return AnalyzerConfig()


async def analyze_repository_simple(
    repo_owner: str,
    repo_name: str,
    github_token: Optional[str] = None,
    focus_area: Optional[str] = None,
    max_stories: int = 5,
    output_format: OutputFormat = OutputFormat.TEXT
) -> AnalysisResult:
    """Simple function to analyze a repository with minimal configuration."""
    
    # Create basic configuration
    config = AnalyzerConfig()
    config.github.token = github_token
    config.focus_area = focus_area
    config.max_stories = max_stories
    config.output_format = output_format
    
    # Create and run analyzer
    async with GitHubRepoAnalyzer(config) as analyzer:
        return await analyzer.analyze_repository(repo_owner, repo_name)
