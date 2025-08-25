"""
GitHub API client for fetching repository information.
"""

import os
import re
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from .types import RepositoryInfo, GitHubConfig
from .exceptions import GitHubAPIError, RepositoryNotFoundError


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.session = requests.Session()
        
        if config.token:
            self.session.headers.update({
                "Authorization": f"token {config.token}",
                "Accept": "application/vnd.github.v3+json"
            })
        else:
            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json"
            })
    
    def get_repository_info(self, owner: str, repo: str) -> RepositoryInfo:
        """Fetch repository information from GitHub API."""
        try:
            # Get basic repository info
            repo_url = f"{self.config.base_url}/repos/{owner}/{repo}"
            response = self.session.get(repo_url, timeout=self.config.timeout)
            
            if response.status_code == 404:
                raise RepositoryNotFoundError(f"Repository {owner}/{repo} not found")
            elif response.status_code != 200:
                raise GitHubAPIError(f"GitHub API error: {response.status_code} - {response.text}")
            
            repo_data = response.json()
            
            # Get README content
            readme_content = self._get_readme_content(owner, repo)
            
            # Get topics
            topics = self._get_repository_topics(owner, repo)
            
            # Parse dates
            created_at = datetime.fromisoformat(repo_data["created_at"].replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(repo_data["updated_at"].replace("Z", "+00:00"))
            
            return RepositoryInfo(
                owner=owner,
                name=repo,
                full_name=repo_data["full_name"],
                description=repo_data.get("description"),
                language=repo_data.get("language"),
                stars=repo_data.get("stargazers_count", 0),
                forks=repo_data.get("forks_count", 0),
                topics=topics,
                readme_content=readme_content,
                license=repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                created_at=created_at,
                updated_at=updated_at,
                size=repo_data.get("size", 0),
                default_branch=repo_data.get("default_branch", "main")
            )
            
        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error: {e}")
        except Exception as e:
            raise GitHubAPIError(f"Unexpected error: {e}")
    
    def _get_readme_content(self, owner: str, repo: str) -> Optional[str]:
        """Fetch README content from repository."""
        try:
            readme_url = f"{self.config.base_url}/repos/{owner}/{repo}/readme"
            response = self.session.get(readme_url, timeout=self.config.timeout)
            
            if response.status_code == 200:
                readme_data = response.json()
                # Decode base64 content
                import base64
                content = base64.b64decode(readme_data["content"]).decode("utf-8")
                return content
            return None
            
        except Exception:
            return None
    
    def _get_repository_topics(self, owner: str, repo: str) -> List[str]:
        """Fetch repository topics."""
        try:
            topics_url = f"{self.config.base_url}/repos/{owner}/{repo}/topics"
            response = self.session.get(topics_url, timeout=self.config.timeout)
            
            if response.status_code == 200:
                topics_data = response.json()
                return topics_data.get("names", [])
            return []
            
        except Exception:
            return []
    
    def get_repository_files(self, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        """Get list of files in a repository directory."""
        try:
            files_url = f"{self.config.base_url}/repos/{owner}/{repo}/contents/{path}"
            response = self.session.get(files_url, timeout=self.config.timeout)
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception:
            return []
    
    def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get content of a specific file."""
        try:
            file_url = f"{self.config.base_url}/repos/{owner}/{repo}/contents/{path}"
            response = self.session.get(file_url, timeout=self.config.timeout)
            
            if response.status_code == 200:
                file_data = response.json()
                import base64
                content = base64.b64decode(file_data["content"]).decode("utf-8")
                return content
            return None
            
        except Exception:
            return None
    
    def get_repository_stats(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get additional repository statistics."""
        try:
            stats = {}
            
            # Get contributors
            contributors_url = f"{self.config.base_url}/repos/{owner}/{repo}/contributors"
            response = self.session.get(contributors_url, timeout=self.config.timeout)
            if response.status_code == 200:
                stats["contributors_count"] = len(response.json())
            
            # Get commits count (approximate)
            commits_url = f"{self.config.base_url}/repos/{owner}/{repo}/commits"
            response = self.session.get(commits_url, timeout=self.config.timeout)
            if response.status_code == 200:
                # GitHub doesn't provide total count, but we can estimate from headers
                link_header = response.headers.get("Link", "")
                if "rel=\"last\"" in link_header:
                    match = re.search(r'page=(\d+)>; rel="last"', link_header)
                    if match:
                        stats["estimated_commits"] = int(match.group(1)) * 30  # 30 per page
            
            # Get releases
            releases_url = f"{self.config.base_url}/repos/{owner}/{repo}/releases"
            response = self.session.get(releases_url, timeout=self.config.timeout)
            if response.status_code == 200:
                stats["releases_count"] = len(response.json())
            
            return stats
            
        except Exception:
            return {}
    
    def search_repositories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for repositories using GitHub search API."""
        try:
            search_url = f"{self.config.base_url}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": min(limit, 100)  # GitHub max is 100
            }
            
            response = self.session.get(search_url, params=params, timeout=self.config.timeout)
            
            if response.status_code == 200:
                search_data = response.json()
                return search_data.get("items", [])
            return []
            
        except Exception:
            return []
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit information."""
        try:
            rate_limit_url = f"{self.config.base_url}/rate_limit"
            response = self.session.get(rate_limit_url, timeout=self.config.timeout)
            
            if response.status_code == 200:
                return response.json()
            return {}
            
        except Exception:
            return {}
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
