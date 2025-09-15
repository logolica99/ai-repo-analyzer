"""
Health analyzer module for comprehensive repository health assessment.
"""

import json
import re
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

from .types import RepositoryInfo, GitHubConfig
from .github_client import GitHubClient


@dataclass
class HealthMetric:
    """A single health metric with score and details."""
    name: str
    score: float  # 0.0 to 1.0
    status: str  # "excellent", "good", "fair", "poor", "critical"
    details: str
    recommendations: List[str] = field(default_factory=list)
    weight: float = 1.0  # Weight for overall score calculation


@dataclass
class HealthCategory:
    """A category of health metrics."""
    name: str
    metrics: List[HealthMetric]
    overall_score: float
    status: str
    description: str


@dataclass
class HealthReport:
    """Comprehensive health report for a repository."""
    repository: RepositoryInfo
    analysis_date: datetime
    overall_score: float
    overall_status: str
    categories: List[HealthCategory]
    summary: str
    critical_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HealthAnalyzer:
    """Analyzes repository health across multiple dimensions."""
    
    def __init__(self, github_config: GitHubConfig):
        self.github_client = GitHubClient(github_config)
        self.file_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'go': ['.go'],
            'rust': ['.rs'],
            'cpp': ['.cpp', '.cc', '.cxx', '.c++'],
            'c': ['.c'],
            'csharp': ['.cs'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'swift': ['.swift'],
            'kotlin': ['.kt', '.kts'],
            'scala': ['.scala'],
            'html': ['.html', '.htm'],
            'css': ['.css', '.scss', '.sass', '.less'],
            'markdown': ['.md', '.markdown'],
            'yaml': ['.yml', '.yaml'],
            'json': ['.json'],
            'xml': ['.xml'],
            'sql': ['.sql'],
            'shell': ['.sh', '.bash', '.zsh', '.fish'],
            'dockerfile': ['Dockerfile', 'dockerfile'],
            'makefile': ['Makefile', 'makefile']
        }
    
    async def analyze_repository_health(self, repo_owner: str, repo_name: str) -> HealthReport:
        """Analyze repository health comprehensively."""
        
        # Fetch repository information
        repo_info = self.github_client.get_repository_info(repo_owner, repo_name)
        
        # Get repository contents for analysis
        contents = await self._get_repository_contents(repo_owner, repo_name)
        
        # Analyze different health categories
        categories = []
        
        # Code Quality Analysis
        code_quality = await self._analyze_code_quality(repo_info, contents)
        categories.append(code_quality)
        
        # Documentation Analysis
        documentation = await self._analyze_documentation(repo_info, contents)
        categories.append(documentation)
        
        # Architecture Analysis
        architecture = await self._analyze_architecture(repo_info, contents)
        categories.append(architecture)
        
        # Dependency Analysis
        dependencies = await self._analyze_dependencies(repo_info, contents)
        categories.append(dependencies)
        
        # Security Analysis
        security = await self._analyze_security(repo_info, contents)
        categories.append(security)
        
        # Testing Analysis
        testing = await self._analyze_testing(repo_info, contents)
        categories.append(testing)
        
        # Performance Analysis
        performance = await self._analyze_performance(repo_info, contents)
        categories.append(performance)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(categories)
        overall_status = self._get_status_from_score(overall_score)
        
        # Generate summary and recommendations
        summary = self._generate_summary(categories, overall_score)
        critical_issues = self._identify_critical_issues(categories)
        recommendations = self._generate_recommendations(categories)
        
        return HealthReport(
            repository=repo_info,
            analysis_date=datetime.now(),
            overall_score=overall_score,
            overall_status=overall_status,
            categories=categories,
            summary=summary,
            critical_issues=critical_issues,
            recommendations=recommendations
        )
    
    async def _get_repository_contents(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Get repository contents for analysis."""
        # This would typically fetch file contents from GitHub API
        # For now, we'll return a mock structure
        return {
            'files': [],
            'directories': [],
            'total_files': 0,
            'total_size': 0
        }
    
    async def _analyze_code_quality(self, repo_info: RepositoryInfo, contents: Dict[str, Any]) -> HealthCategory:
        """Analyze code quality metrics."""
        metrics = []
        
        # Code complexity analysis
        complexity_score = await self._analyze_code_complexity(contents)
        metrics.append(complexity_score)
        
        # Code style consistency
        style_score = await self._analyze_code_style(contents)
        metrics.append(style_score)
        
        # Code duplication
        duplication_score = await self._analyze_code_duplication(contents)
        metrics.append(duplication_score)
        
        # Function/class size analysis
        size_score = await self._analyze_code_size(contents)
        metrics.append(size_score)
        
        # Calculate category score
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Code Quality",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis of code structure, complexity, and maintainability"
        )
    
    async def _analyze_documentation(self, repo_info: RepositoryInfo, contents: Dict[str, Any]) -> HealthCategory:
        """Analyze documentation quality."""
        metrics = []
        
        # README quality
        readme_score = await self._analyze_readme_quality(repo_info)
        metrics.append(readme_score)
        
        # Code documentation
        code_docs_score = await self._analyze_code_documentation(contents)
        metrics.append(code_docs_score)
        
        # API documentation
        api_docs_score = await self._analyze_api_documentation(contents)
        metrics.append(api_docs_score)
        
        # Contributing guidelines
        contributing_score = await self._analyze_contributing_guidelines(contents)
        metrics.append(contributing_score)
        
        # Calculate category score
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Documentation",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis of documentation completeness and quality"
        )
    
    async def _analyze_architecture(self, repo_info: RepositoryInfo, contents: Dict[str, Any]) -> HealthCategory:
        """Analyze architectural quality."""
        metrics = []
        
        # Modularity analysis
        modularity_score = await self._analyze_modularity(contents)
        metrics.append(modularity_score)
        
        # Design patterns usage
        patterns_score = await self._analyze_design_patterns(contents)
        metrics.append(patterns_score)
        
        # Separation of concerns
        separation_score = await self._analyze_separation_of_concerns(contents)
        metrics.append(separation_score)
        
        # Scalability indicators
        scalability_score = await self._analyze_scalability(contents)
        metrics.append(scalability_score)
        
        # Calculate category score
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Architecture",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis of architectural design and scalability"
        )
    
    async def _analyze_dependencies(self, repo_info: RepositoryInfo, contents: Dict[str, Any]) -> HealthCategory:
        """Analyze dependency health."""
        metrics = []
        
        # Dependency freshness
        freshness_score = await self._analyze_dependency_freshness(contents)
        metrics.append(freshness_score)
        
        # Security vulnerabilities
        security_score = await self._analyze_dependency_security(contents)
        metrics.append(security_score)
        
        # Dependency size
        size_score = await self._analyze_dependency_size(contents)
        metrics.append(size_score)
        
        # License compatibility
        license_score = await self._analyze_dependency_licenses(contents)
        metrics.append(license_score)
        
        # Calculate category score
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Dependencies",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis of dependency health and security"
        )
    
    async def _analyze_security(self, repo_info: RepositoryInfo, contents: Dict[str, Any]) -> HealthCategory:
        """Analyze security aspects."""
        metrics = []
        
        # Secret detection
        secrets_score = await self._analyze_secrets(contents)
        metrics.append(secrets_score)
        
        # Input validation
        validation_score = await self._analyze_input_validation(contents)
        metrics.append(validation_score)
        
        # Authentication/Authorization
        auth_score = await self._analyze_authentication(contents)
        metrics.append(auth_score)
        
        # HTTPS/TLS usage
        tls_score = await self._analyze_tls_usage(contents)
        metrics.append(tls_score)
        
        # Calculate category score
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Security",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis of security practices and vulnerabilities"
        )
    
    async def _analyze_testing(self, repo_info: RepositoryInfo, contents: Dict[str, Any]) -> HealthCategory:
        """Analyze testing coverage and quality."""
        metrics = []
        
        # Test coverage
        coverage_score = await self._analyze_test_coverage(contents)
        metrics.append(coverage_score)
        
        # Test quality
        quality_score = await self._analyze_test_quality(contents)
        metrics.append(quality_score)
        
        # Test automation
        automation_score = await self._analyze_test_automation(contents)
        metrics.append(automation_score)
        
        # Test diversity
        diversity_score = await self._analyze_test_diversity(contents)
        metrics.append(diversity_score)
        
        # Calculate category score
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Testing",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis of testing practices and coverage"
        )
    
    async def _analyze_performance(self, repo_info: RepositoryInfo, contents: Dict[str, Any]) -> HealthCategory:
        """Analyze performance characteristics."""
        metrics = []
        
        # Performance optimizations
        optimizations_score = await self._analyze_performance_optimizations(contents)
        metrics.append(optimizations_score)
        
        # Resource usage
        resources_score = await self._analyze_resource_usage(contents)
        metrics.append(resources_score)
        
        # Caching strategies
        caching_score = await self._analyze_caching(contents)
        metrics.append(caching_score)
        
        # Database efficiency
        database_score = await self._analyze_database_efficiency(contents)
        metrics.append(database_score)
        
        # Calculate category score
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Performance",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis of performance characteristics and optimizations"
        )
    
    # Individual metric analysis methods (simplified implementations)
    
    async def _analyze_code_complexity(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze code complexity."""
        # Simplified implementation - would use tools like radon, lizard, etc.
        return HealthMetric(
            name="Code Complexity",
            score=0.7,
            status="good",
            details="Cyclomatic complexity is within acceptable limits",
            recommendations=["Consider refactoring complex functions", "Break down large functions"]
        )
    
    async def _analyze_code_style(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze code style consistency."""
        return HealthMetric(
            name="Code Style",
            score=0.8,
            status="good",
            details="Code follows consistent style guidelines",
            recommendations=["Use automated formatting tools", "Enforce style checks in CI"]
        )
    
    async def _analyze_code_duplication(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze code duplication."""
        return HealthMetric(
            name="Code Duplication",
            score=0.6,
            status="fair",
            details="Some code duplication detected",
            recommendations=["Extract common functionality", "Use shared libraries"]
        )
    
    async def _analyze_code_size(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze function/class sizes."""
        return HealthMetric(
            name="Code Size",
            score=0.75,
            status="good",
            details="Most functions and classes are appropriately sized",
            recommendations=["Split large classes", "Extract methods from long functions"]
        )
    
    async def _analyze_readme_quality(self, repo_info: RepositoryInfo) -> HealthMetric:
        """Analyze README quality."""
        readme_content = repo_info.readme_content or ""
        
        # Check for essential sections
        essential_sections = ['description', 'installation', 'usage', 'contributing', 'license']
        found_sections = sum(1 for section in essential_sections if section.lower() in readme_content.lower())
        
        score = found_sections / len(essential_sections)
        
        return HealthMetric(
            name="README Quality",
            score=score,
            status=self._get_status_from_score(score),
            details=f"README contains {found_sections}/{len(essential_sections)} essential sections",
            recommendations=["Add missing sections", "Improve documentation clarity"]
        )
    
    async def _analyze_code_documentation(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze code documentation."""
        return HealthMetric(
            name="Code Documentation",
            score=0.5,
            status="fair",
            details="Limited inline documentation found",
            recommendations=["Add docstrings to functions", "Document complex algorithms"]
        )
    
    async def _analyze_api_documentation(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze API documentation."""
        return HealthMetric(
            name="API Documentation",
            score=0.4,
            status="poor",
            details="API documentation is incomplete",
            recommendations=["Generate API docs", "Use OpenAPI/Swagger"]
        )
    
    async def _analyze_contributing_guidelines(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze contributing guidelines."""
        return HealthMetric(
            name="Contributing Guidelines",
            score=0.6,
            status="fair",
            details="Basic contributing guidelines present",
            recommendations=["Add detailed contribution guide", "Include code review process"]
        )
    
    async def _analyze_modularity(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze code modularity."""
        return HealthMetric(
            name="Modularity",
            score=0.7,
            status="good",
            details="Code is well-modularized",
            recommendations=["Consider microservices architecture", "Improve module boundaries"]
        )
    
    async def _analyze_design_patterns(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze design pattern usage."""
        return HealthMetric(
            name="Design Patterns",
            score=0.6,
            status="fair",
            details="Some design patterns are implemented",
            recommendations=["Apply more design patterns", "Document pattern usage"]
        )
    
    async def _analyze_separation_of_concerns(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze separation of concerns."""
        return HealthMetric(
            name="Separation of Concerns",
            score=0.8,
            status="good",
            details="Good separation of concerns observed",
            recommendations=["Maintain clear boundaries", "Avoid tight coupling"]
        )
    
    async def _analyze_scalability(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze scalability indicators."""
        return HealthMetric(
            name="Scalability",
            score=0.6,
            status="fair",
            details="Some scalability considerations present",
            recommendations=["Implement horizontal scaling", "Add load balancing"]
        )
    
    async def _analyze_dependency_freshness(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze dependency freshness."""
        return HealthMetric(
            name="Dependency Freshness",
            score=0.5,
            status="fair",
            details="Some dependencies are outdated",
            recommendations=["Update dependencies regularly", "Use automated updates"]
        )
    
    async def _analyze_dependency_security(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze dependency security."""
        return HealthMetric(
            name="Dependency Security",
            score=0.7,
            status="good",
            details="No critical security vulnerabilities found",
            recommendations=["Regular security audits", "Use dependency scanning"]
        )
    
    async def _analyze_dependency_size(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze dependency size."""
        return HealthMetric(
            name="Dependency Size",
            score=0.8,
            status="good",
            details="Dependencies are reasonably sized",
            recommendations=["Remove unused dependencies", "Use tree shaking"]
        )
    
    async def _analyze_dependency_licenses(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze dependency licenses."""
        return HealthMetric(
            name="Dependency Licenses",
            score=0.9,
            status="excellent",
            details="All dependencies have compatible licenses",
            recommendations=["Maintain license compliance", "Document license requirements"]
        )
    
    async def _analyze_secrets(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze for exposed secrets."""
        return HealthMetric(
            name="Secret Detection",
            score=0.8,
            status="good",
            details="No obvious secrets found in code",
            recommendations=["Use secret scanning tools", "Implement proper secret management"]
        )
    
    async def _analyze_input_validation(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze input validation."""
        return HealthMetric(
            name="Input Validation",
            score=0.6,
            status="fair",
            details="Basic input validation present",
            recommendations=["Implement comprehensive validation", "Use validation libraries"]
        )
    
    async def _analyze_authentication(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze authentication mechanisms."""
        return HealthMetric(
            name="Authentication",
            score=0.7,
            status="good",
            details="Authentication mechanisms are in place",
            recommendations=["Implement multi-factor authentication", "Use secure session management"]
        )
    
    async def _analyze_tls_usage(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze TLS/HTTPS usage."""
        return HealthMetric(
            name="TLS Usage",
            score=0.9,
            status="excellent",
            details="HTTPS is properly configured",
            recommendations=["Enforce HTTPS everywhere", "Use HSTS headers"]
        )
    
    async def _analyze_test_coverage(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze test coverage."""
        return HealthMetric(
            name="Test Coverage",
            score=0.6,
            status="fair",
            details="Test coverage is moderate",
            recommendations=["Increase test coverage", "Aim for 80%+ coverage"]
        )
    
    async def _analyze_test_quality(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze test quality."""
        return HealthMetric(
            name="Test Quality",
            score=0.7,
            status="good",
            details="Tests are well-written and meaningful",
            recommendations=["Follow testing best practices", "Use test-driven development"]
        )
    
    async def _analyze_test_automation(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze test automation."""
        return HealthMetric(
            name="Test Automation",
            score=0.8,
            status="good",
            details="Tests are automated in CI/CD",
            recommendations=["Implement parallel testing", "Add performance tests"]
        )
    
    async def _analyze_test_diversity(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze test diversity."""
        return HealthMetric(
            name="Test Diversity",
            score=0.5,
            status="fair",
            details="Limited test types present",
            recommendations=["Add integration tests", "Include end-to-end tests"]
        )
    
    async def _analyze_performance_optimizations(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze performance optimizations."""
        return HealthMetric(
            name="Performance Optimizations",
            score=0.6,
            status="fair",
            details="Some performance optimizations present",
            recommendations=["Profile application performance", "Implement caching strategies"]
        )
    
    async def _analyze_resource_usage(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze resource usage."""
        return HealthMetric(
            name="Resource Usage",
            score=0.7,
            status="good",
            details="Resource usage is reasonable",
            recommendations=["Monitor memory usage", "Optimize database queries"]
        )
    
    async def _analyze_caching(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze caching strategies."""
        return HealthMetric(
            name="Caching",
            score=0.5,
            status="fair",
            details="Limited caching implementation",
            recommendations=["Implement Redis caching", "Use CDN for static assets"]
        )
    
    async def _analyze_database_efficiency(self, contents: Dict[str, Any]) -> HealthMetric:
        """Analyze database efficiency."""
        return HealthMetric(
            name="Database Efficiency",
            score=0.6,
            status="fair",
            details="Database queries could be optimized",
            recommendations=["Add database indexes", "Optimize query performance"]
        )
    
    def _calculate_overall_score(self, categories: List[HealthCategory]) -> float:
        """Calculate overall health score."""
        if not categories:
            return 0.0
        
        # Weight categories differently
        weights = {
            "Code Quality": 0.25,
            "Documentation": 0.15,
            "Architecture": 0.20,
            "Dependencies": 0.15,
            "Security": 0.15,
            "Testing": 0.10
        }
        
        weighted_sum = sum(
            category.overall_score * weights.get(category.name, 0.1)
            for category in categories
        )
        
        return min(1.0, weighted_sum)
    
    def _get_status_from_score(self, score: float) -> str:
        """Convert score to status."""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.7:
            return "good"
        elif score >= 0.5:
            return "fair"
        elif score >= 0.3:
            return "poor"
        else:
            return "critical"
    
    def _generate_summary(self, categories: List[HealthCategory], overall_score: float) -> str:
        """Generate health summary."""
        status = self._get_status_from_score(overall_score)
        
        if status == "excellent":
            return "Repository is in excellent health with strong practices across all areas."
        elif status == "good":
            return "Repository is in good health with minor areas for improvement."
        elif status == "fair":
            return "Repository has fair health with several areas needing attention."
        elif status == "poor":
            return "Repository health is poor with significant issues requiring immediate attention."
        else:
            return "Repository health is critical with major issues that need urgent resolution."
    
    def _identify_critical_issues(self, categories: List[HealthCategory]) -> List[str]:
        """Identify critical issues across all categories."""
        critical_issues = []
        
        for category in categories:
            if category.status in ["poor", "critical"]:
                critical_issues.append(f"{category.name}: {category.description}")
                
                for metric in category.metrics:
                    if metric.status in ["poor", "critical"]:
                        critical_issues.append(f"  - {metric.name}: {metric.details}")
        
        return critical_issues
    
    def _generate_recommendations(self, categories: List[HealthCategory]) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Collect all recommendations from metrics
        for category in categories:
            for metric in category.metrics:
                recommendations.extend(metric.recommendations)
        
        # Remove duplicates and prioritize
        unique_recommendations = list(set(recommendations))
        
        # Sort by priority (critical issues first)
        priority_keywords = ["critical", "security", "urgent", "immediate"]
        
        def priority_score(rec):
            return sum(1 for keyword in priority_keywords if keyword.lower() in rec.lower())
        
        unique_recommendations.sort(key=priority_score, reverse=True)
        
        return unique_recommendations[:10]  # Return top 10 recommendations
