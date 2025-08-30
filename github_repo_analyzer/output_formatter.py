"""
Output formatting module for user stories and analysis results.
"""

import json
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .types import AnalysisResult, OutputFormat


class OutputFormatter:
    """Formats analysis results into different output formats."""
    
    def __init__(self, output_format: OutputFormat = OutputFormat.TEXT):
        self.output_format = output_format
    
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
                "full_name": result.repository.full_name,
                "description": result.repository.description,
                "language": result.repository.language,
                "stars": result.repository.stars,
                "forks": result.repository.forks,
                "topics": result.repository.topics,
                "license": result.repository.license,
                "created_at": result.repository.created_at.isoformat(),
                "updated_at": result.repository.updated_at.isoformat()
            },
            "analysis": {
                "date": result.analysis_date.isoformat(),
                "focus_area": result.focus_area,
                "tech_stack": result.tech_stack,
                "key_features": result.key_features,
                "target_users": result.target_users
            },
            "user_stories": []
        }
        
        # Add comprehensive analysis data if available
        if result.system_architecture:
            output_data["system_architecture"] = {
                "system_diagram": result.system_architecture.system_diagram,
                "api_flow_diagram": result.system_architecture.api_flow_diagram,
                "data_flow_diagram": result.system_architecture.data_flow_diagram,
                "component_diagram": result.system_architecture.component_diagram,
                "deployment_diagram": result.system_architecture.deployment_diagram
            }
        
        if result.api_analysis:
            output_data["api_analysis"] = {
                "endpoints": result.api_analysis.endpoints,
                "external_services": result.api_analysis.external_services,
                "authentication_methods": result.api_analysis.authentication_methods,
                "data_formats": result.api_analysis.data_formats,
                "websocket_events": result.api_analysis.websocket_events,
                "database_schemas": result.api_analysis.database_schemas
            }
        
        if result.technical_deep_dive:
            output_data["technical_deep_dive"] = {
                "technology_stack": result.technical_deep_dive.technology_stack,
                "build_system": result.technical_deep_dive.build_system,
                "testing_framework": result.technical_deep_dive.testing_framework,
                "ci_cd_pipeline": result.technical_deep_dive.ci_cd_pipeline,
                "deployment_strategy": result.technical_deep_dive.deployment_strategy,
                "performance_optimizations": result.technical_deep_dive.performance_optimizations,
                "security_features": result.technical_deep_dive.security_features
            }
        
        if result.comprehensive_report:
            output_data["comprehensive_report"] = result.comprehensive_report
        
        for story in result.user_stories:
            story_data = {
                "id": story.id,
                "title": story.title,
                "description": story.description,
                "acceptance_criteria": [
                    criterion.description for criterion in story.acceptance_criteria
                ],
                "priority": story.priority.value,
                "effort": story.effort.value,
                "tags": story.tags,
                "created_at": story.created_at.isoformat()
            }
            output_data["user_stories"].append(story_data)
        
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
                lines.append(result.system_architecture.system_diagram)
                lines.append("```")
                lines.append("")
            
            if result.system_architecture.api_flow_diagram:
                lines.append("### API Flow Diagram")
                lines.append("")
                lines.append("```mermaid")
                lines.append(result.system_architecture.api_flow_diagram)
                lines.append("```")
                lines.append("")
            
            if result.system_architecture.component_diagram:
                lines.append("### Component Architecture")
                lines.append("")
                lines.append("```mermaid")
                lines.append(result.system_architecture.component_diagram)
                lines.append("```")
                lines.append("")
            
            if result.system_architecture.data_flow_diagram:
                lines.append("### Data Flow Architecture")
                lines.append("")
                lines.append("```mermaid")
                lines.append(result.system_architecture.data_flow_diagram)
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
