"""
Output formatting module for user stories and analysis results.
"""

import json
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .types import AnalysisResult, OutputFormat, TestDocumentation
from .mermaid_validator import MermaidValidator


class OutputFormatter:
    """Formats analysis results into different output formats."""
    
    def __init__(self, output_format: OutputFormat = OutputFormat.TEXT):
        self.output_format = output_format
        self.mermaid_validator = MermaidValidator()
    
    def format_analysis_result(self, result: AnalysisResult) -> str:
        """Format the analysis result according to the specified output format."""
        if self.output_format == OutputFormat.JSON:
            return self._format_json(result)
        elif self.output_format == OutputFormat.MARKDOWN:
            return self._format_markdown(result)
        else:
            return self._format_text(result)
    
    def _format_text(self, result: AnalysisResult) -> str:
        """Format the result as plain text."""
        lines = []
        
        # Header
        lines.append(f"📋 User Stories for {result.repository.full_name}")
        lines.append("=" * (len(result.repository.full_name) + 20))
        lines.append("")
        
        # Repository summary
        lines.append("📊 Repository Summary:")
        lines.append(f"  • Description: {result.repository.description or 'No description available'}")
        lines.append(f"  • Language: {result.repository.language or 'Not specified'}")
        lines.append(f"  • Stars: {result.repository.stars}")
        lines.append(f"  • Forks: {result.repository.forks}")
        lines.append(f"  • Topics: {', '.join(result.repository.topics) if result.repository.topics else 'None'}")
        lines.append(f"  • License: {result.repository.license or 'Not specified'}")
        lines.append(f"  • Analysis Date: {result.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if result.focus_area:
            lines.append(f"  • Focus Area: {result.focus_area}")
        
        lines.append("")
        
        # Technology stack
        if result.tech_stack:
            lines.append("🔧 Technology Stack:")
            for tech in result.tech_stack:
                lines.append(f"  • {tech}")
            lines.append("")
        
        # Key features
        if result.key_features:
            lines.append("🎯 Key Features Identified:")
            for feature in result.key_features[:5]:  # Limit to top 5
                lines.append(f"  • {feature}")
            lines.append("")
        
        # Target users
        if result.target_users:
            lines.append("👥 Target Users:")
            for user in result.target_users:
                lines.append(f"  • {user}")
            lines.append("")
        
        # User stories
        lines.append("📝 User Stories:")
        lines.append("")
        
        for i, story in enumerate(result.user_stories, 1):
            lines.append(f"🎯 Story {i}: {story.title}")
            lines.append(f"   {story.description}")
            lines.append("")
            
            if story.acceptance_criteria:
                lines.append("   Acceptance Criteria:")
                for criterion in story.acceptance_criteria:
                    lines.append(f"   • {criterion.description}")
                lines.append("")
            
            lines.append(f"   Priority: {story.priority.value}")
            lines.append(f"   Effort: {story.effort.value}")
            
            if story.tags:
                lines.append(f"   Tags: {', '.join(story.tags)}")
            
            lines.append("")
            lines.append("-" * 60)
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_json(self, result: AnalysisResult) -> str:
        """Format the result as JSON."""
        output_data = {
            "repository": {
                "fullName": result.repository.full_name,
                "description": result.repository.description,
                "language": result.repository.language,
                "stars": result.repository.stars,
                "forks": result.repository.forks,
                "topics": result.repository.topics,
                "license": result.repository.license,
                "createdAt": result.repository.created_at.isoformat(),
                "updatedAt": result.repository.updated_at.isoformat()
            },
            "analysis": {
                "date": result.analysis_date.isoformat(),
                "focusArea": result.focus_area,
                "techStack": result.tech_stack,
                "keyFeatures": result.key_features,
                "targetUsers": result.target_users
            },
            "userStories": []
        }
        
        # Add comprehensive analysis data if available
        if result.system_architecture:
            output_data["systemArchitecture"] = {
                "systemDiagram": result.system_architecture.system_diagram,
                "apiFlowDiagram": result.system_architecture.api_flow_diagram,
                "dataFlowDiagram": result.system_architecture.data_flow_diagram,
                "componentDiagram": result.system_architecture.component_diagram,
                "deploymentDiagram": result.system_architecture.deployment_diagram
            }
        
        if result.api_analysis:
            output_data["apiAnalysis"] = {
                "endpoints": result.api_analysis.endpoints,
                "externalServices": result.api_analysis.external_services,
                "authenticationMethods": result.api_analysis.authentication_methods,
                "dataFormats": result.api_analysis.data_formats,
                "websocketEvents": result.api_analysis.websocket_events,
                "databaseSchemas": result.api_analysis.database_schemas
            }
        
        if result.technical_deep_dive:
            output_data["technicalDeepDive"] = {
                "technologyStack": result.technical_deep_dive.technology_stack,
                "buildSystem": result.technical_deep_dive.build_system,
                "testingFramework": result.technical_deep_dive.testing_framework,
                "ciCdPipeline": result.technical_deep_dive.ci_cd_pipeline,
                "deploymentStrategy": result.technical_deep_dive.deployment_strategy,
                "performanceOptimizations": result.technical_deep_dive.performance_optimizations,
                "securityFeatures": result.technical_deep_dive.security_features
            }
        
        if result.comprehensive_report:
            output_data["comprehensiveReport"] = result.comprehensive_report
        
        for story in result.user_stories:
            story_data = {
                "id": story.id,
                "title": story.title,
                "description": story.description,
                "acceptanceCriteria": [
                    criterion.description for criterion in story.acceptance_criteria
                ],
                "priority": story.priority.value,
                "effort": story.effort.value,
                "tags": story.tags,
                "createdAt": story.created_at.isoformat()
            }
            output_data["userStories"].append(story_data)
        
        return json.dumps(output_data, indent=2, ensure_ascii=False)
    
    def _format_markdown(self, result: AnalysisResult) -> str:
        """Format the result as Markdown."""
        lines = []
        
        # Check if this is a comprehensive analysis
        is_comprehensive = bool(result.system_architecture or result.api_analysis or result.technical_deep_dive)
        
        # Header
        if is_comprehensive:
            lines.append(f"# Comprehensive Technical Analysis: {result.repository.full_name}")
        else:
            lines.append(f"# User Stories for {result.repository.full_name}")
        lines.append("")
        
        # Repository summary
        lines.append("## Repository Overview")
        lines.append("")
        lines.append(f"**Repository:** {result.repository.full_name}  ")
        lines.append(f"**Description:** {result.repository.description or 'No description available'}  ")
        lines.append(f"**Language:** {result.repository.language or 'Not specified'}  ")
        lines.append(f"**Stars:** {result.repository.stars:,}  ")
        lines.append(f"**Forks:** {result.repository.forks:,}  ")
        lines.append(f"**Topics:** {', '.join(result.repository.topics) if result.repository.topics else 'None'}  ")
        lines.append(f"**License:** {result.repository.license or 'Not specified'}  ")
        lines.append(f"**Size:** {result.repository.size:,} KB  ")
        lines.append(f"**Analysis Date:** {result.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}  ")
        
        if result.focus_area:
            lines.append(f"**Focus Area:** {result.focus_area}  ")
        
        lines.append("")
        
        # System Architecture Section
        if result.system_architecture:
            lines.append("## 🏗️ System Architecture")
            lines.append("")
            lines.append("This section contains Mermaid diagrams that visualize the system architecture. ")
            lines.append("Copy the diagram code to [Mermaid Live](https://mermaid.live) to view the interactive diagrams.")
            lines.append("")
            
            if result.system_architecture.system_diagram:
                lines.append("### Overall System Architecture")
                lines.append("")
                lines.append("```mermaid")
                # Validate and fix the diagram before output
                validated_diagram, _ = self.mermaid_validator.validate_and_fix_diagram(result.system_architecture.system_diagram)
                lines.append(validated_diagram)
                lines.append("```")
                lines.append("")
            
            if result.system_architecture.api_flow_diagram:
                lines.append("### API Flow Diagram")
                lines.append("")
                lines.append("```mermaid")
                # Validate and fix the diagram before output
                validated_diagram, _ = self.mermaid_validator.validate_and_fix_diagram(result.system_architecture.api_flow_diagram)
                lines.append(validated_diagram)
                lines.append("```")
                lines.append("")
            
            if result.system_architecture.component_diagram:
                lines.append("### Component Architecture")
                lines.append("")
                lines.append("```mermaid")
                # Validate and fix the diagram before output
                validated_diagram, _ = self.mermaid_validator.validate_and_fix_diagram(result.system_architecture.component_diagram)
                lines.append(validated_diagram)
                lines.append("```")
                lines.append("")
            
            if result.system_architecture.data_flow_diagram:
                lines.append("### Data Flow Architecture")
                lines.append("")
                lines.append("```mermaid")
                # Validate and fix the diagram before output
                validated_diagram, _ = self.mermaid_validator.validate_and_fix_diagram(result.system_architecture.data_flow_diagram)
                lines.append(validated_diagram)
                lines.append("```")
                lines.append("")
        
        # API Analysis Section
        if result.api_analysis:
            lines.append("## 🌐 API & Integration Analysis")
            lines.append("")
            
            if result.api_analysis.endpoints:
                lines.append("### API Endpoints")
                lines.append("")
                for i, endpoint in enumerate(result.api_analysis.endpoints, 1):
                    if isinstance(endpoint, dict):
                        method = endpoint.get('method', 'GET')
                        path = endpoint.get('path', endpoint.get('name', 'Unknown'))
                        desc = endpoint.get('description', '')
                        lines.append(f"{i}. **{method}** `{path}`")
                        if desc:
                            lines.append(f"   - {desc}")
                    else:
                        lines.append(f"{i}. {endpoint}")
                lines.append("")
            
            if result.api_analysis.external_services:
                lines.append("### External Services & Integrations")
                lines.append("")
                for service in result.api_analysis.external_services:
                    lines.append(f"- {service}")
                lines.append("")
            
            if result.api_analysis.authentication_methods:
                lines.append("### Authentication Methods")
                lines.append("")
                for auth in result.api_analysis.authentication_methods:
                    lines.append(f"- {auth}")
                lines.append("")
            
            if result.api_analysis.websocket_events:
                lines.append("### Real-time Events (WebSocket)")
                lines.append("")
                for event in result.api_analysis.websocket_events:
                    lines.append(f"- {event}")
                lines.append("")
        
        # Technical Deep Dive Section
        if result.technical_deep_dive:
            lines.append("## 🔧 Technical Deep Dive")
            lines.append("")
            
            # Technology Stack
            tech_stack = result.technical_deep_dive.technology_stack
            if tech_stack:
                lines.append("### Technology Stack")
                lines.append("")
                for category, technologies in tech_stack.items():
                    if technologies:
                        lines.append(f"**{category.replace('_', ' ').title()}:**")
                        for tech in technologies:
                            lines.append(f"- {tech}")
                        lines.append("")
            
            # Build System
            if result.technical_deep_dive.build_system:
                lines.append("### Build System")
                lines.append("")
                build_info = result.technical_deep_dive.build_system
                for key, value in build_info.items():
                    if value:
                        lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
                lines.append("")
            
            # Performance Optimizations
            if result.technical_deep_dive.performance_optimizations:
                lines.append("### Performance Optimizations")
                lines.append("")
                for opt in result.technical_deep_dive.performance_optimizations:
                    lines.append(f"- {opt}")
                lines.append("")
            
            # Security Features
            if result.technical_deep_dive.security_features:
                lines.append("### Security Features")
                lines.append("")
                for security in result.technical_deep_dive.security_features:
                    lines.append(f"- {security}")
                lines.append("")
        
        # Comprehensive Technical Report
        if result.comprehensive_report:
            lines.append("## 📋 Technical Report")
            lines.append("")
            lines.append(result.comprehensive_report)
            lines.append("")
        
        # Show basic analysis only if no comprehensive analysis is available
        if not is_comprehensive:
            # Technology stack
            if result.tech_stack:
                lines.append("## Technology Stack")
                lines.append("")
                for tech in result.tech_stack:
                    lines.append(f"- {tech}")
                lines.append("")
            
            # Key features
            if result.key_features:
                lines.append("## Key Features Identified")
                lines.append("")
                for feature in result.key_features[:5]:  # Limit to top 5
                    lines.append(f"- {feature}")
                lines.append("")
            
            # Target users
            if result.target_users:
                lines.append("## Target Users")
                lines.append("")
                for user in result.target_users:
                    lines.append(f"- {user}")
                lines.append("")
        
        # User stories
        lines.append("## User Stories")
        lines.append("")
        
        for i, story in enumerate(result.user_stories, 1):
            lines.append(f"### Story {i}: {story.title}")
            lines.append("")
            
            # Format the user story description
            if "As a" in story.description and "I want" in story.description and "So that" in story.description:
                parts = story.description.split("I want")
                if len(parts) == 2:
                    user_part = parts[0].replace("As a", "").strip()
                    want_benefit = parts[1].split("So that")
                    if len(want_benefit) == 2:
                        want_part = want_benefit[0].strip()
                        benefit_part = want_benefit[1].strip()
                        
                        lines.append(f"**As a** {user_part}  ")
                        lines.append(f"**I want to** {want_part}  ")
                        lines.append(f"**So that** {benefit_part}")
                        lines.append("")
                    else:
                        lines.append(f"**Description:** {story.description}")
                        lines.append("")
                else:
                    lines.append(f"**Description:** {story.description}")
                    lines.append("")
            else:
                lines.append(f"**Description:** {story.description}")
                lines.append("")
            
            # Acceptance criteria
            if story.acceptance_criteria:
                lines.append("#### Acceptance Criteria")
                lines.append("")
                for criterion in story.acceptance_criteria:
                    lines.append(f"- {criterion.description}")
                lines.append("")
            
            # Metadata
            lines.append(f"**Priority:** {story.priority.value}  ")
            lines.append(f"**Effort:** {story.effort.value}  ")
            
            if story.tags:
                lines.append(f"**Tags:** {', '.join(story.tags)}  ")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_to_file(self, result: AnalysisResult, file_path: Path) -> None:
        """Save the formatted result to a file."""
        try:
            content = self.format_analysis_result(result)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            raise IOError(f"Failed to save output to file {file_path}: {e}")
    
    def format_test_documentation(self, test_doc: TestDocumentation) -> str:
        """Format test documentation according to the specified output format."""
        if self.output_format == OutputFormat.JSON:
            return self._format_test_documentation_json(test_doc)
        elif self.output_format == OutputFormat.MARKDOWN:
            return self._format_test_documentation_markdown(test_doc)
        else:
            return self._format_test_documentation_text(test_doc)
    
    def _format_test_documentation_text(self, test_doc: TestDocumentation) -> str:
        """Format test documentation as plain text."""
        lines = []
        
        # Header
        lines.append(f"🧪 Test Documentation for {test_doc.repository_name}")
        lines.append("=" * (len(test_doc.repository_name) + 30))
        lines.append("")
        
        # Summary
        lines.append("📊 Test Summary:")
        lines.append(f"  • Total Test Cases: {test_doc.total_test_cases}")
        lines.append(f"  • Total Test Suites: {len(test_doc.test_suites)}")
        lines.append(f"  • Analysis Date: {test_doc.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Test coverage
        if test_doc.test_coverage:
            lines.append("📈 Test Coverage by Type:")
            for test_type, coverage in test_doc.test_coverage.items():
                lines.append(f"  • {test_type.title()}: {coverage:.1f}%")
            lines.append("")
        
        # Test suites
        lines.append("🧪 Test Suites:")
        lines.append("")
        
        for i, suite in enumerate(test_doc.test_suites, 1):
            lines.append(f"📋 Suite {i}: {suite.name}")
            lines.append(f"   Description: {suite.description}")
            lines.append(f"   Test Type: {suite.test_type.value.title()}")
            lines.append(f"   Total Tests: {suite.total_tests}")
            lines.append(f"   User Stories: {', '.join(map(str, suite.user_story_ids))}")
            lines.append("")
            
            # Test cases
            lines.append("   Test Cases:")
            for j, test_case in enumerate(suite.test_cases, 1):
                lines.append(f"     {j}. {test_case.title}")
                lines.append(f"        Description: {test_case.description}")
                lines.append(f"        Type: {test_case.test_type.value.title()}")
                lines.append(f"        Priority: {test_case.priority.value}")
                lines.append(f"        User Story: {test_case.user_story_title}")
                lines.append("")
                
                if test_case.test_steps:
                    lines.append("        Test Steps:")
                    for step in test_case.test_steps:
                        lines.append(f"          • {step}")
                    lines.append("")
                
                if test_case.expected_results:
                    lines.append("        Expected Results:")
                    for result in test_case.expected_results:
                        lines.append(f"          • {result}")
                    lines.append("")
                
                if test_case.prerequisites:
                    lines.append("        Prerequisites:")
                    for prereq in test_case.prerequisites:
                        lines.append(f"          • {prereq}")
                    lines.append("")
                
                if test_case.tags:
                    lines.append(f"        Tags: {', '.join(test_case.tags)}")
                
                lines.append("        " + "-" * 40)
                lines.append("")
            
            lines.append("   " + "-" * 60)
            lines.append("")
        
        # Testing strategy
        if test_doc.testing_strategy:
            lines.append("📋 Testing Strategy:")
            lines.append("")
            lines.append(test_doc.testing_strategy)
            lines.append("")
        
        # Environment requirements
        if test_doc.test_environment_requirements:
            lines.append("🔧 Test Environment Requirements:")
            for req in test_doc.test_environment_requirements:
                lines.append(f"  • {req}")
            lines.append("")
        
        # Execution instructions
        if test_doc.execution_instructions:
            lines.append("▶️ Execution Instructions:")
            lines.append("")
            lines.append(test_doc.execution_instructions)
            lines.append("")
        
        # Maintenance notes
        if test_doc.maintenance_notes:
            lines.append("🔧 Maintenance Notes:")
            lines.append("")
            lines.append(test_doc.maintenance_notes)
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_test_documentation_markdown(self, test_doc: TestDocumentation) -> str:
        """Format test documentation as markdown."""
        lines = []
        
        # Header
        lines.append(f"# 🧪 Test Documentation for {test_doc.repository_name}")
        lines.append("")
        lines.append(f"**Analysis Date:** {test_doc.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Summary
        lines.append("## 📊 Test Summary")
        lines.append("")
        lines.append(f"- **Total Test Cases:** {test_doc.total_test_cases}")
        lines.append(f"- **Total Test Suites:** {len(test_doc.test_suites)}")
        lines.append("")
        
        # Test coverage
        if test_doc.test_coverage:
            lines.append("## 📈 Test Coverage by Type")
            lines.append("")
            for test_type, coverage in test_doc.test_coverage.items():
                lines.append(f"- **{test_type.title()}:** {coverage:.1f}%")
            lines.append("")
        
        # Test suites
        lines.append("## 🧪 Test Suites")
        lines.append("")
        
        for i, suite in enumerate(test_doc.test_suites, 1):
            lines.append(f"### 📋 Suite {i}: {suite.name}")
            lines.append("")
            lines.append(f"**Description:** {suite.description}")
            lines.append(f"**Test Type:** {suite.test_type.value.title()}")
            lines.append(f"**Total Tests:** {suite.total_tests}")
            lines.append(f"**User Stories:** {', '.join(map(str, suite.user_story_ids))}")
            lines.append("")
            
            # Test cases
            lines.append("#### Test Cases")
            lines.append("")
            
            for j, test_case in enumerate(suite.test_cases, 1):
                lines.append(f"**{j}. {test_case.title}**")
                lines.append("")
                lines.append(f"*{test_case.description}*")
                lines.append("")
                lines.append(f"- **Type:** {test_case.test_type.value.title()}")
                lines.append(f"- **Priority:** {test_case.priority.value}")
                lines.append(f"- **User Story:** {test_case.user_story_title}")
                lines.append("")
                
                if test_case.test_steps:
                    lines.append("**Test Steps:**")
                    lines.append("")
                    for step in test_case.test_steps:
                        lines.append(f"1. {step}")
                    lines.append("")
                
                if test_case.expected_results:
                    lines.append("**Expected Results:**")
                    lines.append("")
                    for result in test_case.expected_results:
                        lines.append(f"- {result}")
                    lines.append("")
                
                if test_case.prerequisites:
                    lines.append("**Prerequisites:**")
                    lines.append("")
                    for prereq in test_case.prerequisites:
                        lines.append(f"- {prereq}")
                    lines.append("")
                
                if test_case.tags:
                    lines.append(f"**Tags:** {', '.join(test_case.tags)}")
                
                lines.append("---")
                lines.append("")
        
        # Testing strategy
        if test_doc.testing_strategy:
            lines.append("## 📋 Testing Strategy")
            lines.append("")
            lines.append(test_doc.testing_strategy)
            lines.append("")
        
        # Environment requirements
        if test_doc.test_environment_requirements:
            lines.append("## 🔧 Test Environment Requirements")
            lines.append("")
            for req in test_doc.test_environment_requirements:
                lines.append(f"- {req}")
            lines.append("")
        
        # Execution instructions
        if test_doc.execution_instructions:
            lines.append("## ▶️ Execution Instructions")
            lines.append("")
            lines.append(test_doc.execution_instructions)
            lines.append("")
        
        # Maintenance notes
        if test_doc.maintenance_notes:
            lines.append("## 🔧 Maintenance Notes")
            lines.append("")
            lines.append(test_doc.maintenance_notes)
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_test_documentation_json(self, test_doc: TestDocumentation) -> str:
        """Format test documentation as JSON."""
        import json
        
        # Convert to dictionary
        test_data = {
            "repositoryName": test_doc.repository_name,
            "analysisDate": test_doc.analysis_date.isoformat(),
            "totalTestCases": test_doc.total_test_cases,
            "testSuites": [],
            "testCoverage": test_doc.test_coverage,
            "testingStrategy": test_doc.testing_strategy,
            "testEnvironmentRequirements": test_doc.test_environment_requirements,
            "executionInstructions": test_doc.execution_instructions,
            "maintenanceNotes": test_doc.maintenance_notes,
            "metadata": test_doc.metadata
        }
        
        # Convert test suites
        for suite in test_doc.test_suites:
            suite_data = {
                "id": suite.id,
                "name": suite.name,
                "description": suite.description,
                "testType": suite.test_type.value,
                "userStoryIds": suite.user_story_ids,
                "totalTests": suite.total_tests,
                "createdAt": suite.created_at.isoformat(),
                "testCases": []
            }
            
            # Convert test cases
            for test_case in suite.test_cases:
                test_case_data = {
                    "id": test_case.id,
                    "title": test_case.title,
                    "description": test_case.description,
                    "testType": test_case.test_type.value,
                    "priority": test_case.priority.value,
                    "userStoryId": test_case.user_story_id,
                    "userStoryTitle": test_case.user_story_title,
                    "testSteps": test_case.test_steps,
                    "expectedResults": test_case.expected_results,
                    "prerequisites": test_case.prerequisites,
                    "testData": test_case.test_data,
                    "tags": test_case.tags,
                    "createdAt": test_case.created_at.isoformat()
                }
                suite_data["testCases"].append(test_case_data)
            
            test_data["testSuites"].append(suite_data)
        
        return json.dumps(test_data, indent=2, ensure_ascii=False)
    
    def save_test_documentation_to_file(self, test_doc: TestDocumentation, file_path: Path) -> None:
        """Save the formatted test documentation to a file."""
        try:
            content = self.format_test_documentation(test_doc)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            raise IOError(f"Failed to save test documentation to file {file_path}: {e}")
    
    def get_file_extension(self) -> str:
        """Get the appropriate file extension for the current output format."""
        if self.output_format == OutputFormat.JSON:
            return ".json"
        elif self.output_format == OutputFormat.MARKDOWN:
            return ".md"
        else:
            return ".txt"
    
    def get_mime_type(self) -> str:
        """Get the MIME type for the current output format."""
        if self.output_format == OutputFormat.JSON:
            return "application/json"
        elif self.output_format == OutputFormat.MARKDOWN:
            return "text/markdown"
        else:
            return "text/plain"
