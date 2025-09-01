"""
Test generation module for the GitHub Repository Analyzer.
Generates comprehensive test cases and documentation based on user stories.
"""

import json
import anyio
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock, ToolUseBlock, ToolResultBlock
from claude_code_sdk.types import Message

from .types import (
    RepositoryInfo, UserStory, TestCase, TestSuite, TestDocumentation, 
    TestType, TestPriority, TestGenerationConfig, AnalysisResult
)


class TestGenerator:
    """Generates comprehensive test cases and documentation from user stories."""
    
    def __init__(self, config: TestGenerationConfig):
        self.config = config
    
    async def generate_tests_from_analysis(
        self,
        analysis_result: AnalysisResult,
        repo_info: RepositoryInfo
    ) -> TestDocumentation:
        """Generate comprehensive test documentation from analysis results."""
        
        # Detect test framework and language from repository
        test_framework = self._detect_test_framework(repo_info, analysis_result)
        test_language = self._detect_test_language(repo_info, analysis_result)
        
        # Generate test cases for each user story
        test_suites = []
        all_test_cases = []
        
        for story in analysis_result.user_stories:
            story_tests = await self._generate_tests_for_story(
                story, repo_info, test_framework, test_language
            )
            all_test_cases.extend(story_tests)
            
            # Group tests by type into test suites
            test_suites.extend(self._create_test_suites(story_tests, story))
        
        # Calculate test coverage
        test_coverage = self._calculate_test_coverage(all_test_cases, test_suites)
        
        # Generate testing strategy and documentation
        testing_strategy = await self._generate_testing_strategy(
            repo_info, analysis_result, test_framework, test_language
        )
        
        # Generate environment requirements and execution instructions
        env_requirements = self._generate_environment_requirements(
            repo_info, test_framework, test_language
        )
        
        execution_instructions = self._generate_execution_instructions(
            test_framework, test_language
        )
        
        maintenance_notes = self._generate_maintenance_notes(test_suites)
        
        return TestDocumentation(
            repository_name=repo_info.full_name,
            analysis_date=datetime.now(),
            total_test_cases=len(all_test_cases),
            test_suites=test_suites,
            test_coverage=test_coverage,
            testing_strategy=testing_strategy,
            test_environment_requirements=env_requirements,
            execution_instructions=execution_instructions,
            maintenance_notes=maintenance_notes,
            metadata={
                'test_framework': test_framework,
                'test_language': test_language,
                'focus_area': self.config.focus_area,
                'generation_config': {
                    'include_unit_tests': self.config.include_unit_tests,
                    'include_integration_tests': self.config.include_integration_tests,
                    'include_e2e_tests': self.config.include_e2e_tests,
                    'include_api_tests': self.config.include_api_tests,
                    'max_tests_per_story': self.config.max_tests_per_story
                }
            }
        )
    
    async def _generate_tests_for_story(
        self,
        story: UserStory,
        repo_info: RepositoryInfo,
        test_framework: str,
        test_language: str
    ) -> List[TestCase]:
        """Generate test cases for a specific user story."""
        
        prompt = self._build_test_generation_prompt(
            story, repo_info, test_framework, test_language
        )
        
        options = ClaudeCodeOptions(
            system_prompt=self._get_test_generation_system_prompt(),
            max_turns=3,
            allowed_tools=["Read", "Write", "Bash"],
            permission_mode="acceptEdits"
        )
        
        # Collect response from Claude
        response_text = ""
        async for message in query(prompt=prompt, options=options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
        
        # Parse the response to extract test cases
        test_cases = self._parse_test_generation_response(
            response_text, story, test_framework, test_language
        )
        
        return test_cases[:self.config.max_tests_per_story]
    
    def _build_test_generation_prompt(
        self,
        story: UserStory,
        repo_info: RepositoryInfo,
        test_framework: str,
        test_language: str
    ) -> str:
        """Build a comprehensive prompt for test generation."""
        
        prompt = f"""
        Generate comprehensive test cases for the following user story from the {repo_info.full_name} repository.

        Repository Information:
        - Name: {repo_info.full_name}
        - Description: {repo_info.description or 'No description available'}
        - Language: {repo_info.language or 'Not specified'}
        - Test Framework: {test_framework}
        - Programming Language: {test_language}

        User Story:
        - ID: {story.id}
        - Title: {story.title}
        - Description: {story.description}
        - Priority: {story.priority.value}
        - Effort: {story.effort.value}
        - Tags: {', '.join(story.tags) if story.tags else 'None'}

        Acceptance Criteria:
        {chr(10).join([f"- {criterion.description}" for criterion in story.acceptance_criteria])}

        Generate the following types of tests (if applicable):
        - Unit tests for individual components/functions
        - Integration tests for component interactions
        - API tests for endpoints and data flow
        - End-to-end tests for complete user workflows
        - Performance tests for critical paths
        - Security tests for authentication and authorization

        For each test case, provide:
        1. Clear, descriptive title
        2. Detailed description of what is being tested
        3. Test type (unit, integration, e2e, api, performance, security)
        4. Priority level (Low, Medium, High, Critical)
        5. Step-by-step test execution steps
        6. Expected results for each step
        7. Prerequisites and test data requirements
        8. Relevant tags for categorization

        Focus on creating practical, executable tests that cover all acceptance criteria.
        """
        
        return prompt
    
    def _get_test_generation_system_prompt(self) -> str:
        """Get the system prompt for test generation."""
        
        return """You are an expert QA engineer and test automation specialist. Your task is to generate comprehensive, practical test cases that can be executed by development teams.

        When generating tests:
        1. Focus on testability and clarity
        2. Ensure tests cover all acceptance criteria
        3. Provide realistic test data and scenarios
        4. Consider edge cases and error conditions
        5. Make tests maintainable and reusable
        6. Follow testing best practices and patterns
        7. Generate tests in the specified framework and language
        8. Include both positive and negative test scenarios
        9. Consider performance and security aspects
        10. Provide clear execution instructions

        Format your response as a structured list of test cases with all required information."""
    
    def _parse_test_generation_response(
        self,
        response: str,
        story: UserStory,
        test_framework: str,
        test_language: str
    ) -> List[TestCase]:
        """Parse the Claude response to extract structured test cases."""
        
        test_cases = []
        test_id = 1
        
        # This is a simplified parser - in a real implementation, you might want
        # to use more sophisticated parsing or ask Claude to format in JSON
        lines = response.split('\n')
        current_test = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Test Case') or line.startswith('Test:'):
                # Save previous test if exists
                if current_test:
                    test_cases.append(current_test)
                
                # Start new test case
                title = line.replace('Test Case', '').replace('Test:', '').strip()
                current_test = TestCase(
                    id=test_id,
                    title=title,
                    description="",
                    test_type=TestType.UNIT,  # Default, will be updated
                    priority=TestPriority.MEDIUM,  # Default, will be updated
                    user_story_id=story.id,
                    user_story_title=story.title,
                    test_steps=[],
                    expected_results=[],
                    prerequisites=[],
                    test_data={},
                    tags=[]
                )
                test_id += 1
            
            elif current_test and line.startswith('Type:'):
                test_type_str = line.replace('Type:', '').strip().lower()
                current_test.test_type = self._parse_test_type(test_type_str)
            
            elif current_test and line.startswith('Priority:'):
                priority_str = line.replace('Priority:', '').strip()
                current_test.priority = self._parse_test_priority(priority_str)
            
            elif current_test and line.startswith('Steps:'):
                # Parse test steps
                pass  # Simplified for now
            
            elif current_test and line.startswith('Expected:'):
                # Parse expected results
                pass  # Simplified for now
        
        # Add the last test case
        if current_test:
            test_cases.append(current_test)
        
        # If parsing fails, create a basic test case
        if not test_cases:
            test_cases.append(TestCase(
                id=1,
                title=f"Basic test for {story.title}",
                description=f"Test covering the main functionality of: {story.description}",
                test_type=TestType.UNIT,
                priority=TestPriority.MEDIUM,
                user_story_id=story.id,
                user_story_title=story.title,
                test_steps=["1. Set up test environment", "2. Execute main functionality", "3. Verify results"],
                expected_results=["Environment is ready", "Functionality executes successfully", "Results match expectations"],
                prerequisites=["Test environment configured"],
                tags=["basic", "smoke"]
            ))
        
        return test_cases
    
    def _parse_test_type(self, type_str: str) -> TestType:
        """Parse test type string to TestType enum."""
        type_mapping = {
            'unit': TestType.UNIT,
            'integration': TestType.INTEGRATION,
            'e2e': TestType.END_TO_END,
            'end-to-end': TestType.END_TO_END,
            'api': TestType.API,
            'ui': TestType.UI,
            'performance': TestType.PERFORMANCE,
            'security': TestType.SECURITY
        }
        return type_mapping.get(type_str.lower(), TestType.UNIT)
    
    def _parse_test_priority(self, priority_str: str) -> TestPriority:
        """Parse priority string to TestPriority enum."""
        priority_mapping = {
            'low': TestPriority.LOW,
            'medium': TestPriority.MEDIUM,
            'high': TestPriority.HIGH,
            'critical': TestPriority.CRITICAL
        }
        return priority_mapping.get(priority_str.lower(), TestPriority.MEDIUM)
    
    def _create_test_suites(
        self,
        test_cases: List[TestCase],
        story: UserStory
    ) -> List[TestSuite]:
        """Create test suites by grouping test cases by type."""
        
        suites = []
        test_cases_by_type = {}
        
        # Group test cases by type
        for test_case in test_cases:
            test_type = test_case.test_type
            if test_type not in test_cases_by_type:
                test_cases_by_type[test_type] = []
            test_cases_by_type[test_type].append(test_case)
        
        # Create test suites for each type
        for test_type, cases in test_cases_by_type.items():
            if cases:
                suite = TestSuite(
                    id=len(suites) + 1,
                    name=f"{test_type.value.title()} Tests for {story.title}",
                    description=f"Test suite covering {test_type.value} testing for user story: {story.title}",
                    test_cases=cases,
                    test_type=test_type,
                    user_story_ids=[story.id]
                )
                suites.append(suite)
        
        return suites
    
    def _calculate_test_coverage(
        self,
        test_cases: List[TestCase],
        test_suites: List[TestSuite]
    ) -> Dict[str, float]:
        """Calculate test coverage by test type."""
        
        coverage = {}
        total_tests = len(test_cases)
        
        if total_tests == 0:
            return coverage
        
        # Count tests by type
        tests_by_type = {}
        for test_case in test_cases:
            test_type = test_case.test_type.value
            tests_by_type[test_type] = tests_by_type.get(test_type, 0) + 1
        
        # Calculate coverage percentages
        for test_type, count in tests_by_type.items():
            coverage[test_type] = (count / total_tests) * 100
        
        return coverage
    
    async def _generate_testing_strategy(
        self,
        repo_info: RepositoryInfo,
        analysis_result: AnalysisResult,
        test_framework: str,
        test_language: str
    ) -> str:
        """Generate a comprehensive testing strategy document."""
        
        prompt = f"""
        Generate a comprehensive testing strategy for the {repo_info.full_name} repository.

        Repository Context:
        - Language: {repo_info.language}
        - Test Framework: {test_framework}
        - Programming Language: {test_language}
        - Focus Area: {self.config.focus_area or 'General'}
        - Total User Stories: {len(analysis_result.user_stories)}

        Testing Requirements:
        - Unit Tests: {self.config.include_unit_tests}
        - Integration Tests: {self.config.include_integration_tests}
        - E2E Tests: {self.config.include_e2e_tests}
        - API Tests: {self.config.include_api_tests}

        Provide a comprehensive testing strategy that includes:
        1. Testing approach and methodology
        2. Test pyramid strategy
        3. Test environment setup
        4. Test data management
        5. Continuous integration testing
        6. Test automation strategy
        7. Quality gates and metrics
        8. Risk-based testing approach
        """
        
        options = ClaudeCodeOptions(
            system_prompt="You are an expert QA architect. Generate comprehensive, practical testing strategies.",
            max_turns=2,
            allowed_tools=["Read", "Write"],
            permission_mode="acceptEdits"
        )
        
        # Collect response from Claude
        response_text = ""
        async for message in query(prompt=prompt, options=options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
        
        return response_text
    
    def _generate_environment_requirements(
        self,
        repo_info: RepositoryInfo,
        test_framework: str,
        test_language: str
    ) -> List[str]:
        """Generate test environment requirements."""
        
        requirements = [
            f"{test_language} runtime environment",
            f"{test_framework} testing framework",
            "Test database or mock data sources",
            "Network access for integration tests",
            "Browser automation tools (for UI tests)",
            "Performance testing tools",
            "Security testing tools",
            "Test reporting and coverage tools"
        ]
        
        # Add language-specific requirements
        if test_language.lower() in ['python', 'py']:
            requirements.extend([
                "Python virtual environment",
                "pip package manager",
                "pytest or unittest framework"
            ])
        elif test_language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            requirements.extend([
                "Node.js runtime",
                "npm or yarn package manager",
                "Jest, Mocha, or similar framework"
            ])
        elif test_language.lower() in ['java']:
            requirements.extend([
                "Java Development Kit (JDK)",
                "Maven or Gradle build tool",
                "JUnit testing framework"
            ])
        
        return requirements
    
    def _generate_execution_instructions(
        self,
        test_framework: str,
        test_language: str
    ) -> str:
        """Generate test execution instructions."""
        
        instructions = f"""
        Test Execution Instructions for {test_language} with {test_framework}

        1. Environment Setup:
           - Install {test_language} and {test_framework}
           - Set up test environment variables
           - Configure test database connections

        2. Running Tests:
           - Unit Tests: Run with {test_framework} unit test runner
           - Integration Tests: Ensure external services are available
           - E2E Tests: Start application and run browser tests
           - API Tests: Verify API endpoints are accessible

        3. Test Data:
           - Use provided test fixtures and mock data
           - Reset test data between test runs
           - Ensure test isolation

        4. Reporting:
           - Generate test coverage reports
           - Export test results in desired format
           - Monitor test execution time and failures

        5. Continuous Integration:
           - Integrate tests into CI/CD pipeline
           - Set up automated test execution
           - Configure quality gates and thresholds
        """
        
        return instructions
    
    def _generate_maintenance_notes(self, test_suites: List[TestSuite]) -> str:
        """Generate maintenance notes for the test suite."""
        
        notes = f"""
        Test Maintenance Notes

        Total Test Suites: {len(test_suites)}
        Total Test Cases: {sum(suite.total_tests for suite in test_suites)}

        Maintenance Guidelines:
        1. Regular Review: Review test cases monthly for relevance
        2. Update Tests: Update tests when user stories change
        3. Remove Obsolete Tests: Delete tests for removed features
        4. Performance Monitoring: Monitor test execution time
        5. Coverage Analysis: Maintain target test coverage levels
        6. Test Data Management: Keep test data current and relevant

        Test Suite Breakdown:
        """
        
        for suite in test_suites:
            notes += f"\n- {suite.name}: {suite.total_tests} tests ({suite.test_type.value})"
        
        return notes
    
    def _detect_test_framework(
        self,
        repo_info: RepositoryInfo,
        analysis_result: AnalysisResult
    ) -> str:
        """Detect the test framework used in the repository."""
        
        # Check if we have technical analysis
        if analysis_result.technical_deep_dive and analysis_result.technical_deep_dive.testing_framework:
            testing_info = analysis_result.technical_deep_dive.testing_framework
            if isinstance(testing_info, dict):
                # Extract framework information
                if 'unit_tests' in testing_info:
                    unit_test_info = testing_info['unit_tests']
                    if 'pytest' in str(unit_test_info).lower():
                        return 'pytest'
                    elif 'jest' in str(unit_test_info).lower():
                        return 'Jest'
                    elif 'junit' in str(unit_test_info).lower():
                        return 'JUnit'
                    elif 'mocha' in str(unit_test_info).lower():
                        return 'Mocha'
        
        # Fallback based on language
        if repo_info.language:
            language = repo_info.language.lower()
            if language in ['python', 'py']:
                return 'pytest'
            elif language in ['javascript', 'js', 'typescript', 'ts']:
                return 'Jest'
            elif language in ['java']:
                return 'JUnit'
            elif language in ['c#', 'csharp']:
                return 'NUnit'
        
        return 'Standard Testing Framework'
    
    def _detect_test_language(
        self,
        repo_info: RepositoryInfo,
        analysis_result: AnalysisResult
    ) -> str:
        """Detect the programming language for tests."""
        
        if repo_info.language:
            return repo_info.language
        
        # Fallback to common languages
        return 'Python'
