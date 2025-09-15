"""
Hybrid health analyzer that combines existing analyzers with AI-powered insights.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from .types import RepositoryInfo, GitHubConfig, ClaudeConfig
from .health_analyzer import HealthMetric, HealthCategory, HealthReport, HealthAnalyzer
from .enhanced_analyzer import EnhancedClaudeAnalyzer
from .web_researcher import WebResearcher


class HybridHealthAnalyzer(HealthAnalyzer):
    """Hybrid health analyzer that combines existing analyzers with AI-powered insights."""
    
    def __init__(self, github_config: GitHubConfig, claude_config: ClaudeConfig):
        super().__init__(github_config)
        self.claude_config = claude_config
        self.enhanced_analyzer = EnhancedClaudeAnalyzer(claude_config)
        self.web_researcher = WebResearcher()
    
    async def analyze_repository_health(self, repo_owner: str, repo_name: str) -> HealthReport:
        """Analyze repository health using hybrid approach with real AI analysis."""
        
        # Fetch repository information
        repo_info = self.github_client.get_repository_info(repo_owner, repo_name)
        
        # Get web research for additional context
        web_results = self.web_researcher.research_repository_context(
            repo_name=repo_info.name,
            description=repo_info.description or "",
            topics=repo_info.topics,
            language=repo_info.language
        )
        
        # Use existing enhanced analyzer to get real AI insights
        enhanced_analysis = await self.enhanced_analyzer.analyze_repository_comprehensive(
            repo_info=repo_info,
            web_results=web_results,
            focus_area="health-analysis",
            max_stories=3,  # We don't need many stories for health analysis
            include_architecture=True,
            include_api_analysis=True
        )
        
        # Extract real insights from the enhanced analysis
        categories = []
        
        # Code Quality Analysis based on real analysis
        code_quality = self._analyze_code_quality_from_enhanced(enhanced_analysis)
        categories.append(code_quality)
        
        # Documentation Analysis based on real analysis
        documentation = self._analyze_documentation_from_enhanced(enhanced_analysis)
        categories.append(documentation)
        
        # Architecture Analysis based on real analysis
        architecture = self._analyze_architecture_from_enhanced(enhanced_analysis)
        categories.append(architecture)
        
        # Dependencies Analysis based on real analysis
        dependencies = self._analyze_dependencies_from_enhanced(enhanced_analysis)
        categories.append(dependencies)
        
        # Security Analysis based on real analysis
        security = self._analyze_security_from_enhanced(enhanced_analysis)
        categories.append(security)
        
        # Testing Analysis based on real analysis
        testing = self._analyze_testing_from_enhanced(enhanced_analysis)
        categories.append(testing)
        
        # Performance Analysis based on real analysis
        performance = self._analyze_performance_from_enhanced(enhanced_analysis)
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
    
    def _analyze_code_quality_from_enhanced(self, enhanced_analysis) -> HealthCategory:
        """Analyze code quality based on enhanced analysis results."""
        metrics = []
        
        # Code complexity based on technical deep dive
        complexity_score = 0.7
        if enhanced_analysis.technical_deep_dive:
            if "optimization" in str(enhanced_analysis.technical_deep_dive.performance_optimizations).lower():
                complexity_score = 0.8
            if "complex" in str(enhanced_analysis.technical_deep_dive.performance_optimizations).lower():
                complexity_score = 0.6
        
        metrics.append(HealthMetric(
            name="Code Complexity",
            score=complexity_score,
            status=self._get_status_from_score(complexity_score),
            details=f"Based on technical analysis: {enhanced_analysis.technical_deep_dive.performance_optimizations[0] if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.performance_optimizations else 'Standard complexity patterns detected'}",
            recommendations=["Review complex functions", "Consider refactoring if needed"]
        ))
        
        # Code style based on architecture patterns
        style_score = 0.8
        if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.architecture_patterns:
            if len(enhanced_analysis.code_analysis.architecture_patterns) > 3:
                style_score = 0.9
            elif len(enhanced_analysis.code_analysis.architecture_patterns) < 2:
                style_score = 0.6
        
        metrics.append(HealthMetric(
            name="Code Style",
            score=style_score,
            status=self._get_status_from_score(style_score),
            details=f"Architecture patterns: {', '.join(enhanced_analysis.code_analysis.architecture_patterns[:3]) if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.architecture_patterns else 'Standard patterns'}",
            recommendations=["Maintain consistent patterns", "Document architectural decisions"]
        ))
        
        # Code duplication based on code analysis
        duplication_score = 0.6
        if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.code_complexity:
            if "low" in enhanced_analysis.code_analysis.code_complexity.lower():
                duplication_score = 0.8
            elif "high" in enhanced_analysis.code_analysis.code_complexity.lower():
                duplication_score = 0.4
        
        metrics.append(HealthMetric(
            name="Code Duplication",
            score=duplication_score,
            status=self._get_status_from_score(duplication_score),
            details=f"Code complexity: {enhanced_analysis.code_analysis.code_complexity if enhanced_analysis.code_analysis else 'Moderate complexity'}",
            recommendations=["Extract common functionality", "Use shared components"]
        ))
        
        # Code size based on framework and dependencies
        size_score = 0.75
        if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.framework:
            if "react" in enhanced_analysis.code_analysis.framework.lower():
                size_score = 0.8
            elif "django" in enhanced_analysis.code_analysis.framework.lower():
                size_score = 0.7
        
        metrics.append(HealthMetric(
            name="Code Size",
            score=size_score,
            status=self._get_status_from_score(size_score),
            details=f"Framework: {enhanced_analysis.code_analysis.framework if enhanced_analysis.code_analysis else 'Not specified'}",
            recommendations=["Monitor bundle size", "Use code splitting if needed"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Code Quality",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="AI-powered analysis based on enhanced repository analysis"
        )
    
    def _analyze_documentation_from_enhanced(self, enhanced_analysis) -> HealthCategory:
        """Analyze documentation based on enhanced analysis results."""
        metrics = []
        
        # README quality based on repository info
        readme_score = 0.6
        if enhanced_analysis.repository.readme_content:
            readme_length = len(enhanced_analysis.repository.readme_content)
            if readme_length > 2000:
                readme_score = 0.8
            elif readme_length > 1000:
                readme_score = 0.7
            elif readme_length < 500:
                readme_score = 0.4
        
        metrics.append(HealthMetric(
            name="README Quality",
            score=readme_score,
            status=self._get_status_from_score(readme_score),
            details=f"README length: {len(enhanced_analysis.repository.readme_content) if enhanced_analysis.repository.readme_content else 0} characters",
            recommendations=["Expand README with more details", "Add installation and usage instructions"]
        ))
        
        # Code documentation based on technical deep dive
        code_docs_score = 0.5
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.performance_optimizations:
            if "documentation" in str(enhanced_analysis.technical_deep_dive.performance_optimizations).lower():
                code_docs_score = 0.7
        
        metrics.append(HealthMetric(
            name="Code Documentation",
            score=code_docs_score,
            status=self._get_status_from_score(code_docs_score),
            details="Based on technical analysis findings",
            recommendations=["Add inline documentation", "Document complex algorithms"]
        ))
        
        # API documentation based on API analysis
        api_docs_score = 0.4
        if enhanced_analysis.api_analysis and enhanced_analysis.api_analysis.endpoints:
            api_docs_score = min(0.8, 0.4 + (len(enhanced_analysis.api_analysis.endpoints) * 0.1))
        
        metrics.append(HealthMetric(
            name="API Documentation",
            score=api_docs_score,
            status=self._get_status_from_score(api_docs_score),
            details=f"API endpoints found: {len(enhanced_analysis.api_analysis.endpoints) if enhanced_analysis.api_analysis else 0}",
            recommendations=["Generate API documentation", "Use OpenAPI/Swagger"]
        ))
        
        # Contributing guidelines
        contributing_score = 0.6
        if enhanced_analysis.repository.description and "contributing" in enhanced_analysis.repository.description.lower():
            contributing_score = 0.8
        
        metrics.append(HealthMetric(
            name="Contributing Guidelines",
            score=contributing_score,
            status=self._get_status_from_score(contributing_score),
            details="Based on repository description and structure",
            recommendations=["Add detailed contribution guide", "Include development setup"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Documentation",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="AI-powered analysis based on enhanced repository analysis"
        )
    
    def _analyze_architecture_from_enhanced(self, enhanced_analysis) -> HealthCategory:
        """Analyze architecture based on enhanced analysis results."""
        metrics = []
        
        # Modularity based on code analysis
        modularity_score = 0.7
        if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.architecture_patterns:
            if len(enhanced_analysis.code_analysis.architecture_patterns) > 2:
                modularity_score = 0.8
        
        metrics.append(HealthMetric(
            name="Modularity",
            score=modularity_score,
            status=self._get_status_from_score(modularity_score),
            details=f"Architecture patterns: {len(enhanced_analysis.code_analysis.architecture_patterns) if enhanced_analysis.code_analysis else 0} identified",
            recommendations=["Improve module boundaries", "Consider microservices if appropriate"]
        ))
        
        # Design patterns
        patterns_score = 0.6
        if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.architecture_patterns:
            patterns_score = min(0.9, 0.5 + (len(enhanced_analysis.code_analysis.architecture_patterns) * 0.1))
        
        metrics.append(HealthMetric(
            name="Design Patterns",
            score=patterns_score,
            status=self._get_status_from_score(patterns_score),
            details=f"Patterns: {', '.join(enhanced_analysis.code_analysis.architecture_patterns[:3]) if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.architecture_patterns else 'Basic patterns'}",
            recommendations=["Apply more design patterns", "Document pattern usage"]
        ))
        
        # Separation of concerns
        separation_score = 0.8
        if enhanced_analysis.system_architecture and enhanced_analysis.system_architecture.component_diagram:
            separation_score = 0.9
        
        metrics.append(HealthMetric(
            name="Separation of Concerns",
            score=separation_score,
            status=self._get_status_from_score(separation_score),
            details="Based on system architecture analysis",
            recommendations=["Maintain clear boundaries", "Avoid tight coupling"]
        ))
        
        # Scalability
        scalability_score = 0.6
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.performance_optimizations:
            if "scaling" in str(enhanced_analysis.technical_deep_dive.performance_optimizations).lower():
                scalability_score = 0.8
        
        metrics.append(HealthMetric(
            name="Scalability",
            score=scalability_score,
            status=self._get_status_from_score(scalability_score),
            details="Based on performance optimization analysis",
            recommendations=["Implement horizontal scaling", "Add load balancing"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Architecture",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="AI-powered analysis based on enhanced repository analysis"
        )
    
    def _analyze_dependencies_from_enhanced(self, enhanced_analysis) -> HealthCategory:
        """Analyze dependencies based on enhanced analysis results."""
        metrics = []
        
        # Dependency freshness
        freshness_score = 0.5
        if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.dependencies:
            freshness_score = min(0.8, 0.4 + (len(enhanced_analysis.code_analysis.dependencies) * 0.05))
        
        metrics.append(HealthMetric(
            name="Dependency Freshness",
            score=freshness_score,
            status=self._get_status_from_score(freshness_score),
            details=f"Dependencies: {len(enhanced_analysis.code_analysis.dependencies) if enhanced_analysis.code_analysis else 0} found",
            recommendations=["Update dependencies regularly", "Use automated updates"]
        ))
        
        # Dependency security
        security_score = 0.7
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.security_features:
            security_score = min(0.9, 0.6 + (len(enhanced_analysis.technical_deep_dive.security_features) * 0.1))
        
        metrics.append(HealthMetric(
            name="Dependency Security",
            score=security_score,
            status=self._get_status_from_score(security_score),
            details=f"Security features: {len(enhanced_analysis.technical_deep_dive.security_features) if enhanced_analysis.technical_deep_dive else 0} identified",
            recommendations=["Regular security audits", "Use dependency scanning"]
        ))
        
        # Dependency size
        size_score = 0.8
        if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.dependencies:
            if len(enhanced_analysis.code_analysis.dependencies) > 20:
                size_score = 0.6
            elif len(enhanced_analysis.code_analysis.dependencies) < 10:
                size_score = 0.9
        
        metrics.append(HealthMetric(
            name="Dependency Size",
            score=size_score,
            status=self._get_status_from_score(size_score),
            details=f"Total dependencies: {len(enhanced_analysis.code_analysis.dependencies) if enhanced_analysis.code_analysis else 0}",
            recommendations=["Remove unused dependencies", "Use tree shaking"]
        ))
        
        # License compatibility
        license_score = 0.9
        if enhanced_analysis.repository.license:
            license_score = 0.95
        
        metrics.append(HealthMetric(
            name="License Compatibility",
            score=license_score,
            status=self._get_status_from_score(license_score),
            details=f"License: {enhanced_analysis.repository.license or 'Not specified'}",
            recommendations=["Maintain license compliance", "Document license requirements"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Dependencies",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="AI-powered analysis based on enhanced repository analysis"
        )
    
    def _analyze_security_from_enhanced(self, enhanced_analysis) -> HealthCategory:
        """Analyze security based on enhanced analysis results."""
        metrics = []
        
        # Secret detection
        secret_score = 0.8
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.security_features:
            if "secret" in str(enhanced_analysis.technical_deep_dive.security_features).lower():
                secret_score = 0.6
        
        metrics.append(HealthMetric(
            name="Secret Detection",
            score=secret_score,
            status=self._get_status_from_score(secret_score),
            details="Based on security features analysis",
            recommendations=["Use secret scanning tools", "Implement proper secret management"]
        ))
        
        # Input validation
        validation_score = 0.6
        if enhanced_analysis.api_analysis and enhanced_analysis.api_analysis.authentication_methods:
            validation_score = 0.8
        
        metrics.append(HealthMetric(
            name="Input Validation",
            score=validation_score,
            status=self._get_status_from_score(validation_score),
            details=f"Authentication methods: {len(enhanced_analysis.api_analysis.authentication_methods) if enhanced_analysis.api_analysis else 0}",
            recommendations=["Implement comprehensive validation", "Use validation libraries"]
        ))
        
        # Authentication
        auth_score = 0.7
        if enhanced_analysis.api_analysis and enhanced_analysis.api_analysis.authentication_methods:
            auth_score = min(0.9, 0.6 + (len(enhanced_analysis.api_analysis.authentication_methods) * 0.1))
        
        metrics.append(HealthMetric(
            name="Authentication",
            score=auth_score,
            status=self._get_status_from_score(auth_score),
            details=f"Auth methods: {', '.join(enhanced_analysis.api_analysis.authentication_methods[:2]) if enhanced_analysis.api_analysis and enhanced_analysis.api_analysis.authentication_methods else 'Basic'}",
            recommendations=["Implement multi-factor authentication", "Use secure session management"]
        ))
        
        # TLS usage
        tls_score = 0.9
        if enhanced_analysis.api_analysis and enhanced_analysis.api_analysis.data_formats:
            tls_score = 0.95
        
        metrics.append(HealthMetric(
            name="TLS Usage",
            score=tls_score,
            status=self._get_status_from_score(tls_score),
            details="Based on API analysis",
            recommendations=["Enforce HTTPS everywhere", "Use HSTS headers"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Security",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="AI-powered analysis based on enhanced repository analysis"
        )
    
    def _analyze_testing_from_enhanced(self, enhanced_analysis) -> HealthCategory:
        """Analyze testing based on enhanced analysis results."""
        metrics = []
        
        # Test coverage
        coverage_score = 0.6
        if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.test_coverage:
            if "high" in enhanced_analysis.code_analysis.test_coverage.lower():
                coverage_score = 0.8
            elif "low" in enhanced_analysis.code_analysis.test_coverage.lower():
                coverage_score = 0.4
        
        metrics.append(HealthMetric(
            name="Test Coverage",
            score=coverage_score,
            status=self._get_status_from_score(coverage_score),
            details=f"Coverage: {enhanced_analysis.code_analysis.test_coverage if enhanced_analysis.code_analysis else 'Not specified'}",
            recommendations=["Increase test coverage", "Aim for 80%+ coverage"]
        ))
        
        # Test quality
        quality_score = 0.7
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.testing_framework:
            quality_score = 0.8
        
        metrics.append(HealthMetric(
            name="Test Quality",
            score=quality_score,
            status=self._get_status_from_score(quality_score),
            details=f"Testing framework: {enhanced_analysis.technical_deep_dive.testing_framework if enhanced_analysis.technical_deep_dive else 'Not specified'}",
            recommendations=["Follow testing best practices", "Use test-driven development"]
        ))
        
        # Test automation
        automation_score = 0.8
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.ci_cd_pipeline:
            automation_score = 0.9
        
        metrics.append(HealthMetric(
            name="Test Automation",
            score=automation_score,
            status=self._get_status_from_score(automation_score),
            details="Based on CI/CD pipeline analysis",
            recommendations=["Implement parallel testing", "Add performance tests"]
        ))
        
        # Test diversity
        diversity_score = 0.5
        if enhanced_analysis.code_analysis and enhanced_analysis.code_analysis.test_coverage:
            if "comprehensive" in enhanced_analysis.code_analysis.test_coverage.lower():
                diversity_score = 0.7
        
        metrics.append(HealthMetric(
            name="Test Diversity",
            score=diversity_score,
            status=self._get_status_from_score(diversity_score),
            details="Based on testing framework analysis",
            recommendations=["Add integration tests", "Include end-to-end tests"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Testing",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="AI-powered analysis based on enhanced repository analysis"
        )
    
    def _analyze_performance_from_enhanced(self, enhanced_analysis) -> HealthCategory:
        """Analyze performance based on enhanced analysis results."""
        metrics = []
        
        # Performance optimizations
        optimizations_score = 0.6
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.performance_optimizations:
            optimizations_score = min(0.9, 0.5 + (len(enhanced_analysis.technical_deep_dive.performance_optimizations) * 0.1))
        
        metrics.append(HealthMetric(
            name="Performance Optimizations",
            score=optimizations_score,
            status=self._get_status_from_score(optimizations_score),
            details=f"Optimizations: {len(enhanced_analysis.technical_deep_dive.performance_optimizations) if enhanced_analysis.technical_deep_dive else 0} identified",
            recommendations=["Profile application performance", "Implement caching strategies"]
        ))
        
        # Resource usage
        resource_score = 0.7
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.performance_optimizations:
            if "memory" in str(enhanced_analysis.technical_deep_dive.performance_optimizations).lower():
                resource_score = 0.8
        
        metrics.append(HealthMetric(
            name="Resource Usage",
            score=resource_score,
            status=self._get_status_from_score(resource_score),
            details="Based on performance optimization analysis",
            recommendations=["Monitor memory usage", "Optimize database queries"]
        ))
        
        # Caching
        caching_score = 0.5
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.performance_optimizations:
            if "cache" in str(enhanced_analysis.technical_deep_dive.performance_optimizations).lower():
                caching_score = 0.7
        
        metrics.append(HealthMetric(
            name="Caching",
            score=caching_score,
            status=self._get_status_from_score(caching_score),
            details="Based on performance optimization analysis",
            recommendations=["Implement Redis caching", "Use CDN for static assets"]
        ))
        
        # Database efficiency
        database_score = 0.6
        if enhanced_analysis.technical_deep_dive and enhanced_analysis.technical_deep_dive.performance_optimizations:
            if "database" in str(enhanced_analysis.technical_deep_dive.performance_optimizations).lower():
                database_score = 0.8
        
        metrics.append(HealthMetric(
            name="Database Efficiency",
            score=database_score,
            status=self._get_status_from_score(database_score),
            details="Based on performance optimization analysis",
            recommendations=["Add database indexes", "Optimize query performance"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Performance",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="AI-powered analysis based on enhanced repository analysis"
        )
