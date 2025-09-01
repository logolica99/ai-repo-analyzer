"""
Tests for the test generation functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from github_repo_analyzer.types import (
    TestType, TestPriority, TestCase, TestSuite, TestDocumentation,
    TestGenerationConfig, UserStory, AcceptanceCriterion, StoryPriority, StoryEffort
)
from github_repo_analyzer.test_generator import TestGenerator


class TestTestGenerationTypes:
    """Test the test generation type definitions."""
    
    def test_test_type_enum(self):
        """Test TestType enum values."""
        assert TestType.UNIT.value == "unit"
        assert TestType.INTEGRATION.value == "integration"
        assert TestType.END_TO_END.value == "e2e"
        assert TestType.API.value == "api"
        assert TestType.UI.value == "ui"
        assert TestType.PERFORMANCE.value == "performance"
        assert TestType.SECURITY.value == "security"
    
    def test_test_priority_enum(self):
        """Test TestPriority enum values."""
        assert TestPriority.LOW.value == "Low"
        assert TestPriority.MEDIUM.value == "Medium"
        assert TestPriority.HIGH.value == "High"
        assert TestPriority.CRITICAL.value == "Critical"
    
    def test_test_case_creation(self):
        """Test TestCase creation."""
        test_case = TestCase(
            id=1,
            title="Test User Registration",
            description="Test user registration functionality",
            test_type=TestType.UNIT,
            priority=TestPriority.HIGH,
            user_story_id=1,
            user_story_title="User Authentication",
            test_steps=["1. Set up test", "2. Execute test", "3. Verify result"],
            expected_results=["Test passes", "User is registered"],
            prerequisites=["Test environment ready"],
            tags=["unit", "authentication"]
        )
        
        assert test_case.id == 1
        assert test_case.title == "Test User Registration"
        assert test_case.test_type == TestType.UNIT
        assert test_case.priority == TestPriority.HIGH
        assert len(test_case.test_steps) == 3
        assert len(test_case.expected_results) == 2
    
    def test_test_suite_creation(self):
        """Test TestSuite creation."""
        test_cases = [
            TestCase(
                id=1, title="Test 1", description="Test 1", test_type=TestType.UNIT,
                priority=TestPriority.HIGH, user_story_id=1, user_story_title="Story 1",
                test_steps=[], expected_results=[], prerequisites=[], tags=[]
            ),
            TestCase(
                id=2, title="Test 2", description="Test 2", test_type=TestType.UNIT,
                priority=TestPriority.MEDIUM, user_story_id=1, user_story_title="Story 1",
                test_steps=[], expected_results=[], prerequisites=[], tags=[]
            )
        ]
        
        suite = TestSuite(
            id=1,
            name="Unit Tests for Story 1",
            description="Test suite for user story 1",
            test_cases=test_cases,
            test_type=TestType.UNIT,
            user_story_ids=[1]
        )
        
        assert suite.id == 1
        assert suite.name == "Unit Tests for Story 1"
        assert suite.total_tests == 2
        assert suite.test_type == TestType.UNIT
    
    def test_test_documentation_creation(self):
        """Test TestDocumentation creation."""
        test_suites = [
            TestSuite(
                id=1, name="Suite 1", description="Suite 1", test_cases=[],
                test_type=TestType.UNIT, user_story_ids=[1]
            )
        ]
        
        doc = TestDocumentation(
            repository_name="test/repo",
            analysis_date=datetime.now(),
            total_test_cases=5,
            test_suites=test_suites,
            test_coverage={"unit": 60.0, "integration": 40.0},
            testing_strategy="Comprehensive testing approach",
            test_environment_requirements=["Python 3.8+", "pytest"],
            execution_instructions="Run tests with pytest",
            maintenance_notes="Update tests monthly"
        )
        
        assert doc.repository_name == "test/repo"
        assert doc.total_test_cases == 5
        assert len(doc.test_suites) == 1
        assert doc.test_coverage["unit"] == 60.0
    
    def test_test_generation_config(self):
        """Test TestGenerationConfig creation."""
        config = TestGenerationConfig(
            include_unit_tests=True,
            include_integration_tests=False,
            include_e2e_tests=True,
            include_api_tests=True,
            max_tests_per_story=10,
            focus_area="security"
        )
        
        assert config.include_unit_tests is True
        assert config.include_integration_tests is False
        assert config.include_e2e_tests is True
        assert config.max_tests_per_story == 10
        assert config.focus_area == "security"


class TestTestGenerator:
    """Test the TestGenerator class."""
    
    def test_test_generator_initialization(self):
        """Test TestGenerator initialization."""
        config = TestGenerationConfig()
        generator = TestGenerator(config)
        
        assert generator.config == config
    
    def test_parse_test_type(self):
        """Test test type parsing."""
        config = TestGenerationConfig()
        generator = TestGenerator(config)
        
        assert generator._parse_test_type("unit") == TestType.UNIT
        assert generator._parse_test_type("integration") == TestType.INTEGRATION
        assert generator._parse_test_type("e2e") == TestType.END_TO_END
        assert generator._parse_test_type("api") == TestType.API
        assert generator._parse_test_type("unknown") == TestType.UNIT  # Default
    
    def test_parse_test_priority(self):
        """Test test priority parsing."""
        config = TestGenerationConfig()
        generator = TestGenerator(config)
        
        assert generator._parse_test_priority("low") == TestPriority.LOW
        assert generator._parse_test_priority("medium") == TestPriority.MEDIUM
        assert generator._parse_test_priority("high") == TestPriority.HIGH
        assert generator._parse_test_priority("critical") == TestPriority.CRITICAL
        assert generator._parse_test_priority("unknown") == TestPriority.MEDIUM  # Default
    
    def test_calculate_test_coverage(self):
        """Test test coverage calculation."""
        config = TestGenerationConfig()
        generator = TestGenerator(config)
        
        # Create test cases
        test_cases = [
            TestCase(
                id=1, title="Test 1", description="Test 1", test_type=TestType.UNIT,
                priority=TestPriority.HIGH, user_story_id=1, user_story_title="Story 1",
                test_steps=[], expected_results=[], prerequisites=[], tags=[]
            ),
            TestCase(
                id=2, title="Test 2", description="Test 2", test_type=TestType.INTEGRATION,
                priority=TestPriority.MEDIUM, user_story_id=1, user_story_title="Story 1",
                test_steps=[], expected_results=[], prerequisites=[], tags=[]
            ),
            TestCase(
                id=3, title="Test 3", description="Test 3", test_type=TestType.UNIT,
                priority=TestPriority.LOW, user_story_id=1, user_story_title="Story 1",
                test_steps=[], expected_results=[], prerequisites=[], tags=[]
            )
        ]
        
        test_suites = [
            TestSuite(
                id=1, name="Suite 1", description="Suite 1", test_cases=test_cases,
                test_type=TestType.UNIT, user_story_ids=[1]
            )
        ]
        
        coverage = generator._calculate_test_coverage(test_cases, test_suites)
        
        assert coverage["unit"] == pytest.approx(66.67, 0.01)
        assert coverage["integration"] == pytest.approx(33.33, 0.01)
    
    def test_create_test_suites(self):
        """Test test suite creation from test cases."""
        config = TestGenerationConfig()
        generator = TestGenerator(config)
        
        # Create test cases with different types
        test_cases = [
            TestCase(
                id=1, title="Unit Test", description="Unit test", test_type=TestType.UNIT,
                priority=TestPriority.HIGH, user_story_id=1, user_story_title="Story 1",
                test_steps=[], expected_results=[], prerequisites=[], tags=[]
            ),
            TestCase(
                id=2, title="Integration Test", description="Integration test", test_type=TestType.INTEGRATION,
                priority=TestPriority.MEDIUM, user_story_id=1, user_story_title="Story 1",
                test_steps=[], expected_results=[], prerequisites=[], tags=[]
            ),
            TestCase(
                id=3, title="Another Unit Test", description="Another unit test", test_type=TestType.UNIT,
                priority=TestPriority.LOW, user_story_id=1, user_story_title="Story 1",
                test_steps=[], expected_results=[], prerequisites=[], tags=[]
            )
        ]
        
        story = UserStory(
            id=1,
            title="User Authentication",
            description="As a user, I want to authenticate",
            acceptance_criteria=[],
            priority=StoryPriority.HIGH,
            effort=StoryEffort.MEDIUM
        )
        
        suites = generator._create_test_suites(test_cases, story)
        
        assert len(suites) == 2  # One for unit, one for integration
        assert suites[0].test_type == TestType.UNIT
        assert suites[0].total_tests == 2
        assert suites[1].test_type == TestType.INTEGRATION
        assert suites[1].total_tests == 1


if __name__ == "__main__":
    pytest.main([__file__])
