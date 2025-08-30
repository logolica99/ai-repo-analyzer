"""
Claude Code SDK integration for analyzing repositories and generating user stories.
"""

import json
import anyio
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock, ToolUseBlock, ToolResultBlock
from claude_code_sdk.types import Message

from .types import (
    RepositoryInfo, UserStory, AcceptanceCriterion, StoryPriority, StoryEffort,
    AnalysisResult, ClaudeConfig, WebSearchResult
)


class ClaudeAnalyzer:
    """Uses Claude Code SDK to analyze repositories and generate user stories."""
    
    def __init__(self, config: ClaudeConfig):
        self.config = config
    
    async def analyze_repository(
        self,
        repo_info: RepositoryInfo,
        web_results: List[WebSearchResult],
        focus_area: Optional[str] = None,
        max_stories: int = 5
    ) -> AnalysisResult:
        """Analyze a repository and generate user stories using Claude."""
        
        # Prepare the analysis prompt
        prompt = self._build_analysis_prompt(repo_info, web_results, focus_area, max_stories)
        
        # Configure Claude options
        options = ClaudeCodeOptions(
            system_prompt=self.config.system_prompt,
            max_turns=self.config.max_turns,
            allowed_tools=self.config.allowed_tools,
            permission_mode=self.config.permission_mode
        )
        
        # Generate user stories
        user_stories = await self._generate_user_stories(prompt, options, max_stories)
        
        # Extract additional analysis information
        tech_stack, key_features, target_users = self._extract_analysis_info(user_stories)
        
        return AnalysisResult(
            repository=repo_info,
            user_stories=user_stories,
            analysis_date=datetime.now(),
            focus_area=focus_area,
            tech_stack=tech_stack,
            key_features=key_features,
            target_users=target_users
        )
    
    def _build_analysis_prompt(
        self,
        repo_info: RepositoryInfo,
        web_results: List[WebSearchResult],
        focus_area: Optional[str] = None,
        max_stories: int = 5
    ) -> str:
        """Build a comprehensive prompt for Claude analysis."""
        
        prompt_parts = [
            f"Analyze the GitHub repository '{repo_info.full_name}' and generate {max_stories} comprehensive user stories.",
            "",
            "Repository Information:",
            f"- Name: {repo_info.full_name}",
            f"- Description: {repo_info.description or 'No description available'}",
            f"- Primary Language: {repo_info.language or 'Not specified'}",
            f"- Topics: {', '.join(repo_info.topics) if repo_info.topics else 'None'}",
            f"- Stars: {repo_info.stars}",
            f"- Forks: {repo_info.forks}",
            f"- License: {repo_info.license or 'Not specified'}",
            f"- Created: {repo_info.created_at.strftime('%Y-%m-%d')}",
            f"- Last Updated: {repo_info.updated_at.strftime('%Y-%m-%d')}",
            ""
        ]
        
        if repo_info.readme_content:
            prompt_parts.extend([
                "README Content:",
                repo_info.readme_content[:2000] + "..." if len(repo_info.readme_content) > 2000 else repo_info.readme_content,
                ""
            ])
        
        if focus_area:
            prompt_parts.extend([
                f"Focus Area: {focus_area}",
                "Generate user stories that specifically address this focus area.",
                ""
            ])
        
        if web_results:
            prompt_parts.extend([
                "Additional Research Context:",
                "Use this information to better understand the project context and user needs:"
            ])
            
            for i, result in enumerate(web_results[:5], 1):
                prompt_parts.extend([
                    f"{i}. {result.title}",
                    f"   URL: {result.url}",
                    f"   Context: {result.snippet[:300]}...",
                    ""
                ])
        
        prompt_parts.extend([
            "Requirements for User Stories:",
            "1. Each user story should follow the format: 'The user [user type], is able to [feature/functionality], So that [benefit/value]'",
            "2. Include 3-5 acceptance criteria for each story",
            "3. Assign appropriate priority (Low, Medium, High, Critical) and effort (Small, Medium, Large, Extra Large)",
            "4. Focus on actionable, implementable features",
            "5. Consider the technology stack and project context",
            "6. Make stories specific to this repository's purpose and domain",
            "",
            "Output Format:",
            "Return a JSON object with the following structure:",
            "{",
            '  "user_stories": [',
            '    {',
            '      "title": "Story title",',
            '      "description": "As a [user type], I want [feature], So that [benefit]",',
            '      "acceptance_criteria": ["criterion 1", "criterion 2", "criterion 3"],',
            '      "priority": "High",',
            '      "effort": "Medium",',
            '      "tags": ["tag1", "tag2"]',
            '    }',
            '  ]',
            "}",
            "",
            "Ensure the JSON is valid and properly formatted."
        ])
        
        return "\n".join(prompt_parts)
    
    async def _generate_user_stories(
        self,
        prompt: str,
        options: ClaudeCodeOptions,
        max_stories: int
    ) -> List[UserStory]:
        """Generate user stories using Claude Code SDK."""
        
        user_stories = []
        story_id = 1
        
        try:
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Try to extract JSON from the text
                            json_content = self._extract_json_from_text(block.text)
                            if json_content and "user_stories" in json_content:
                                stories_data = json_content["user_stories"]
                                for story_data in stories_data[:max_stories]:
                                    try:
                                        user_story = self._parse_user_story(story_data, story_id)
                                        if user_story:
                                            user_stories.append(user_story)
                                            story_id += 1
                                    except Exception as e:
                                        # Continue with other stories if one fails to parse
                                        continue
                        
                        elif isinstance(block, ToolUseBlock):
                            # Handle tool usage if needed
                            pass
                        
                        elif isinstance(block, ToolResultBlock):
                            # Handle tool results if needed
                            pass
                
                # Break if we have enough stories
                if len(user_stories) >= max_stories:
                    break
        
        except Exception as e:
            # If Claude fails, generate fallback stories
            user_stories = self._generate_fallback_stories(max_stories)
        
        return user_stories[:max_stories]
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON content from Claude's response text."""
        try:
            # Look for JSON content in the text
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx + 1]
                return json.loads(json_str)
            
            return None
        except (json.JSONDecodeError, ValueError):
            return None
    
    def _parse_user_story(self, story_data: Dict[str, Any], story_id: int) -> Optional[UserStory]:
        """Parse a user story from the JSON data."""
        try:
            # Extract basic information
            title = story_data.get("title", f"User Story {story_id}")
            description = story_data.get("description", "")
            
            # Parse acceptance criteria
            criteria_data = story_data.get("acceptance_criteria", [])
            acceptance_criteria = [
                AcceptanceCriterion(description=criterion)
                for criterion in criteria_data
                if isinstance(criterion, str)
            ]
            
            # Parse priority and effort
            priority_str = story_data.get("priority", "Medium")
            effort_str = story_data.get("effort", "Medium")
            
            try:
                priority = StoryPriority(priority_str)
            except ValueError:
                priority = StoryPriority.MEDIUM
            
            try:
                effort = StoryEffort(effort_str)
            except ValueError:
                effort = StoryEffort.MEDIUM
            
            # Extract tags
            tags = story_data.get("tags", [])
            if not isinstance(tags, list):
                tags = []
            
            return UserStory(
                id=story_id,
                title=title,
                description=description,
                acceptance_criteria=acceptance_criteria,
                priority=priority,
                effort=effort,
                tags=tags
            )
            
        except Exception:
            return None
    
    def _generate_fallback_stories(self, max_stories: int) -> List[UserStory]:
        """Generate fallback user stories if Claude analysis fails."""
        fallback_stories = []
        
        # Generic fallback stories
        generic_stories = [
            {
                "title": "User Authentication",
                "description": "As a user, I want to securely log in to the application, so that I can access my personalized content and features.",
                "priority": "High",
                "effort": "Medium"
            },
            {
                "title": "Data Management",
                "description": "As a user, I want to create, read, update, and delete my data, so that I can manage my information effectively.",
                "priority": "High",
                "effort": "Medium"
            },
            {
                "title": "User Interface",
                "description": "As a user, I want an intuitive and responsive user interface, so that I can easily navigate and use the application.",
                "priority": "Medium",
                "effort": "Large"
            },
            {
                "title": "Performance Optimization",
                "description": "As a user, I want the application to load quickly and respond promptly, so that I can work efficiently without delays.",
                "priority": "Medium",
                "effort": "Large"
            },
            {
                "title": "Error Handling",
                "description": "As a user, I want clear error messages and graceful error handling, so that I understand what went wrong and can recover easily.",
                "priority": "Low",
                "effort": "Medium"
            }
        ]
        
        for i, story_data in enumerate(generic_stories[:max_stories], 1):
            try:
                user_story = self._parse_user_story(story_data, i)
                if user_story:
                    fallback_stories.append(user_story)
            except Exception:
                continue
        
        return fallback_stories
    
    def _extract_analysis_info(self, user_stories: List[UserStory]) -> tuple[List[str], List[str], List[str]]:
        """Extract technology stack, key features, and target users from user stories."""
        tech_stack = []
        key_features = []
        target_users = []
        
        for story in user_stories:
            # Extract key features from story titles
            key_features.append(story.title)
            
            # Extract target users from descriptions
            if "As a" in story.description:
                user_part = story.description.split("As a")[1].split(",")[0].strip()
                if user_part not in target_users:
                    target_users.append(user_part)
            
            # Extract tags that might indicate technology
            for tag in story.tags:
                if tag.lower() in ["api", "database", "frontend", "backend", "mobile", "web"]:
                    if tag not in tech_stack:
                        tech_stack.append(tag)
        
        return tech_stack, key_features, target_users
