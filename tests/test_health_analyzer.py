"""
Tests for the health analyzer functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from github_repo_analyzer.health_analyzer import HealthAnalyzer, HealthMetric, HealthCategory, HealthReport
from github_repo_analyzer.health_formatter import HealthFormatter
from github_repo_analyzer.types import RepositoryInfo, OutputFormat, GitHubConfig


def test_health_metric_creation():
    """Test creating a HealthMetric object."""
    metric = HealthMetric(
        name="Test Metric",
        score=0.8,
        status="good",
        details="Test details",
        recommendations=["Test recommendation"],
        weight=1.0
    )
    
    assert metric.name == "Test Metric"
    assert metric.score == 0.8
    assert metric.status == "good"
    assert metric.details == "Test details"
    assert metric.recommendations == ["Test recommendation"]
    assert metric.weight == 1.0


def test_health_category_creation():
    """Test creating a HealthCategory object."""
    metrics = [
        HealthMetric("Metric 1", 0.8, "good", "Details 1"),
        HealthMetric("Metric 2", 0.6, "fair", "Details 2")
    ]
    
    category = HealthCategory(
        name="Test Category",
        metrics=metrics,
        overall_score=0.7,
        status="good",
        description="Test category description"
    )
    
    assert category.name == "Test Category"
    assert len(category.metrics) == 2
    assert category.overall_score == 0.7
    assert category.status == "good"
    assert category.description == "Test category description"


def test_health_report_creation():
    """Test creating a HealthReport object."""
    repo_info = Mock(spec=RepositoryInfo)
    repo_info.full_name = "test/repo"
    
    categories = [
        HealthCategory("Category 1", [], 0.8, "good", "Description 1"),
        HealthCategory("Category 2", [], 0.6, "fair", "Description 2")
    ]
    
    report = HealthReport(
        repository=repo_info,
        analysis_date=datetime.now(),
        overall_score=0.7,
        overall_status="good",
        categories=categories,
        summary="Test summary",
        critical_issues=["Issue 1"],
        recommendations=["Rec 1", "Rec 2"]
    )
    
    assert report.repository == repo_info
    assert report.overall_score == 0.7
    assert report.overall_status == "good"
    assert len(report.categories) == 2
    assert report.summary == "Test summary"
    assert len(report.critical_issues) == 1
    assert len(report.recommendations) == 2


def test_health_analyzer_initialization():
    """Test HealthAnalyzer initialization."""
    config = GitHubConfig()
    analyzer = HealthAnalyzer(config)
    
    assert analyzer.github_client is not None
    assert isinstance(analyzer.file_extensions, dict)
    assert 'python' in analyzer.file_extensions
    assert 'javascript' in analyzer.file_extensions


def test_status_from_score():
    """Test status calculation from score."""
    analyzer = HealthAnalyzer(GitHubConfig())
    
    assert analyzer._get_status_from_score(0.95) == "excellent"
    assert analyzer._get_status_from_score(0.8) == "good"
    assert analyzer._get_status_from_score(0.6) == "fair"
    assert analyzer._get_status_from_score(0.4) == "poor"
    assert analyzer._get_status_from_score(0.1) == "critical"


def test_overall_score_calculation():
    """Test overall score calculation."""
    analyzer = HealthAnalyzer(GitHubConfig())
    
    categories = [
        HealthCategory("Code Quality", [], 0.8, "good", "Description"),
        HealthCategory("Documentation", [], 0.6, "fair", "Description"),
        HealthCategory("Architecture", [], 0.7, "good", "Description"),
        HealthCategory("Dependencies", [], 0.9, "excellent", "Description"),
        HealthCategory("Security", [], 0.8, "good", "Description"),
        HealthCategory("Testing", [], 0.5, "fair", "Description")
    ]
    
    overall_score = analyzer._calculate_overall_score(categories)
    
    # Should be a weighted average
    assert 0.0 <= overall_score <= 1.0
    assert overall_score > 0.6  # Should be good overall


def test_health_formatter_text():
    """Test health formatter text output."""
    repo_info = Mock(spec=RepositoryInfo)
    repo_info.full_name = "test/repo"
    repo_info.owner = "test"
    repo_info.name = "repo"
    repo_info.description = "Test repository"
    repo_info.language = "Python"
    repo_info.stars = 100
    repo_info.forks = 50
    
    categories = [
        HealthCategory(
            "Code Quality",
            [HealthMetric("Complexity", 0.8, "good", "Good complexity")],
            0.8,
            "good",
            "Code quality analysis"
        )
    ]
    
    report = HealthReport(
        repository=repo_info,
        analysis_date=datetime.now(),
        overall_score=0.8,
        overall_status="good",
        categories=categories,
        summary="Good health",
        critical_issues=[],
        recommendations=["Test recommendation"]
    )
    
    formatter = HealthFormatter(OutputFormat.TEXT)
    output = formatter.format_health_report(report)
    
    assert "Repository Health Report" in output
    assert "test/repo" in output
    assert "Code Quality" in output
    assert "Good health" in output


def test_health_formatter_markdown():
    """Test health formatter markdown output."""
    repo_info = Mock(spec=RepositoryInfo)
    repo_info.full_name = "test/repo"
    repo_info.owner = "test"
    repo_info.name = "repo"
    repo_info.description = "Test repository"
    repo_info.language = "Python"
    repo_info.stars = 100
    repo_info.forks = 50
    
    categories = [
        HealthCategory(
            "Code Quality",
            [HealthMetric("Complexity", 0.8, "good", "Good complexity")],
            0.8,
            "good",
            "Code quality analysis"
        )
    ]
    
    report = HealthReport(
        repository=repo_info,
        analysis_date=datetime.now(),
        overall_score=0.8,
        overall_status="good",
        categories=categories,
        summary="Good health",
        critical_issues=[],
        recommendations=["Test recommendation"]
    )
    
    formatter = HealthFormatter(OutputFormat.MARKDOWN)
    output = formatter.format_health_report(report)
    
    assert "# 🏥 Repository Health Report" in output
    assert "**Repository:** test/repo" in output
    assert "### 🟡 Code Quality" in output
    assert "| Metric | Score | Status | Details |" in output


def test_health_formatter_json():
    """Test health formatter JSON output."""
    repo_info = Mock(spec=RepositoryInfo)
    repo_info.full_name = "test/repo"
    repo_info.owner = "test"
    repo_info.name = "repo"
    repo_info.description = "Test repository"
    repo_info.language = "Python"
    repo_info.stars = 100
    repo_info.forks = 50
    
    categories = [
        HealthCategory(
            "Code Quality",
            [HealthMetric("Complexity", 0.8, "good", "Good complexity")],
            0.8,
            "good",
            "Code quality analysis"
        )
    ]
    
    report = HealthReport(
        repository=repo_info,
        analysis_date=datetime.now(),
        overall_score=0.8,
        overall_status="good",
        categories=categories,
        summary="Good health",
        critical_issues=[],
        recommendations=["Test recommendation"]
    )
    
    formatter = HealthFormatter(OutputFormat.JSON)
    output = formatter.format_health_report(report)
    
    # Should be valid JSON
    import json
    data = json.loads(output)
    
    assert data["repository"]["full_name"] == "test/repo"
    assert data["overall_score"] == 0.8
    assert data["overall_status"] == "good"
    assert len(data["categories"]) == 1
    assert data["categories"][0]["name"] == "Code Quality"


def test_status_emoji_mapping():
    """Test status emoji mapping."""
    formatter = HealthFormatter(OutputFormat.TEXT)
    
    assert formatter._get_status_emoji("excellent") == "🟢"
    assert formatter._get_status_emoji("good") == "🟡"
    assert formatter._get_status_emoji("fair") == "🟠"
    assert formatter._get_status_emoji("poor") == "🔴"
    assert formatter._get_status_emoji("critical") == "💀"
    assert formatter._get_status_emoji("unknown") == "❓"


if __name__ == "__main__":
    pytest.main([__file__])
