"""
Basic tests for the GitHub Repository Analyzer.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from github_repo_analyzer.types import (
    RepositoryInfo, UserStory, AcceptanceCriterion, 
    StoryPriority, StoryEffort, AnalysisResult
)


def test_repository_info_creation():
    """Test creating a RepositoryInfo object."""
    repo_info = RepositoryInfo(
        owner="test-owner",
        name="test-repo",
        full_name="test-owner/test-repo",
        description="A test repository",
        language="Python",
        stars=100,
        forks=50,
        topics=["test", "example"],
        readme_content="This is a test README",
        license="MIT",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        size=1024,
        default_branch="main"
    )
    
    assert repo_info.owner == "test-owner"
    assert repo_info.name == "test-repo"
    assert repo_info.full_name == "test-owner/test-repo"
    assert repo_info.description == "A test repository"
    assert repo_info.language == "Python"
    assert repo_info.stars == 100
    assert repo_info.forks == 50
    assert repo_info.topics == ["test", "example"]
    assert repo_info.readme_content == "This is a test README"
    assert repo_info.license == "MIT"
    assert repo_info.size == 1024
    assert repo_info.default_branch == "main"


def test_user_story_creation():
    """Test creating a UserStory object."""
    acceptance_criteria = [
        AcceptanceCriterion("User can input data"),
        AcceptanceCriterion("Data is validated"),
        AcceptanceCriterion("User receives confirmation")
    ]
    
    user_story = UserStory(
        id=1,
        title="Data Input Feature",
        description="As a user, I want to input data, so that I can process information",
        acceptance_criteria=acceptance_criteria,
        priority=StoryPriority.HIGH,
        effort=StoryEffort.MEDIUM,
        tags=["feature", "data"]
    )
    
    assert user_story.id == 1
    assert user_story.title == "Data Input Feature"
    assert user_story.description == "As a user, I want to input data, so that I can process information"
    assert len(user_story.acceptance_criteria) == 3
    assert user_story.priority == StoryPriority.HIGH
    assert user_story.effort == StoryEffort.MEDIUM
    assert user_story.tags == ["feature", "data"]


def test_analysis_result_creation():
    """Test creating an AnalysisResult object."""
    repo_info = Mock(spec=RepositoryInfo)
    repo_info.full_name = "test-owner/test-repo"
    
    user_stories = [Mock(spec=UserStory)]
    
    analysis_result = AnalysisResult(
        repository=repo_info,
        user_stories=user_stories,
        analysis_date=datetime.now(),
        focus_area="testing",
        tech_stack=["Python", "pytest"],
        key_features=["Feature 1", "Feature 2"],
        target_users=["Developers", "Testers"]
    )
    
    assert analysis_result.repository == repo_info
    assert len(analysis_result.user_stories) == 1
    assert analysis_result.focus_area == "testing"
    assert analysis_result.tech_stack == ["Python", "pytest"]
    assert analysis_result.key_features == ["Feature 1", "Feature 2"]
    assert analysis_result.target_users == ["Developers", "Testers"]


def test_story_priority_enum():
    """Test StoryPriority enum values."""
    assert StoryPriority.LOW.value == "Low"
    assert StoryPriority.MEDIUM.value == "Medium"
    assert StoryPriority.HIGH.value == "High"
    assert StoryPriority.CRITICAL.value == "Critical"


def test_story_effort_enum():
    """Test StoryEffort enum values."""
    assert StoryEffort.SMALL.value == "Small"
    assert StoryEffort.MEDIUM.value == "Medium"
    assert StoryEffort.LARGE.value == "Large"
    assert StoryEffort.EXTRA_LARGE.value == "Extra Large"


def test_output_format_enum():
    """Test OutputFormat enum values."""
    from github_repo_analyzer.types import OutputFormat
    
    assert OutputFormat.TEXT.value == "text"
    assert OutputFormat.JSON.value == "json"
    assert OutputFormat.MARKDOWN.value == "markdown"


if __name__ == "__main__":
    pytest.main([__file__])
