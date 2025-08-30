"""
Web research module for gathering additional context about repositories and technologies.
"""

import re
import time
import requests
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus, urlparse
from dataclasses import dataclass

from .types import WebSearchResult


@dataclass
class SearchQuery:
    """A search query for web research."""
    query: str
    context: str
    priority: int = 1


class WebResearcher:
    """Module for conducting web research to gather additional context."""
    
    def __init__(self, max_results: int = 5, delay: float = 1.0):
        self.max_results = max_results
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def research_repository_context(self, repo_name: str, description: str, topics: List[str], language: Optional[str]) -> List[WebSearchResult]:
        """Research additional context about a repository."""
        search_queries = self._generate_search_queries(repo_name, description, topics, language)
        results = []
        
        for query in search_queries:
            try:
                search_results = self._search_web(query.query)
                for result in search_results[:self.max_results]:
                    result.context = query.context
                    results.append(result)
                
                # Respect rate limits
                time.sleep(self.delay)
                
            except Exception as e:
                # Continue with other queries if one fails
                continue
        
        # Sort by relevance and remove duplicates
        return self._deduplicate_and_sort_results(results)
    
    def research_technology_context(self, technology: str, context: str = "software development") -> List[WebSearchResult]:
        """Research information about a specific technology."""
        query = f"{technology} {context} features benefits use cases"
        try:
            results = self._search_web(query)
            return results[:self.max_results]
        except Exception:
            return []
    
    def research_user_needs(self, domain: str, target_audience: str) -> List[WebSearchResult]:
        """Research user needs and pain points in a specific domain."""
        query = f"{domain} {target_audience} user needs pain points requirements"
        try:
            results = self._search_web(query)
            return results[:self.max_results]
        except Exception:
            return []
    
    def _generate_search_queries(self, repo_name: str, description: str, topics: List[str], language: Optional[str]) -> List[SearchQuery]:
        """Generate search queries for web research."""
        queries = []
        
        # Repository-specific queries
        if description:
            queries.append(SearchQuery(
                query=f'"{repo_name}" {description}',
                context="repository_purpose",
                priority=1
            ))
        
        # Technology stack queries
        if language:
            queries.append(SearchQuery(
                query=f'{language} framework features benefits',
                context="technology_stack",
                priority=2
            ))
        
        # Domain-specific queries
        for topic in topics[:3]:  # Limit to top 3 topics
            queries.append(SearchQuery(
                query=f'{topic} software development use cases',
                context="domain_knowledge",
                priority=3
            ))
        
        # General project queries
        queries.append(SearchQuery(
            query=f'{repo_name} project analysis review',
            context="project_analysis",
            priority=4
        ))
        
        # Sort by priority
        queries.sort(key=lambda x: x.priority)
        return queries
    
    def _search_web(self, query: str) -> List[WebSearchResult]:
        """Perform web search using DuckDuckGo (no API key required)."""
        try:
            # Use DuckDuckGo search
            search_url = "https://html.duckduckgo.com/html/"
            params = {
                "q": query,
                "kl": "us-en"
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse HTML results (simplified parsing)
            results = self._parse_duckduckgo_results(response.text)
            return results
            
        except Exception:
            # Fallback to a different search method or return empty results
            return []
    
    def _parse_duckduckgo_results(self, html_content: str) -> List[WebSearchResult]:
        """Parse DuckDuckGo search results from HTML."""
        results = []
        
        try:
            # Simple regex-based parsing (in production, use BeautifulSoup)
            # Look for result links and snippets
            link_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
            snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]*)</a>'
            
            links = re.findall(link_pattern, html_content)
            snippets = re.findall(snippet_pattern, html_content)
            
            for i, (url, title) in enumerate(links[:self.max_results]):
                snippet = snippets[i] if i < len(snippets) else ""
                
                # Clean up the URL (DuckDuckGo redirects)
                clean_url = self._clean_duckduckgo_url(url)
                
                # Calculate simple relevance score
                relevance_score = self._calculate_relevance_score(title, snippet)
                
                results.append(WebSearchResult(
                    title=title.strip(),
                    url=clean_url,
                    snippet=snippet.strip(),
                    relevance_score=relevance_score
                ))
                
        except Exception:
            pass
        
        return results
    
    def _clean_duckduckgo_url(self, url: str) -> str:
        """Clean DuckDuckGo redirect URLs."""
        if url.startswith("/l/?uddg="):
            # Extract the actual URL from DuckDuckGo redirect
            try:
                import urllib.parse
                decoded = urllib.parse.unquote(url.split("uddg=")[1])
                return decoded
            except:
                return url
        return url
    
    def _calculate_relevance_score(self, title: str, snippet: str) -> float:
        """Calculate a simple relevance score for search results."""
        score = 0.0
        
        # Title relevance
        title_lower = title.lower()
        if any(word in title_lower for word in ["software", "development", "tool", "framework", "library"]):
            score += 0.3
        
        # Snippet relevance
        snippet_lower = snippet.lower()
        if any(word in snippet_lower for word in ["features", "benefits", "use cases", "examples"]):
            score += 0.2
        
        # Length bonus
        if len(title) > 20 and len(snippet) > 50:
            score += 0.1
        
        # Normalize to 0-1 range
        return min(score, 1.0)
    
    def _deduplicate_and_sort_results(self, results: List[WebSearchResult]) -> List[WebSearchResult]:
        """Remove duplicate results and sort by relevance."""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        # Sort by relevance score (descending)
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_results[:self.max_results]
    
    def get_technology_overview(self, technology: str) -> Dict[str, Any]:
        """Get a comprehensive overview of a technology."""
        try:
            # Search for technology overview
            overview_query = f"{technology} overview introduction features"
            results = self._search_web(overview_query)
            
            # Extract key information
            overview = {
                "name": technology,
                "description": "",
                "key_features": [],
                "use_cases": [],
                "resources": []
            }
            
            for result in results[:3]:
                if "overview" in result.title.lower() or "introduction" in result.title.lower():
                    overview["description"] = result.snippet
                    break
            
            # Search for features
            features_query = f"{technology} features capabilities"
            feature_results = self._search_web(features_query)
            for result in feature_results[:2]:
                overview["key_features"].append(result.snippet[:100] + "...")
            
            # Search for use cases
            use_cases_query = f"{technology} use cases examples applications"
            use_case_results = self._search_web(use_cases_query)
            for result in use_case_results[:2]:
                overview["use_cases"].append(result.snippet[:100] + "...")
            
            return overview
            
        except Exception:
            return {"name": technology, "description": "Information not available"}
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
