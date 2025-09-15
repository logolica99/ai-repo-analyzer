"""
File-based health analyzer that clones repositories and analyzes actual source code.
"""

import asyncio
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .types import RepositoryInfo, GitHubConfig, ClaudeConfig
from .health_analyzer import HealthMetric, HealthCategory, HealthReport, HealthAnalyzer
from .repo_cloner import RepositoryCloner


class FileBasedHealthAnalyzer(HealthAnalyzer):
    """Health analyzer that clones repositories and analyzes actual source code files."""
    
    def __init__(self, github_config: GitHubConfig, claude_config: ClaudeConfig):
        super().__init__(github_config)
        self.claude_config = claude_config
        self.repo_cloner = RepositoryCloner()
    
    async def analyze_repository_health(self, repo_owner: str, repo_name: str) -> HealthReport:
        """Analyze repository health by cloning and analyzing actual files."""
        
        # Fetch repository information
        repo_info = self.github_client.get_repository_info(repo_owner, repo_name)
        
        # Clone and analyze the repository
        file_analysis = await self.repo_cloner.clone_and_analyze_repository(
            repo_info, 
            self.github_client.config.token
        )
        
        if "error" in file_analysis:
            # Fallback to basic analysis if cloning fails
            return await self._fallback_analysis(repo_info, file_analysis["error"])
        
        # Analyze different health categories based on actual files
        categories = []
        
        # Code Quality Analysis based on actual files
        code_quality = self._analyze_code_quality_from_files(file_analysis)
        categories.append(code_quality)
        
        # Documentation Analysis based on actual files
        documentation = self._analyze_documentation_from_files(file_analysis)
        categories.append(documentation)
        
        # Architecture Analysis based on actual files
        architecture = self._analyze_architecture_from_files(file_analysis)
        categories.append(architecture)
        
        # Dependencies Analysis based on actual files
        dependencies = self._analyze_dependencies_from_files(file_analysis)
        categories.append(dependencies)
        
        # Security Analysis based on actual files
        security = self._analyze_security_from_files(file_analysis)
        categories.append(security)
        
        # Testing Analysis based on actual files
        testing = self._analyze_testing_from_files(file_analysis)
        categories.append(testing)
        
        # Performance Analysis based on actual files
        performance = self._analyze_performance_from_files(file_analysis)
        categories.append(performance)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(categories)
        overall_status = self._get_status_from_score(overall_score)
        
        # Generate summary and recommendations
        summary = self._generate_summary(categories, overall_score)
        critical_issues = self._identify_critical_issues(categories)
        recommendations = self._generate_recommendations(categories)
        
        # Cleanup
        self.repo_cloner.cleanup()
        
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
    
    async def _fallback_analysis(self, repo_info: RepositoryInfo, error: str) -> HealthReport:
        """Fallback analysis when cloning fails."""
        
        # Create basic categories with limited data
        categories = [
            HealthCategory(
                name="Code Quality",
                metrics=[
                    HealthMetric("Code Analysis", 0.5, "fair", f"File analysis failed: {error}", [])
                ],
                overall_score=0.5,
                status="fair",
                description="Limited analysis due to cloning failure"
            )
        ]
        
        return HealthReport(
            repository=repo_info,
            analysis_date=datetime.now(),
            overall_score=0.5,
            overall_status="fair",
            categories=categories,
            summary="Limited health analysis due to repository access issues",
            critical_issues=[f"Repository cloning failed: {error}"],
            recommendations=["Check repository access permissions", "Verify repository exists and is accessible"]
        )
    
    def _analyze_code_quality_from_files(self, file_analysis: Dict[str, Any]) -> HealthCategory:
        """Analyze code quality based on actual file analysis."""
        metrics = []
        
        # Code complexity based on file structure and size
        code_files = file_analysis.get("code_files", [])
        total_code_lines = sum(f.get("lines", 0) for f in code_files)
        avg_file_size = total_code_lines / len(code_files) if code_files else 0
        
        complexity_score = 0.7
        if avg_file_size > 200:
            complexity_score = 0.5  # Large files indicate complexity
        elif avg_file_size < 50:
            complexity_score = 0.9  # Small files are good
        
        metrics.append(HealthMetric(
            name="Code Complexity",
            score=complexity_score,
            status=self._get_status_from_score(complexity_score),
            details=f"Average file size: {avg_file_size:.1f} lines across {len(code_files)} code files",
            recommendations=["Break down large files", "Extract common functionality"]
        ))
        
        # Code style based on file organization
        structure = file_analysis.get("structure", {})
        style_score = 0.8
        if structure.get("has_src") and structure.get("has_tests"):
            style_score = 0.9
        elif structure.get("has_src"):
            style_score = 0.7
        
        metrics.append(HealthMetric(
            name="Code Style",
            score=style_score,
            status=self._get_status_from_score(style_score),
            details=f"Repository structure: {'Well organized' if structure.get('has_src') else 'Basic structure'}",
            recommendations=["Organize code in src/ directory", "Separate tests from main code"]
        ))
        
        # Code duplication based on file patterns
        duplication_score = 0.6
        if len(code_files) > 50:
            # More files might indicate better modularity
            duplication_score = 0.8
        elif len(code_files) < 10:
            # Few files might indicate poor separation
            duplication_score = 0.4
        
        metrics.append(HealthMetric(
            name="Code Duplication",
            score=duplication_score,
            status=self._get_status_from_score(duplication_score),
            details=f"Code files: {len(code_files)} total",
            recommendations=["Extract common functionality", "Use shared libraries"]
        ))
        
        # Code size based on total lines
        size_score = 0.7
        if total_code_lines > 10000:
            size_score = 0.9  # Large codebase
        elif total_code_lines < 1000:
            size_score = 0.5  # Small codebase
        
        metrics.append(HealthMetric(
            name="Code Size",
            score=size_score,
            status=self._get_status_from_score(size_score),
            details=f"Total code lines: {total_code_lines}",
            recommendations=["Monitor codebase growth", "Use code splitting if needed"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Code Quality",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis based on actual source code files"
        )
    
    def _analyze_documentation_from_files(self, file_analysis: Dict[str, Any]) -> HealthCategory:
        """Analyze documentation based on actual file analysis."""
        metrics = []
        
        # README quality based on actual README files
        doc_files = file_analysis.get("documentation_files", [])
        readme_files = [f for f in doc_files if "readme" in f["path"].lower()]
        
        readme_score = 0.6
        if readme_files:
            readme_size = readme_files[0].get("lines", 0)
            if readme_size > 50:
                readme_score = 0.8
            elif readme_size > 20:
                readme_score = 0.7
            else:
                readme_score = 0.4
        
        metrics.append(HealthMetric(
            name="README Quality",
            score=readme_score,
            status=self._get_status_from_score(readme_score),
            details=f"README files: {len(readme_files)}, lines: {readme_files[0].get('lines', 0) if readme_files else 0}",
            recommendations=["Expand README with more details", "Add installation and usage instructions"]
        ))
        
        # Code documentation based on code files with comments
        code_files = file_analysis.get("code_files", [])
        documented_files = 0
        
        for code_file in code_files:
            content = code_file.get("content", "")
            if content and ("def " in content or "function " in content or "class " in content):
                # Check for docstrings or comments
                if '"""' in content or "'''" in content or "//" in content or "#" in content:
                    documented_files += 1
        
        doc_ratio = documented_files / len(code_files) if code_files else 0
        code_docs_score = min(0.9, doc_ratio)
        
        metrics.append(HealthMetric(
            name="Code Documentation",
            score=code_docs_score,
            status=self._get_status_from_score(code_docs_score),
            details=f"Documented files: {documented_files}/{len(code_files)} ({doc_ratio:.1%})",
            recommendations=["Add docstrings to functions", "Document complex algorithms"]
        ))
        
        # API documentation
        api_docs_score = 0.4
        if any("api" in f["path"].lower() for f in doc_files):
            api_docs_score = 0.7
        if any("swagger" in f["path"].lower() or "openapi" in f["path"].lower() for f in doc_files):
            api_docs_score = 0.9
        
        metrics.append(HealthMetric(
            name="API Documentation",
            score=api_docs_score,
            status=self._get_status_from_score(api_docs_score),
            details=f"API docs found: {any('api' in f['path'].lower() for f in doc_files)}",
            recommendations=["Generate API documentation", "Use OpenAPI/Swagger"]
        ))
        
        # Contributing guidelines
        contributing_score = 0.6
        if any("contributing" in f["path"].lower() for f in doc_files):
            contributing_score = 0.8
        if any("contribute" in f["path"].lower() for f in doc_files):
            contributing_score = 0.7
        
        metrics.append(HealthMetric(
            name="Contributing Guidelines",
            score=contributing_score,
            status=self._get_status_from_score(contributing_score),
            details=f"Contributing files: {sum(1 for f in doc_files if 'contribut' in f['path'].lower())}",
            recommendations=["Add detailed contribution guide", "Include development setup"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Documentation",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis based on actual documentation files"
        )
    
    def _analyze_architecture_from_files(self, file_analysis: Dict[str, Any]) -> HealthCategory:
        """Analyze architecture based on actual file analysis."""
        metrics = []
        
        # Modularity based on directory structure
        structure = file_analysis.get("structure", {})
        modularity_score = 0.7
        
        if structure.get("has_src") and structure.get("has_tests"):
            modularity_score = 0.9
        elif structure.get("has_src"):
            modularity_score = 0.8
        elif len(structure.get("main_directories", [])) > 3:
            modularity_score = 0.6
        
        metrics.append(HealthMetric(
            name="Modularity",
            score=modularity_score,
            status=self._get_status_from_score(modularity_score),
            details=f"Structure: src={structure.get('has_src')}, tests={structure.get('has_tests')}",
            recommendations=["Organize code in modules", "Separate concerns clearly"]
        ))
        
        # Design patterns based on file organization
        patterns_score = 0.6
        if structure.get("has_config") and structure.get("has_scripts"):
            patterns_score = 0.8
        elif structure.get("has_config"):
            patterns_score = 0.7
        
        metrics.append(HealthMetric(
            name="Design Patterns",
            score=patterns_score,
            status=self._get_status_from_score(patterns_score),
            details=f"Config files: {structure.get('has_config')}, Scripts: {structure.get('has_scripts')}",
            recommendations=["Apply design patterns", "Document architectural decisions"]
        ))
        
        # Separation of concerns
        separation_score = 0.8
        if structure.get("has_src") and structure.get("has_tests") and structure.get("has_docs"):
            separation_score = 0.9
        elif structure.get("has_src") and structure.get("has_tests"):
            separation_score = 0.8
        
        metrics.append(HealthMetric(
            name="Separation of Concerns",
            score=separation_score,
            status=self._get_status_from_score(separation_score),
            details=f"Clear separation: {separation_score > 0.7}",
            recommendations=["Maintain clear boundaries", "Avoid tight coupling"]
        ))
        
        # Scalability based on structure depth and organization
        scalability_score = 0.6
        depth = structure.get("depth", 0)
        if depth > 3 and structure.get("has_src"):
            scalability_score = 0.8
        elif depth > 2:
            scalability_score = 0.7
        
        metrics.append(HealthMetric(
            name="Scalability",
            score=scalability_score,
            status=self._get_status_from_score(scalability_score),
            details=f"Structure depth: {depth} levels",
            recommendations=["Plan for horizontal scaling", "Design for growth"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Architecture",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis based on actual repository structure"
        )
    
    def _analyze_dependencies_from_files(self, file_analysis: Dict[str, Any]) -> HealthCategory:
        """Analyze dependencies based on actual file analysis."""
        metrics = []
        
        # Dependency freshness based on config files
        config_files = file_analysis.get("config_files", [])
        dependency_files = [f for f in config_files if f["path"].endswith(("package.json", "requirements.txt", "pyproject.toml", "pom.xml"))]
        
        freshness_score = 0.7
        if dependency_files:
            freshness_score = 0.8  # Has dependency management
        else:
            freshness_score = 0.4  # No clear dependency management
        
        metrics.append(HealthMetric(
            name="Dependency Freshness",
            score=freshness_score,
            status=self._get_status_from_score(freshness_score),
            details=f"Dependency files: {len(dependency_files)}",
            recommendations=["Update dependencies regularly", "Use automated updates"]
        ))
        
        # Dependency security
        security_score = 0.7
        if any("lock" in f["path"].lower() for f in config_files):
            security_score = 0.8  # Has lock files for security
        
        metrics.append(HealthMetric(
            name="Dependency Security",
            score=security_score,
            status=self._get_status_from_score(security_score),
            details=f"Lock files: {any('lock' in f['path'].lower() for f in config_files)}",
            recommendations=["Use dependency scanning", "Regular security audits"]
        ))
        
        # Dependency size
        size_score = 0.8
        if len(dependency_files) > 3:
            size_score = 0.6  # Many dependency files
        elif len(dependency_files) == 0:
            size_score = 0.4  # No dependency management
        
        metrics.append(HealthMetric(
            name="Dependency Size",
            score=size_score,
            status=self._get_status_from_score(size_score),
            details=f"Config files: {len(config_files)}",
            recommendations=["Consolidate dependencies", "Remove unused dependencies"]
        ))
        
        # License compatibility
        license_score = 0.9
        if any("license" in f["path"].lower() for f in file_analysis.get("files", [])):
            license_score = 0.95
        
        metrics.append(HealthMetric(
            name="License Compatibility",
            score=license_score,
            status=self._get_status_from_score(license_score),
            details=f"License file: {any('license' in f['path'].lower() for f in file_analysis.get('files', []))}",
            recommendations=["Maintain license compliance", "Document license requirements"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Dependencies",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis based on actual dependency files"
        )
    
    def _analyze_security_from_files(self, file_analysis: Dict[str, Any]) -> HealthCategory:
        """Analyze security based on actual file analysis."""
        metrics = []
        
        # Secret detection based on file content
        secret_score = 0.8
        secret_indicators = ["password", "secret", "key", "token", "api_key"]
        
        for file_info in file_analysis.get("code_files", []):
            content = file_info.get("content", "").lower()
            if any(indicator in content for indicator in secret_indicators):
                secret_score = 0.4  # Potential secrets found
                break
        
        metrics.append(HealthMetric(
            name="Secret Detection",
            score=secret_score,
            status=self._get_status_from_score(secret_score),
            details=f"Secret patterns: {'Found' if secret_score < 0.7 else 'Not found'}",
            recommendations=["Use environment variables", "Implement secret management"]
        ))
        
        # Input validation based on code patterns
        validation_score = 0.6
        validation_patterns = ["validate", "sanitize", "escape", "filter"]
        
        for file_info in file_analysis.get("code_files", []):
            content = file_info.get("content", "").lower()
            if any(pattern in content for pattern in validation_patterns):
                validation_score = 0.8
                break
        
        metrics.append(HealthMetric(
            name="Input Validation",
            score=validation_score,
            status=self._get_status_from_score(validation_score),
            details=f"Validation patterns: {'Found' if validation_score > 0.7 else 'Limited'}",
            recommendations=["Implement comprehensive validation", "Use validation libraries"]
        ))
        
        # Authentication based on code patterns
        auth_score = 0.6
        auth_patterns = ["auth", "login", "session", "jwt", "oauth"]
        
        for file_info in file_analysis.get("code_files", []):
            content = file_info.get("content", "").lower()
            if any(pattern in content for pattern in auth_patterns):
                auth_score = 0.8
                break
        
        metrics.append(HealthMetric(
            name="Authentication",
            score=auth_score,
            status=self._get_status_from_score(auth_score),
            details=f"Auth patterns: {'Found' if auth_score > 0.7 else 'Basic'}",
            recommendations=["Implement secure authentication", "Use proven auth libraries"]
        ))
        
        # TLS usage based on configuration
        tls_score = 0.9
        config_files = file_analysis.get("config_files", [])
        if any("https" in f.get("content", "").lower() for f in config_files):
            tls_score = 0.95
        
        metrics.append(HealthMetric(
            name="TLS Usage",
            score=tls_score,
            status=self._get_status_from_score(tls_score),
            details=f"HTTPS config: {'Found' if tls_score > 0.9 else 'Not found'}",
            recommendations=["Enforce HTTPS everywhere", "Use HSTS headers"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Security",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis based on actual code patterns and configuration"
        )
    
    def _analyze_testing_from_files(self, file_analysis: Dict[str, Any]) -> HealthCategory:
        """Analyze testing based on actual file analysis."""
        metrics = []
        
        # Test coverage based on test files
        test_files = file_analysis.get("test_files", [])
        code_files = file_analysis.get("code_files", [])
        
        coverage_score = 0.6
        if test_files and code_files:
            test_ratio = len(test_files) / len(code_files)
            coverage_score = min(0.9, 0.4 + test_ratio * 2)
        
        metrics.append(HealthMetric(
            name="Test Coverage",
            score=coverage_score,
            status=self._get_status_from_score(coverage_score),
            details=f"Test files: {len(test_files)}, Code files: {len(code_files)}",
            recommendations=["Increase test coverage", "Aim for 80%+ coverage"]
        ))
        
        # Test quality based on test file organization
        quality_score = 0.7
        if file_analysis.get("structure", {}).get("has_tests"):
            quality_score = 0.8
        
        metrics.append(HealthMetric(
            name="Test Quality",
            score=quality_score,
            status=self._get_status_from_score(quality_score),
            details=f"Test directory: {file_analysis.get('structure', {}).get('has_tests', False)}",
            recommendations=["Organize tests properly", "Use testing best practices"]
        ))
        
        # Test automation based on CI files
        automation_score = 0.6
        if file_analysis.get("structure", {}).get("has_ci"):
            automation_score = 0.9
        
        metrics.append(HealthMetric(
            name="Test Automation",
            score=automation_score,
            status=self._get_status_from_score(automation_score),
            details=f"CI/CD: {file_analysis.get('structure', {}).get('has_ci', False)}",
            recommendations=["Set up automated testing", "Add performance tests"]
        ))
        
        # Test diversity based on test file types
        diversity_score = 0.5
        test_extensions = set(f["extension"] for f in test_files)
        if len(test_extensions) > 1:
            diversity_score = 0.7
        
        metrics.append(HealthMetric(
            name="Test Diversity",
            score=diversity_score,
            status=self._get_status_from_score(diversity_score),
            details=f"Test types: {len(test_extensions)}",
            recommendations=["Add integration tests", "Include end-to-end tests"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Testing",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis based on actual test files and structure"
        )
    
    def _analyze_performance_from_files(self, file_analysis: Dict[str, Any]) -> HealthCategory:
        """Analyze performance based on actual file analysis."""
        metrics = []
        
        # Performance optimizations based on code patterns
        optimization_score = 0.6
        optimization_patterns = ["cache", "optimize", "performance", "async", "lazy"]
        
        for file_info in file_analysis.get("code_files", []):
            content = file_info.get("content", "").lower()
            if any(pattern in content for pattern in optimization_patterns):
                optimization_score = 0.8
                break
        
        metrics.append(HealthMetric(
            name="Performance Optimizations",
            score=optimization_score,
            status=self._get_status_from_score(optimization_score),
            details=f"Optimization patterns: {'Found' if optimization_score > 0.7 else 'Limited'}",
            recommendations=["Profile application performance", "Implement caching strategies"]
        ))
        
        # Resource usage based on file sizes
        code_files = file_analysis.get("code_files", [])
        total_size = sum(f.get("size", 0) for f in code_files)
        avg_size = total_size / len(code_files) if code_files else 0
        
        resource_score = 0.7
        if avg_size > 10000:  # 10KB average
            resource_score = 0.5  # Large files
        elif avg_size < 1000:  # 1KB average
            resource_score = 0.9  # Small files
        
        metrics.append(HealthMetric(
            name="Resource Usage",
            score=resource_score,
            status=self._get_status_from_score(resource_score),
            details=f"Average file size: {avg_size:.0f} bytes",
            recommendations=["Monitor memory usage", "Optimize large files"]
        ))
        
        # Caching based on configuration
        caching_score = 0.5
        config_files = file_analysis.get("config_files", [])
        if any("cache" in f.get("content", "").lower() for f in config_files):
            caching_score = 0.8
        
        metrics.append(HealthMetric(
            name="Caching",
            score=caching_score,
            status=self._get_status_from_score(caching_score),
            details=f"Cache config: {'Found' if caching_score > 0.7 else 'Not found'}",
            recommendations=["Implement Redis caching", "Use CDN for static assets"]
        ))
        
        # Database efficiency based on code patterns
        database_score = 0.6
        db_patterns = ["database", "db", "query", "sql", "orm"]
        
        for file_info in file_analysis.get("code_files", []):
            content = file_info.get("content", "").lower()
            if any(pattern in content for pattern in db_patterns):
                database_score = 0.8
                break
        
        metrics.append(HealthMetric(
            name="Database Efficiency",
            score=database_score,
            status=self._get_status_from_score(database_score),
            details=f"Database patterns: {'Found' if database_score > 0.7 else 'Not found'}",
            recommendations=["Add database indexes", "Optimize query performance"]
        ))
        
        category_score = sum(m.score * m.weight for m in metrics) / sum(m.weight for m in metrics)
        
        return HealthCategory(
            name="Performance",
            metrics=metrics,
            overall_score=category_score,
            status=self._get_status_from_score(category_score),
            description="Analysis based on actual code patterns and file sizes"
        )
