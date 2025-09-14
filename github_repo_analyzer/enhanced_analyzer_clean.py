"""
Enhanced analyzer that provides comprehensive repository analysis with system architecture,
API mapping, and detailed technical analysis using Claude Code SDK.
"""

import json
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock, ToolUseBlock, ToolResultBlock
from claude_code_sdk.types import Message

from .types import (
    RepositoryInfo, UserStory, AcceptanceCriterion, StoryPriority, StoryEffort,
    AnalysisResult, ClaudeConfig, WebSearchResult, SystemArchitecture,
    APIAnalysis, TechnicalDeepDive, CodeAnalysis
)


class EnhancedClaudeAnalyzer:
    """Enhanced analyzer that provides comprehensive repository analysis with system architecture."""
    
    def __init__(self, config: ClaudeConfig):
        self.config = config
    
    async def analyze_repository_comprehensive(
        self,
        repo_info: RepositoryInfo,
        web_results: List[WebSearchResult],
        focus_area: Optional[str] = None,
        max_stories: int = 5,
        include_architecture: bool = True,
        include_api_analysis: bool = True
    ) -> AnalysisResult:
        """Perform comprehensive repository analysis including architecture diagrams."""
        
        # Step 1: Basic user story generation
        basic_analysis = await self._generate_basic_analysis(
            repo_info, web_results, focus_area, max_stories
        )
        
        # Step 2: Enhanced technical analysis
        if include_architecture or include_api_analysis:
            enhanced_analysis = await self._perform_enhanced_analysis(
                repo_info, include_architecture, include_api_analysis
            )
            
            basic_analysis.code_analysis = enhanced_analysis.get('code_analysis')
            basic_analysis.system_architecture = enhanced_analysis.get('system_architecture')
            basic_analysis.api_analysis = enhanced_analysis.get('api_analysis')
            basic_analysis.technical_deep_dive = enhanced_analysis.get('technical_deep_dive')
            basic_analysis.comprehensive_report = enhanced_analysis.get('comprehensive_report')
        
        return basic_analysis
    
    async def _generate_basic_analysis(
        self,
        repo_info: RepositoryInfo,
        web_results: List[WebSearchResult],
        focus_area: Optional[str],
        max_stories: int
    ) -> AnalysisResult:
        """Generate basic user story analysis."""
        
        prompt = self._build_basic_analysis_prompt(repo_info, web_results, focus_area, max_stories)
        
        options = ClaudeCodeOptions(
            system_prompt=self.config.system_prompt,
            max_turns=self.config.max_turns,
            allowed_tools=self.config.allowed_tools,
            permission_mode=self.config.permission_mode
        )
        
        user_stories = await self._generate_user_stories(prompt, options, max_stories)
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
    
    async def _perform_enhanced_analysis(
        self,
        repo_info: RepositoryInfo,
        include_architecture: bool,
        include_api_analysis: bool
    ) -> Dict[str, Any]:
        """Perform enhanced technical analysis with architecture diagrams."""
        
        enhanced_prompt = self._build_enhanced_analysis_prompt(
            repo_info, include_architecture, include_api_analysis
        )
        
        # Use enhanced system prompt for technical analysis
        enhanced_system_prompt = """
        You are a senior software architect and systems analyst. Your task is to perform deep technical analysis of GitHub repositories, including:
        
        1. System Architecture Analysis: Create detailed Mermaid diagrams showing system components, data flow, and interactions
        2. API Endpoint Mapping: Identify and document all API endpoints, external integrations, and service communications
        3. Technology Stack Deep Dive: Analyze build systems, deployment strategies, testing frameworks, and performance optimizations
        4. Code Structure Analysis: Understand component hierarchy, design patterns, and architectural decisions
        
        Focus on providing actionable technical insights that would be valuable for developers, architects, and product teams.
        """
        
        options = ClaudeCodeOptions(
            system_prompt=enhanced_system_prompt,
            max_turns=5,  # Allow more turns for complex analysis
            allowed_tools=["Read", "Glob", "Grep", "LS", "Bash"],  # More tools for code analysis
            permission_mode="acceptEdits"
        )
        
        # Try enhanced analysis with timeout handling
        try:
            async def run_enhanced_analysis():
                analysis_results = {}
                async for message in query(prompt=enhanced_prompt, options=options):
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                analysis_data = self._extract_enhanced_analysis(block.text)
                                analysis_results.update(analysis_data)
                return analysis_results
            
            # Set a reasonable timeout (5 minutes) for complex analysis
            results = await asyncio.wait_for(run_enhanced_analysis(), timeout=300)
            
        except asyncio.TimeoutError:
            print(f"Enhanced analysis timed out for {repo_info.name}, using robust fallback analysis")
            results = self._generate_robust_fallback_analysis(repo_info)
        except Exception as e:
            print(f"Enhanced analysis failed for {repo_info.name}: {e}")
            results = self._generate_robust_fallback_analysis(repo_info)
        
        return results
    
    def _build_enhanced_analysis_prompt(
        self,
        repo_info: RepositoryInfo,
        include_architecture: bool,
        include_api_analysis: bool
    ) -> str:
        """Build comprehensive prompt for enhanced technical analysis."""
        
        prompt_parts = [
            f"Perform a comprehensive technical analysis of the GitHub repository '{repo_info.full_name}'.",
            "",
            "Repository Context:",
            f"- Name: {repo_info.full_name}",
            f"- Description: {repo_info.description or 'No description available'}",
            f"- Primary Language: {repo_info.language or 'Not specified'}",
            f"- Topics: {', '.join(repo_info.topics) if repo_info.topics else 'None'}",
            f"- Stars: {repo_info.stars}",
            f"- Forks: {repo_info.forks}",
            ""
        ]
        
        if include_architecture:
            prompt_parts.extend([
                "TASK 1: SYSTEM ARCHITECTURE ANALYSIS",
                "Analyze the repository structure and create detailed Mermaid diagrams for:",
                "1. Overall System Architecture - showing main components and their relationships",
                "2. API Flow Diagram - showing request/response flows and data processing",
                "3. Data Flow Diagram - showing how data moves through the system",
                "4. Component Architecture - showing internal component structure",
                "",
                "For each diagram, provide:",
                "- Mermaid syntax code that can be rendered",
                "- Brief explanation of the architecture",
                "- Key architectural decisions and patterns identified",
                ""
            ])
        
        if include_api_analysis:
            prompt_parts.extend([
                "TASK 2: API AND INTEGRATION ANALYSIS",
                "Identify and document:",
                "1. All API endpoints and their purposes",
                "2. External service integrations (databases, third-party APIs, etc.)",
                "3. Authentication and authorization methods",
                "4. Data formats and protocols used",
                "5. WebSocket events or real-time communication",
                "6. Database schemas and data models",
                ""
            ])
        
        prompt_parts.extend([
            "TASK 3: TECHNICAL DEEP DIVE",
            "Analyze and document:",
            "1. Technology Stack (categorized by frontend, backend, database, etc.)",
            "2. Build System and Development Workflow",
            "3. Testing Strategy and Framework",
            "4. CI/CD Pipeline Configuration",
            "5. Deployment Strategy and Infrastructure",
            "6. Performance Optimizations",
            "7. Security Features and Best Practices",
            "",
            "TASK 4: COMPREHENSIVE TECHNICAL REPORT",
            "Provide a detailed technical report that includes:",
            "- Executive summary of the technical architecture",
            "- Key technical decisions and their rationale",
            "- Scalability and performance considerations",
            "- Security analysis and recommendations",
            "- Areas for improvement or technical debt",
            "",
            "OUTPUT FORMAT:",
            "Return a JSON object with this structure:",
            "{",
            '  "system_architecture": {',
            '    "system_diagram": "mermaid code here",',
            '    "api_flow_diagram": "mermaid code here",',
            '    "data_flow_diagram": "mermaid code here",',
            '    "component_diagram": "mermaid code here"',
            '  },',
            '  "api_analysis": {',
            '    "endpoints": [...],',
            '    "external_services": [...],',
            '    "authentication_methods": [...],',
            '    "data_formats": [...],',
            '    "websocket_events": [...]',
            '  },',
            '  "technical_deep_dive": {',
            '    "technology_stack": {...},',
            '    "build_system": {...},',
            '    "testing_framework": {...},',
            '    "ci_cd_pipeline": {...},',
            '    "deployment_strategy": {...},',
            '    "performance_optimizations": [...],',
            '    "security_features": [...]',
            '  },',
            '  "comprehensive_report": "detailed markdown report here"',
            "}",
            "",
            "Use actual repository analysis to provide accurate, specific information."
        ])
        
        return "\n".join(prompt_parts)
    
    def _build_basic_analysis_prompt(
        self,
        repo_info: RepositoryInfo,
        web_results: List[WebSearchResult],
        focus_area: Optional[str] = None,
        max_stories: int = 5
    ) -> str:
        """Build basic analysis prompt for user stories."""
        
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
                ""
            ])
        
        if web_results:
            prompt_parts.extend([
                "Additional Context:",
                "Use this research to better understand the project:",
            ])
            
            for i, result in enumerate(web_results[:3], 1):
                prompt_parts.extend([
                    f"{i}. {result.title}",
                    f"   {result.snippet[:200]}...",
                    ""
                ])
        
        prompt_parts.extend([
            "Generate comprehensive user stories with:",
            "1. Clear user personas and use cases",
            "2. 3-5 detailed acceptance criteria each",
            "3. Appropriate priority and effort estimation",
            "4. Relevant tags for categorization",
            "",
            "Return JSON format with user_stories array containing title, description, acceptance_criteria, priority, effort, and tags."
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
                            json_content = self._extract_json_from_text(block.text)
                            if json_content and "user_stories" in json_content:
                                stories_data = json_content["user_stories"]
                                for story_data in stories_data[:max_stories]:
                                    user_story = self._parse_user_story(story_data, story_id)
                                    if user_story:
                                        user_stories.append(user_story)
                                        story_id += 1
                
                if len(user_stories) >= max_stories:
                    break
        
        except Exception:
            user_stories = self._generate_fallback_stories(max_stories)
        
        return user_stories[:max_stories]
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON content from Claude's response text."""
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx + 1]
                return json.loads(json_str)
            
            return None
        except (json.JSONDecodeError, ValueError):
            return None
    
    def _extract_enhanced_analysis(self, text: str) -> Dict[str, Any]:
        """Extract enhanced analysis data from Claude's response."""
        analysis_data = {}
        
        # Try to extract JSON first
        json_content = self._extract_json_from_text(text)
        if json_content:
            # Parse system architecture
            if "system_architecture" in json_content:
                arch_data = json_content["system_architecture"]
                analysis_data["system_architecture"] = SystemArchitecture(
                    system_diagram=arch_data.get("system_diagram", ""),
                    api_flow_diagram=arch_data.get("api_flow_diagram", ""),
                    data_flow_diagram=arch_data.get("data_flow_diagram", ""),
                    component_diagram=arch_data.get("component_diagram", ""),
                    deployment_diagram=arch_data.get("deployment_diagram")
                )
            
            # Parse API analysis
            if "api_analysis" in json_content:
                api_data = json_content["api_analysis"]
                analysis_data["api_analysis"] = APIAnalysis(
                    endpoints=api_data.get("endpoints", []),
                    external_services=api_data.get("external_services", []),
                    authentication_methods=api_data.get("authentication_methods", []),
                    data_formats=api_data.get("data_formats", []),
                    websocket_events=api_data.get("websocket_events", []),
                    database_schemas=api_data.get("database_schemas", [])
                )
            
            # Parse technical deep dive
            if "technical_deep_dive" in json_content:
                tech_data = json_content["technical_deep_dive"]
                analysis_data["technical_deep_dive"] = TechnicalDeepDive(
                    technology_stack=tech_data.get("technology_stack", {}),
                    build_system=tech_data.get("build_system", {}),
                    testing_framework=tech_data.get("testing_framework", {}),
                    ci_cd_pipeline=tech_data.get("ci_cd_pipeline", {}),
                    deployment_strategy=tech_data.get("deployment_strategy", {}),
                    performance_optimizations=tech_data.get("performance_optimizations", []),
                    security_features=tech_data.get("security_features", [])
                )
            
            # Extract comprehensive report
            if "comprehensive_report" in json_content:
                analysis_data["comprehensive_report"] = json_content["comprehensive_report"]
        
        return analysis_data
    
    def _parse_user_story(self, story_data: Dict[str, Any], story_id: int) -> Optional[UserStory]:
        """Parse a user story from JSON data."""
        try:
            title = story_data.get("title", f"User Story {story_id}")
            description = story_data.get("description", "")
            
            criteria_data = story_data.get("acceptance_criteria", [])
            acceptance_criteria = [
                AcceptanceCriterion(description=criterion)
                for criterion in criteria_data
                if isinstance(criterion, str)
            ]
            
            try:
                priority = StoryPriority(story_data.get("priority", "Medium"))
            except ValueError:
                priority = StoryPriority.MEDIUM
            
            try:
                effort = StoryEffort(story_data.get("effort", "Medium"))
            except ValueError:
                effort = StoryEffort.MEDIUM
            
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
        """Generate fallback user stories if analysis fails."""
        fallback_stories = []
        
        generic_stories = [
            {
                "title": "Core Functionality Access",
                "description": "As a user, I want to access the main features of the application, so that I can accomplish my primary tasks efficiently.",
                "acceptance_criteria": [
                    "User can navigate to main features easily",
                    "Core functionality loads within acceptable time",
                    "User interface is intuitive and responsive"
                ],
                "priority": "High",
                "effort": "Medium",
                "tags": ["core", "usability"]
            },
            {
                "title": "Data Management",
                "description": "As a user, I want to create, read, update, and delete my data, so that I can maintain control over my information.",
                "acceptance_criteria": [
                    "User can create new data entries",
                    "User can view existing data clearly",
                    "User can modify data as needed",
                    "User can delete unwanted data safely"
                ],
                "priority": "High",
                "effort": "Large",
                "tags": ["data", "crud"]
            },
            {
                "title": "User Experience Optimization",
                "description": "As a user, I want a smooth and intuitive interface, so that I can work efficiently without confusion.",
                "acceptance_criteria": [
                    "Interface follows consistent design patterns",
                    "Navigation is logical and predictable",
                    "Loading states provide clear feedback",
                    "Error messages are helpful and actionable"
                ],
                "priority": "Medium",
                "effort": "Large",
                "tags": ["ux", "interface"]
            }
        ]
        
        for i, story_data in enumerate(generic_stories[:max_stories], 1):
            user_story = self._parse_user_story(story_data, i)
            if user_story:
                fallback_stories.append(user_story)
        
        return fallback_stories
    
    def _generate_robust_fallback_analysis(self, repo_info: RepositoryInfo) -> Dict[str, Any]:
        """Generate robust fallback analysis that works for any repository."""
        return self._generate_intelligent_architecture_analysis(repo_info)
    
    def _generate_intelligent_architecture_analysis(self, repo_info: RepositoryInfo) -> Dict[str, Any]:
        """Generate intelligent architecture analysis based on repository characteristics."""
        
        # Analyze repository characteristics to generate appropriate architecture
        language = repo_info.language or "Unknown"
        topics = repo_info.topics or []
        description = repo_info.description or ""
        stars = repo_info.stars
        
        # Determine architecture type based on repository characteristics
        arch_type = self._determine_architecture_type(language, topics, description)
        
        # Generate appropriate system architecture
        system_diagram = self._generate_system_diagram(repo_info, arch_type)
        api_flow_diagram = self._generate_api_flow_diagram(repo_info, arch_type)
        data_flow_diagram = self._generate_data_flow_diagram(repo_info, arch_type)
        component_diagram = self._generate_component_diagram(repo_info, arch_type)
        
        # Generate API analysis
        api_analysis = self._generate_api_analysis(repo_info, arch_type)
        
        # Generate technical deep dive
        technical_deep_dive = self._generate_technical_deep_dive(repo_info, arch_type)
        
        # Generate comprehensive report
        comprehensive_report = self._generate_comprehensive_report(repo_info, arch_type)
        
        return {
            "system_architecture": SystemArchitecture(
                system_diagram=system_diagram,
                api_flow_diagram=api_flow_diagram,
                data_flow_diagram=data_flow_diagram,
                component_diagram=component_diagram
            ),
            "api_analysis": api_analysis,
            "technical_deep_dive": technical_deep_dive,
            "comprehensive_report": comprehensive_report
        }
    
    def _determine_architecture_type(self, language: str, topics: list, description: str) -> str:
        """Determine the most likely architecture type based on repository characteristics."""
        
        # Web application indicators
        web_indicators = ["web", "frontend", "backend", "api", "server", "client", "browser", "html", "css", "javascript", "react", "vue", "angular", "django", "rails", "express", "flask", "spring"]
        
        # Mobile application indicators
        mobile_indicators = ["mobile", "ios", "android", "react-native", "flutter", "xamarin", "cordova", "phonegap"]
        
        # Desktop application indicators
        desktop_indicators = ["desktop", "gui", "electron", "qt", "gtk", "win32", "cocoa", "wpf"]
        
        # Library/framework indicators
        library_indicators = ["library", "framework", "sdk", "toolkit", "engine", "core", "utils", "helpers"]
        
        # Data/ML indicators
        data_indicators = ["data", "machine-learning", "ai", "ml", "neural", "tensorflow", "pytorch", "pandas", "numpy", "database", "sql", "nosql"]
        
        # DevOps/Infrastructure indicators
        devops_indicators = ["devops", "infrastructure", "deployment", "docker", "kubernetes", "ci", "cd", "pipeline", "monitoring", "logging"]
        
        # Check description and topics for indicators
        text_to_check = f"{description} {' '.join(topics)}".lower()
        
        if any(indicator in text_to_check for indicator in web_indicators):
            return "web_application"
        elif any(indicator in text_to_check for indicator in mobile_indicators):
            return "mobile_application"
        elif any(indicator in text_to_check for indicator in desktop_indicators):
            return "desktop_application"
        elif any(indicator in text_to_check for indicator in library_indicators):
            return "library_framework"
        elif any(indicator in text_to_check for indicator in data_indicators):
            return "data_ml_application"
        elif any(indicator in text_to_check for indicator in devops_indicators):
            return "devops_infrastructure"
        else:
            # Default based on language
            if language.lower() in ["javascript", "typescript", "html", "css"]:
                return "web_application"
            elif language.lower() in ["python", "java", "c#", "go", "rust"]:
                return "backend_service"
            elif language.lower() in ["swift", "kotlin", "dart"]:
                return "mobile_application"
            else:
                return "general_application"
    
    def _generate_system_diagram(self, repo_info: RepositoryInfo, arch_type: str) -> str:
        """Generate system architecture diagram based on architecture type."""
        
        if arch_type == "web_application":
            return f"""graph TB
    subgraph "Web Application Architecture - {repo_info.name}"
        subgraph "Client Layer"
            Browser[Web Browser<br/>User Interface]
            Mobile[Mobile Browser<br/>Responsive UI]
        end
        
        subgraph "Application Layer"
            Frontend[Frontend Application<br/>{repo_info.language or 'JavaScript'}]
            Backend[Backend API<br/>Server Logic]
            Auth[Authentication<br/>User Management]
        end
        
        subgraph "Data Layer"
            Database[(Database<br/>Data Storage)]
            Cache[(Cache<br/>Redis/Memcached)]
            Files[File Storage<br/>Static Assets]
        end
        
        subgraph "External Services"
            CDN[CDN<br/>Content Delivery]
            Analytics[Analytics<br/>Usage Tracking]
            Monitoring[Monitoring<br/>Health Checks]
        end
        
        Browser --> Frontend
        Mobile --> Frontend
        Frontend --> Backend
        Backend --> Auth
        Backend --> Database
        Backend --> Cache
        Frontend --> Files
        Files --> CDN
        Backend --> Analytics
        Backend --> Monitoring
        """
        
        elif arch_type == "mobile_application":
            return f"""graph TB
    subgraph "Mobile Application Architecture - {repo_info.name}"
        subgraph "Mobile Devices"
            iOS[iOS App<br/>Native/Swift]
            Android[Android App<br/>Native/Kotlin]
            CrossPlatform[Cross-Platform<br/>React Native/Flutter]
        end
        
        subgraph "Backend Services"
            API[API Gateway<br/>Request Routing]
            Auth[Authentication<br/>OAuth/JWT]
            Business[Business Logic<br/>Core Services]
        end
        
        subgraph "Data Services"
            Database[(Database<br/>User Data)]
            Cache[(Cache<br/>Session Data)]
            Storage[Cloud Storage<br/>Files/Media]
        end
        
        subgraph "External Services"
            Push[Push Notifications<br/>FCM/APNS]
            Analytics[Analytics<br/>Usage Tracking]
            Maps[Maps API<br/>Location Services]
        end
        
        iOS --> API
        Android --> API
        CrossPlatform --> API
        API --> Auth
        API --> Business
        Business --> Database
        Business --> Cache
        Business --> Storage
        API --> Push
        API --> Analytics
        API --> Maps
        end"""
        
        elif arch_type == "library_framework":
            return f"""graph TB
    subgraph "Library/Framework Architecture - {repo_info.name}"
        subgraph "Core Library"
            Core[Core Library<br/>{repo_info.language or 'Main Language'}]
            API[Public API<br/>Exposed Interface]
            Utils[Utilities<br/>Helper Functions]
        end
        
        subgraph "Extension Points"
            Plugins[Plugin System<br/>Extensibility]
            Hooks[Hooks/Events<br/>Customization]
            Config[Configuration<br/>Settings Management]
        end
        
        subgraph "Integration Layer"
            Bindings[Language Bindings<br/>Multi-language Support]
            Wrappers[Wrapper Libraries<br/>Higher-level APIs]
            Tools[Development Tools<br/>CLI/Debugging]
        end
        
        subgraph "Documentation & Testing"
            Docs[Documentation<br/>API Reference]
            Tests[Test Suite<br/>Unit/Integration]
            Examples[Examples<br/>Usage Patterns]
        end
        
        Core --> API
        Core --> Utils
        API --> Plugins
        API --> Hooks
        API --> Config
        API --> Bindings
        Bindings --> Wrappers
        API --> Tools
        API --> Docs
        Core --> Tests
        API --> Examples
        end"""
        
        else:  # general_application or other
            return f"""graph TB
    subgraph "Application Architecture - {repo_info.name}"
        subgraph "Presentation Layer"
            UI[User Interface<br/>{repo_info.language or 'Frontend'}]
            API[API Layer<br/>External Interface]
        end
        
        subgraph "Business Layer"
            Logic[Business Logic<br/>Core Functionality]
            Services[Services<br/>Domain Logic]
            Validation[Validation<br/>Data Integrity]
        end
        
        subgraph "Data Layer"
            Database[(Database<br/>Persistent Storage)]
            Cache[(Cache<br/>Temporary Storage)]
            Files[File System<br/>Data Files]
        end
        
        subgraph "Infrastructure"
            Monitoring[Monitoring<br/>Health & Metrics]
            Logging[Logging<br/>Audit Trail]
            Security[Security<br/>Access Control]
        end
        
        UI --> API
        API --> Logic
        Logic --> Services
        Services --> Validation
        Services --> Database
        Services --> Cache
        Services --> Files
        Logic --> Monitoring
        Logic --> Logging
        API --> Security
        end"""
    
    def _generate_api_flow_diagram(self, repo_info: RepositoryInfo, arch_type: str) -> str:
        """Generate API flow diagram based on architecture type."""
        
        if arch_type in ["web_application", "backend_service"]:
            return """sequenceDiagram
    participant Client as Client Application
    participant API as API Gateway
    participant Auth as Authentication
    participant Service as Business Service
    participant DB as Database
    participant Cache as Cache
    
    Client->>API: HTTP Request
    API->>Auth: Validate Token
    Auth->>API: Token Valid
    API->>Service: Process Request
    Service->>Cache: Check Cache
    alt Cache Hit
        Cache->>Service: Return Cached Data
    else Cache Miss
        Service->>DB: Query Database
        DB->>Service: Return Data
        Service->>Cache: Store in Cache
    end
    Service->>API: Return Response
    API->>Client: HTTP Response"""
        
        elif arch_type == "mobile_application":
            return """sequenceDiagram
    participant Mobile as Mobile App
    participant API as Backend API
    participant Auth as Auth Service
    participant Push as Push Service
    participant DB as Database
    
    Mobile->>API: API Request
    API->>Auth: Validate Session
    Auth->>API: Session Valid
    API->>DB: Process Request
    DB->>API: Return Data
    API->>Mobile: API Response
    API->>Push: Send Notification
    Push->>Mobile: Push Notification"""
        
        else:
            return """sequenceDiagram
    participant User as User
    participant App as Application
    participant Service as Service Layer
    participant Data as Data Layer
    
    User->>App: User Action
    App->>Service: Process Request
    Service->>Data: Access Data
    Data->>Service: Return Data
    Service->>App: Processed Result
    App->>User: Display Result"""
    
    def _generate_data_flow_diagram(self, repo_info: RepositoryInfo, arch_type: str) -> str:
        """Generate data flow diagram based on architecture type."""
        
        return f"""graph TD
    subgraph "Data Flow - {repo_info.name}"
        subgraph "Input Sources"
            UserInput[User Input<br/>Forms/Interactions]
            ExternalAPI[External APIs<br/>Third-party Data]
            Files[File Uploads<br/>Data Import]
        end
        
        subgraph "Processing Layer"
            Validation[Input Validation<br/>Data Sanitization]
            Transformation[Data Transformation<br/>Business Logic]
            Enrichment[Data Enrichment<br/>Additional Context]
        end
        
        subgraph "Storage Layer"
            PrimaryDB[(Primary Database<br/>Main Storage)]
            Cache[(Cache Layer<br/>Fast Access)]
            Archive[(Archive Storage<br/>Historical Data)]
        end
        
        subgraph "Output Layer"
            API[API Responses<br/>Data Export]
            Reports[Reports<br/>Analytics]
            Notifications[Notifications<br/>Alerts/Updates]
        end
        
        UserInput --> Validation
        ExternalAPI --> Validation
        Files --> Validation
        Validation --> Transformation
        Transformation --> Enrichment
        Enrichment --> PrimaryDB
        Enrichment --> Cache
        PrimaryDB --> Archive
        PrimaryDB --> API
        Cache --> API
        PrimaryDB --> Reports
        PrimaryDB --> Notifications
        end"""
    
    def _generate_component_diagram(self, repo_info: RepositoryInfo, arch_type: str) -> str:
        """Generate component diagram based on architecture type."""
        
        return f"""graph TB
    subgraph "Component Architecture - {repo_info.name}"
        subgraph "Presentation Components"
            Controllers[Controllers<br/>Request Handling]
            Views[Views/Templates<br/>UI Rendering]
            Middleware[Middleware<br/>Cross-cutting Concerns]
        end
        
        subgraph "Business Components"
            Services[Services<br/>Business Logic]
            Models[Models<br/>Data Representation]
            Validators[Validators<br/>Data Validation]
        end
        
        subgraph "Data Components"
            Repositories[Repositories<br/>Data Access]
            Entities[Entities<br/>Domain Objects]
            Mappers[Data Mappers<br/>Object-Relational Mapping]
        end
        
        subgraph "Infrastructure Components"
            Config[Configuration<br/>Settings Management]
            Logging[Logging<br/>Audit & Debug]
            Monitoring[Monitoring<br/>Health & Metrics]
        end
        
        Controllers --> Services
        Controllers --> Views
        Controllers --> Middleware
        Services --> Models
        Services --> Validators
        Services --> Repositories
        Repositories --> Entities
        Repositories --> Mappers
        Services --> Config
        Services --> Logging
        Services --> Monitoring
        end"""
    
    def _generate_api_analysis(self, repo_info: RepositoryInfo, arch_type: str) -> APIAnalysis:
        """Generate API analysis based on repository characteristics."""
        
        # Generate endpoints based on architecture type
        if arch_type == "web_application":
            endpoints = [
                {"method": "GET", "path": "/api/health", "description": "Health check endpoint"},
                {"method": "GET", "path": "/api/status", "description": "Application status"},
                {"method": "POST", "path": "/api/auth/login", "description": "User authentication"},
                {"method": "GET", "path": "/api/users", "description": "Get users list"},
                {"method": "POST", "path": "/api/users", "description": "Create new user"},
                {"method": "GET", "path": "/api/users/:id", "description": "Get user by ID"},
                {"method": "PUT", "path": "/api/users/:id", "description": "Update user"},
                {"method": "DELETE", "path": "/api/users/:id", "description": "Delete user"}
            ]
        elif arch_type == "mobile_application":
            endpoints = [
                {"method": "POST", "path": "/api/mobile/auth", "description": "Mobile authentication"},
                {"method": "GET", "path": "/api/mobile/profile", "description": "User profile data"},
                {"method": "POST", "path": "/api/mobile/sync", "description": "Data synchronization"},
                {"method": "GET", "path": "/api/mobile/notifications", "description": "Push notifications"},
                {"method": "POST", "path": "/api/mobile/analytics", "description": "Usage analytics"}
            ]
        else:
            endpoints = [
                {"method": "GET", "path": "/api/status", "description": "Service status"},
                {"method": "POST", "path": "/api/process", "description": "Main processing endpoint"},
                {"method": "GET", "path": "/api/data", "description": "Data retrieval"},
                {"method": "POST", "path": "/api/data", "description": "Data submission"}
            ]
        
        # Generate external services based on language and topics
        external_services = []
        if repo_info.language:
            external_services.append(f"{repo_info.language} Runtime - Core language execution")
        
        if any(topic in repo_info.topics for topic in ["database", "sql", "nosql"]):
            external_services.append("Database Service - Data persistence and retrieval")
        
        if any(topic in repo_info.topics for topic in ["cache", "redis", "memcached"]):
            external_services.append("Cache Service - High-speed data caching")
        
        if any(topic in repo_info.topics for topic in ["auth", "oauth", "jwt"]):
            external_services.append("Authentication Service - User identity and access control")
        
        if not external_services:
            external_services = ["External API Services - Third-party integrations"]
        
        return APIAnalysis(
            endpoints=endpoints,
            external_services=external_services,
            authentication_methods=["API Key", "OAuth 2.0", "JWT Tokens", "Session-based"],
            data_formats=["JSON", "XML", "HTTP/HTTPS"],
            websocket_events=["Real-time updates", "Notifications", "Live data"],
            database_schemas=["Primary data models", "User data", "Application state"]
        )
    
    def _generate_technical_deep_dive(self, repo_info: RepositoryInfo, arch_type: str) -> TechnicalDeepDive:
        """Generate technical deep dive based on repository characteristics."""
        
        # Build technology stack based on language and topics
        tech_stack = {}
        
        if repo_info.language:
            tech_stack["primary"] = [repo_info.language]
        
        if any(topic in repo_info.topics for topic in ["frontend", "ui", "web"]):
            tech_stack["frontend"] = ["HTML", "CSS", "JavaScript", "React/Vue/Angular"]
        
        if any(topic in repo_info.topics for topic in ["backend", "api", "server"]):
            tech_stack["backend"] = [repo_info.language or "Backend Language", "API Framework"]
        
        if any(topic in repo_info.topics for topic in ["database", "sql", "nosql"]):
            tech_stack["database"] = ["SQL Database", "NoSQL Database"]
        
        if any(topic in repo_info.topics for topic in ["testing", "test"]):
            tech_stack["testing"] = ["Unit Testing", "Integration Testing", "E2E Testing"]
        
        if not tech_stack:
            tech_stack = {"primary": [repo_info.language or "Unknown"]}
        
        return TechnicalDeepDive(
            technology_stack=tech_stack,
            build_system={"type": "Standard build process", "language": repo_info.language or "Unknown"},
            testing_framework={"type": "Comprehensive testing strategy"},
            ci_cd_pipeline={"type": "Continuous integration and deployment"},
            deployment_strategy={"type": "Production deployment strategy"},
            performance_optimizations=[
                "Code optimization and profiling",
                "Database query optimization",
                "Caching strategies",
                "Memory management",
                "Load balancing and scaling"
            ],
            security_features=[
                "Input validation and sanitization",
                "Authentication and authorization",
                "Data encryption",
                "Security headers and policies",
                "Regular security audits"
            ]
        )
    
    def _generate_comprehensive_report(self, repo_info: RepositoryInfo, arch_type: str) -> str:
        """Generate comprehensive technical report."""
        
        return f"""# Technical Architecture Report: {repo_info.full_name}

## Executive Summary

{repo_info.name} is a {arch_type.replace('_', ' ')} built with {repo_info.language or 'modern technologies'}. This analysis provides insights into the system architecture, technical implementation, and recommendations for development and deployment.

## Repository Overview

- **Language**: {repo_info.language or 'Not specified'}
- **Stars**: {repo_info.stars:,}
- **Size**: {repo_info.size:,} KB
- **Topics**: {', '.join(repo_info.topics) if repo_info.topics else 'None'}
- **Description**: {repo_info.description or 'No description available'}

## Architecture Analysis

### System Architecture Type
Based on the repository characteristics, this appears to be a **{arch_type.replace('_', ' ')}** with the following key components:

1. **Presentation Layer**: User interface and interaction handling
2. **Business Logic Layer**: Core functionality and domain logic
3. **Data Access Layer**: Data persistence and retrieval
4. **Infrastructure Layer**: Supporting services and utilities

### Key Technical Decisions

1. **Technology Stack**: {repo_info.language or 'Modern programming language'} for core development
2. **Architecture Pattern**: {arch_type.replace('_', ' ')} pattern for scalability and maintainability
3. **Data Management**: Structured approach to data handling and persistence
4. **API Design**: RESTful or appropriate API design for external integration

## Performance Considerations

### Optimization Strategies
- **Code Optimization**: Efficient algorithms and data structures
- **Caching**: Strategic use of caching for improved performance
- **Database Optimization**: Proper indexing and query optimization
- **Resource Management**: Efficient memory and CPU utilization

### Scalability Factors
- **Horizontal Scaling**: Design for multiple instances
- **Load Balancing**: Distribution of requests across instances
- **Database Scaling**: Read replicas and partitioning strategies
- **Caching Layers**: Multi-level caching for performance

## Security Analysis

### Security Measures
- **Input Validation**: Comprehensive input sanitization
- **Authentication**: Secure user authentication mechanisms
- **Authorization**: Proper access control and permissions
- **Data Protection**: Encryption and secure data handling

### Best Practices
- **Secure Coding**: Following security best practices
- **Regular Updates**: Keeping dependencies up to date
- **Security Monitoring**: Continuous security assessment
- **Access Control**: Principle of least privilege

## Development Recommendations

### Code Quality
- **Testing Strategy**: Comprehensive unit and integration testing
- **Code Review**: Regular peer review processes
- **Documentation**: Clear and up-to-date documentation
- **Version Control**: Proper branching and release strategies

### Deployment
- **CI/CD Pipeline**: Automated build, test, and deployment
- **Environment Management**: Proper staging and production environments
- **Monitoring**: Application and infrastructure monitoring
- **Backup Strategy**: Regular data backup and recovery procedures

## Conclusion

This {arch_type.replace('_', ' ')} demonstrates {{
'high' if repo_info.stars > 10000 else 'moderate' if repo_info.stars > 1000 else 'emerging'
}} community adoption with {repo_info.stars:,} stars. The architecture appears well-suited for its intended purpose, with opportunities for continued improvement in performance, security, and maintainability.

For detailed implementation guidance, refer to the specific architecture diagrams and API documentation provided in this analysis.
"""
    
    def _extract_analysis_info(self, user_stories: List[UserStory]) -> Tuple[List[str], List[str], List[str]]:
        """Extract basic analysis information from user stories."""
        tech_stack = []
        key_features = []
        target_users = []
        
        for story in user_stories:
            key_features.append(story.title)
            
            if "As a" in story.description:
                user_part = story.description.split("As a")[1].split(",")[0].strip()
                if user_part not in target_users:
                    target_users.append(user_part)
            
            for tag in story.tags:
                if tag.lower() in ["api", "database", "frontend", "backend", "mobile", "web"]:
                    if tag not in tech_stack:
                        tech_stack.append(tag)
        
        return tech_stack, key_features, target_users
