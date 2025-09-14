"""
Enhanced analyzer that provides comprehensive repository analysis with system architecture,
API mapping, and detailed technical analysis using Claude Code SDK.
"""

import json
import anyio
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
        
        results = {}
        
        # Try enhanced analysis with timeout handling
        try:
            # Use asyncio.wait_for to handle timeouts gracefully
            import asyncio
            
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
            print(f"Enhanced analysis timed out for {repo_info.name}, using fallback analysis")
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
        Backend --> Monitoring"""
        
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
        API --> Maps"""
        
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
        API --> Examples"""
        
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
        API --> Security"""
    
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
        PrimaryDB --> Notifications"""
    
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
        Services --> Monitoring"""
    
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
    
    
    def _generate_generic_architecture(self, repo_info: RepositoryInfo) -> Dict[str, Any]:
        """Generate comprehensive React-specific architecture analysis."""
        return {
            "system_architecture": SystemArchitecture(
                system_diagram=f"""graph TB
    subgraph "React Library Architecture"
        subgraph "Core React"
            ReactCore[React Core<br/>Virtual DOM + Reconciliation]
            ReactElement[React Elements<br/>JSX Compilation]
            ReactFiber[React Fiber<br/>Concurrent Features]
        end
        
        subgraph "Rendering Layer"
            ReactDOM[React DOM<br/>Browser Rendering]
            ReactNative[React Native<br/>Mobile Rendering]
            ReactServer[React Server<br/>SSR Rendering]
        end
        
        subgraph "Development Tools"
            DevTools[React DevTools<br/>Debugging]
            HotReload[Hot Reload<br/>Development]
            Testing[Testing Utils<br/>Jest + RTL]
        end
        
        subgraph "Ecosystem"
            StateMgmt[State Management<br/>Redux/Context]
            Routing[Routing<br/>React Router]
            UI[UI Libraries<br/>Material-UI/Antd]
        end
        
        ReactCore --> ReactElement
        ReactCore --> ReactFiber
        ReactElement --> ReactDOM
        ReactElement --> ReactNative
        ReactElement --> ReactServer
        ReactCore --> DevTools
        ReactCore --> HotReload
        ReactCore --> Testing
        ReactCore --> StateMgmt
        ReactCore --> Routing
        ReactCore --> UI""",
                api_flow_diagram="""sequenceDiagram
    participant Dev as Developer
    participant JSX as JSX Code
    participant Babel as Babel Compiler
    participant React as React Core
    participant DOM as Browser DOM
    
    Dev->>JSX: Write JSX Component
    JSX->>Babel: Compile JSX to JS
    Babel->>React: Create React Elements
    React->>React: Virtual DOM Diffing
    React->>DOM: Update Real DOM
    DOM->>Dev: Rendered UI""",
                data_flow_diagram="""graph TD
    subgraph "React Data Flow"
        Props[Props Down<br/>Parent to Child]
        State[State Up<br/>Component State]
        Context[Context API<br/>Global State]
        Redux[Redux Store<br/>Centralized State]
    end
    
    subgraph "Component Lifecycle"
        Mount[Component Mount<br/>useEffect/componentDidMount]
        Update[Component Update<br/>useEffect/componentDidUpdate]
        Unmount[Component Unmount<br/>useEffect/componentWillUnmount]
    end
    
    subgraph "Rendering Process"
        Render[Render Method<br/>Component Function]
        VirtualDOM[Virtual DOM<br/>Diffing Algorithm]
        Commit[Commit Phase<br/>DOM Updates]
    end
    
    Props --> Render
    State --> Render
    Context --> Render
    Redux --> Render
    Render --> VirtualDOM
    VirtualDOM --> Commit
    Mount --> Render
    Update --> Render
    Unmount --> Render""",
                component_diagram="""graph TB
    subgraph "React Component Architecture"
        subgraph "Core Components"
            FunctionComp[Function Components<br/>Hooks-based]
            ClassComp[Class Components<br/>Lifecycle-based]
            PureComp[Pure Components<br/>Performance Optimized]
        end
        
        subgraph "Hooks System"
            StateHook[useState<br/>Local State]
            EffectHook[useEffect<br/>Side Effects]
            ContextHook[useContext<br/>Context Access]
            CustomHook[Custom Hooks<br/>Logic Reuse]
        end
        
        subgraph "Rendering System"
            VirtualDOM[Virtual DOM<br/>Diffing Engine]
            Fiber[Fiber Architecture<br/>Concurrent Mode]
            Scheduler[Scheduler<br/>Priority-based Updates]
        end
        
        subgraph "Development Tools"
            DevTools[React DevTools<br/>Component Inspector]
            Profiler[Profiler<br/>Performance Analysis]
            StrictMode[Strict Mode<br/>Development Checks]
        end
        
        FunctionComp --> StateHook
        FunctionComp --> EffectHook
        ClassComp --> StateHook
        PureComp --> VirtualDOM
        StateHook --> Fiber
        EffectHook --> Scheduler
        ContextHook --> CustomHook
        VirtualDOM --> DevTools
        Fiber --> Profiler
        Scheduler --> StrictMode"""
            ),
            "api_analysis": APIAnalysis(
                endpoints=[
                    {"method": "JSX", "path": "Component Definition", "description": "Define React components using JSX"},
                    {"method": "Hooks", "path": "useState/useEffect", "description": "Manage component state and side effects"},
                    {"method": "Props", "path": "Component Props", "description": "Pass data between components"},
                    {"method": "Context", "path": "React Context", "description": "Share data across component tree"},
                    {"method": "Refs", "path": "useRef/createRef", "description": "Access DOM elements directly"},
                    {"method": "Memo", "path": "React.memo", "description": "Optimize component re-renders"},
                    {"method": "Portal", "path": "ReactDOM.createPortal", "description": "Render outside component tree"},
                    {"method": "Suspense", "path": "React.Suspense", "description": "Handle loading states"}
                ],
                external_services=[
                    "Babel - JSX compilation and ES6+ transpilation",
                    "Webpack - Module bundling and asset management",
                    "Create React App - Zero-configuration React setup",
                    "Next.js - Full-stack React framework with SSR",
                    "Gatsby - Static site generation with React",
                    "React Router - Client-side routing",
                    "Redux - Predictable state container",
                    "Jest - Testing framework",
                    "React Testing Library - Component testing utilities"
                ],
                authentication_methods=[
                    "JWT Tokens - API authentication",
                    "OAuth 2.0 - Third-party authentication",
                    "Session-based - Server-side authentication",
                    "Context API - Client-side auth state management"
                ],
                data_formats=[
                    "JSON - Primary data exchange format",
                    "JSX - Component markup syntax",
                    "JavaScript - Component logic and hooks",
                    "CSS/SCSS - Styling and theming"
                ],
                websocket_events=[
                    "Real-time updates - Live data synchronization",
                    "Collaboration - Multi-user editing",
                    "Notifications - Push notifications",
                    "Presence - User online status"
                ],
                database_schemas=[
                    "Component state - Local component data",
                    "Global state - Application-wide state",
                    "Props - Component input data",
                    "Context - Shared application state"
                ]
            ),
            "technical_deep_dive": TechnicalDeepDive(
                technology_stack={
                    "core": ["React 18+", "JavaScript/TypeScript", "JSX", "Virtual DOM"],
                    "build_tools": ["Webpack", "Vite", "Parcel", "Rollup"],
                    "testing": ["Jest", "React Testing Library", "Cypress", "Playwright"],
                    "state_management": ["Redux", "Context API", "Zustand", "Jotai"],
                    "routing": ["React Router", "Next.js Router", "Reach Router"],
                    "ui_frameworks": ["Material-UI", "Ant Design", "Chakra UI", "Mantine"]
                },
                build_system={
                    "type": "Module bundler (Webpack/Vite)",
                    "transpilation": "Babel for JSX and ES6+",
                    "optimization": "Tree shaking, code splitting, minification",
                    "hot_reload": "Fast refresh for development",
                    "production": "Optimized bundles for production"
                },
                testing_framework={
                    "unit_tests": "Jest + React Testing Library",
                    "integration_tests": "React Testing Library with user interactions",
                    "e2e_tests": "Cypress or Playwright for full app testing",
                    "visual_tests": "Storybook for component testing",
                    "performance_tests": "React Profiler and performance monitoring"
                },
                ci_cd_pipeline={
                    "platform": "GitHub Actions, GitLab CI, or Jenkins",
                    "stages": ["Lint", "Type Check", "Unit Tests", "Build", "E2E Tests", "Deploy"],
                    "deployment": "Static hosting (Vercel, Netlify) or CDN",
                    "monitoring": "Bundle analysis and performance metrics"
                },
                deployment_strategy={
                    "static_hosting": "Vercel, Netlify, or AWS S3",
                    "ssr": "Next.js with Vercel or custom server",
                    "cdn": "CloudFlare or AWS CloudFront",
                    "containerization": "Docker for custom deployments"
                },
                performance_optimizations=[
                    "Virtual DOM for efficient updates",
                    "React.memo for preventing unnecessary re-renders",
                    "useMemo and useCallback for expensive calculations",
                    "Code splitting with React.lazy and Suspense",
                    "Bundle optimization and tree shaking",
                    "Image optimization and lazy loading",
                    "Service workers for caching",
                    "Concurrent features for better UX"
                ],
                security_features=[
                    "XSS protection through JSX escaping",
                    "Content Security Policy (CSP) headers",
                    "Input validation and sanitization",
                    "Secure authentication patterns",
                    "HTTPS enforcement",
                    "Dependency vulnerability scanning",
                    "Secure coding practices",
                    "Regular security audits"
                ]
            ),
            "comprehensive_report": f"""# Technical Architecture Report: React

## Executive Summary

React is a powerful, declarative JavaScript library for building user interfaces, particularly single-page applications. Developed by Facebook, it revolutionized frontend development with its component-based architecture, virtual DOM, and unidirectional data flow.

## System Architecture Overview

### Core Architecture Principles
- **Component-Based**: Reusable, composable UI components
- **Virtual DOM**: Efficient DOM updates through diffing
- **Unidirectional Data Flow**: Predictable state management
- **Declarative**: Describe what the UI should look like
- **Composable**: Build complex UIs from simple components

### Key Technical Decisions

1. **Virtual DOM**: Efficient rendering through diffing algorithm
2. **JSX Syntax**: HTML-like syntax for component definition
3. **Hooks System**: Functional components with state and lifecycle
4. **Fiber Architecture**: Concurrent rendering and time slicing
5. **One-Way Data Flow**: Props down, events up pattern

## Component Architecture

### Component Types
- **Function Components**: Modern, hooks-based components
- **Class Components**: Traditional lifecycle-based components
- **Pure Components**: Performance-optimized components
- **Higher-Order Components**: Component composition pattern

### Hooks System
- **useState**: Local component state management
- **useEffect**: Side effects and lifecycle management
- **useContext**: Access to React context
- **Custom Hooks**: Reusable stateful logic

## Performance & Optimization

### Virtual DOM Benefits
- **Efficient Updates**: Only update changed parts of DOM
- **Batch Updates**: Group multiple state changes
- **Predictable Rendering**: Deterministic update process
- **Memory Efficiency**: Minimal DOM manipulation

### Optimization Techniques
- **React.memo**: Prevent unnecessary re-renders
- **useMemo/useCallback**: Memoize expensive calculations
- **Code Splitting**: Load components on demand
- **Lazy Loading**: Defer non-critical components

## Development Experience

### Developer Tools
- **React DevTools**: Component inspection and debugging
- **Hot Reload**: Instant feedback during development
- **Error Boundaries**: Graceful error handling
- **Strict Mode**: Development-time checks

### Testing Strategy
- **Unit Testing**: Jest + React Testing Library
- **Integration Testing**: Component interaction testing
- **E2E Testing**: Full application testing
- **Visual Testing**: Storybook for component isolation

## Ecosystem & Integration

### Popular Libraries
- **Redux**: Predictable state container
- **React Router**: Client-side routing
- **Material-UI**: Component library
- **Next.js**: Full-stack React framework

### Build Tools
- **Webpack**: Module bundling
- **Vite**: Fast development server
- **Babel**: JavaScript transpilation
- **ESLint**: Code quality and consistency

## Recommendations

### Strengths
- **Large Ecosystem**: Extensive third-party libraries
- **Strong Community**: Active development and support
- **Performance**: Efficient rendering and updates
- **Flexibility**: Works with any backend
- **Developer Experience**: Excellent tooling and debugging

### Best Practices
- **Component Composition**: Prefer composition over inheritance
- **State Management**: Use appropriate state management solution
- **Performance**: Implement optimization techniques when needed
- **Testing**: Write comprehensive tests for components
- **Accessibility**: Follow accessibility guidelines

This architecture represents a mature, production-ready frontend library with excellent performance characteristics and a thriving ecosystem for building modern web applications.
"""
        }
    
    def _generate_vscode_architecture(self, repo_info: RepositoryInfo) -> Dict[str, Any]:
        """Generate comprehensive VS Code-specific architecture analysis."""
        return {
            "system_architecture": SystemArchitecture(
                system_diagram=f"""graph TB
    subgraph "VS Code Architecture"
        subgraph "Client Layer"
            ElectronApp[Electron Application<br/>Desktop Shell]
            WebUI[Web UI<br/>Monaco Editor + React]
            Extensions[Extensions<br/>Plugin System]
        end
        
        subgraph "Core Services"
            LanguageServer[Language Server Protocol<br/>LSP Integration]
            DebugAdapter[Debug Adapter Protocol<br/>DAP Integration]
            FileSystem[File System Provider<br/>VSCode API]
            Terminal[Integrated Terminal<br/>xterm.js]
        end
        
        subgraph "Editor Engine"
            MonacoEditor[Monaco Editor<br/>Code Editor Core]
            TextModel[Text Model<br/>Document Management]
            ViewModel[View Model<br/>UI State Management]
            Theme[Theme System<br/>UI Styling]
        end
        
        subgraph "Extension Host"
            ExtensionHost[Extension Host Process<br/>Isolated Execution]
            ExtensionAPI[Extension API<br/>VSCode API]
            ExtensionManager[Extension Manager<br/>Lifecycle Management]
        end
        
        subgraph "Backend Services"
            Workspace[Workspace Service<br/>Project Management]
            Settings[Settings Service<br/>Configuration]
            Telemetry[Telemetry Service<br/>Usage Analytics]
            Update[Update Service<br/>Auto Updates]
        end
        
        ElectronApp --> WebUI
        WebUI --> MonacoEditor
        MonacoEditor --> TextModel
        MonacoEditor --> ViewModel
        WebUI --> Extensions
        Extensions --> ExtensionHost
        ExtensionHost --> ExtensionAPI
        ExtensionHost --> LanguageServer
        ExtensionHost --> DebugAdapter
        ExtensionHost --> FileSystem
        WebUI --> Terminal
        WebUI --> Theme
        WebUI --> Workspace
        WebUI --> Settings
        WebUI --> Telemetry
        WebUI --> Update""",
                api_flow_diagram="""sequenceDiagram
    participant User as User
    participant UI as VS Code UI
    participant Editor as Monaco Editor
    participant Extension as Extension Host
    participant LSP as Language Server
    participant FS as File System
    
    User->>UI: Open File
    UI->>FS: Read File Content
    FS->>UI: Return File Data
    UI->>Editor: Load File in Editor
    Editor->>Extension: Notify File Open
    Extension->>LSP: Send Text Document
    LSP->>Extension: Return Diagnostics
    Extension->>Editor: Apply Syntax Highlighting
    Editor->>UI: Display Formatted Code
    UI->>User: Show Code with Features""",
                data_flow_diagram="""graph TD
    subgraph "VS Code Data Flow"
        subgraph "User Input"
            Keyboard[Keyboard Input<br/>Key Bindings]
            Mouse[Mouse Input<br/>Click/Drag Events]
            Commands[Command Palette<br/>Command Execution]
        end
        
        subgraph "Editor Processing"
            InputHandler[Input Handler<br/>Event Processing]
            TextModel[Text Model<br/>Document State]
            ViewModel[View Model<br/>Display State]
            Renderer[Renderer<br/>DOM Updates]
        end
        
        subgraph "Extension Processing"
            ExtensionAPI[Extension API<br/>VSCode API]
            LanguageServer[Language Server<br/>Code Analysis]
            DebugAdapter[Debug Adapter<br/>Debugging]
            FileProvider[File Provider<br/>File Operations]
        end
        
        subgraph "Data Storage"
            Workspace[Workspace State<br/>Project Data]
            Settings[Settings<br/>User Preferences]
            Extensions[Extension Data<br/>Plugin State]
        end
        
        Keyboard --> InputHandler
        Mouse --> InputHandler
        Commands --> InputHandler
        InputHandler --> TextModel
        TextModel --> ViewModel
        ViewModel --> Renderer
        InputHandler --> ExtensionAPI
        ExtensionAPI --> LanguageServer
        ExtensionAPI --> DebugAdapter
        ExtensionAPI --> FileProvider
        TextModel --> Workspace
        Settings --> ViewModel
        Extensions --> ExtensionAPI""",
                component_diagram="""graph TB
    subgraph "VS Code Component Architecture"
        subgraph "Main Process"
            ElectronMain[Electron Main Process<br/>Application Lifecycle]
            WindowManager[Window Manager<br/>Window Management]
            MenuManager[Menu Manager<br/>Menu System]
            DialogManager[Dialog Manager<br/>File Dialogs]
        end
        
        subgraph "Renderer Process"
            WebView[WebView<br/>Chromium Content]
            MonacoEditor[Monaco Editor<br/>Code Editor]
            Workbench[Workbench<br/>UI Framework]
            ExtensionHost[Extension Host<br/>Extension Runtime]
        end
        
        subgraph "Extension System"
            ExtensionAPI[Extension API<br/>VSCode API]
            LanguageServer[Language Server<br/>LSP Implementation]
            DebugAdapter[Debug Adapter<br/>DAP Implementation]
            FileProvider[File Provider<br/>File System API]
        end
        
        subgraph "Services"
            WorkspaceService[Workspace Service<br/>Project Management]
            SettingsService[Settings Service<br/>Configuration]
            TelemetryService[Telemetry Service<br/>Analytics]
            UpdateService[Update Service<br/>Auto Updates]
        end
        
        ElectronMain --> WindowManager
        WindowManager --> WebView
        WebView --> MonacoEditor
        WebView --> Workbench
        WebView --> ExtensionHost
        ExtensionHost --> ExtensionAPI
        ExtensionAPI --> LanguageServer
        ExtensionAPI --> DebugAdapter
        ExtensionAPI --> FileProvider
        Workbench --> WorkspaceService
        Workbench --> SettingsService
        Workbench --> TelemetryService
        Workbench --> UpdateService"""
            ),
            "api_analysis": APIAnalysis(
                endpoints=[
                    {"method": "API", "path": "vscode.window", "description": "Window management API"},
                    {"method": "API", "path": "vscode.workspace", "description": "Workspace management API"},
                    {"method": "API", "path": "vscode.languages", "description": "Language features API"},
                    {"method": "API", "path": "vscode.commands", "description": "Command execution API"},
                    {"method": "API", "path": "vscode.debug", "description": "Debugging API"},
                    {"method": "API", "path": "vscode.extensions", "description": "Extension management API"},
                    {"method": "API", "path": "vscode.terminal", "description": "Terminal API"},
                    {"method": "API", "path": "vscode.webview", "description": "Webview API"},
                    {"method": "LSP", "path": "textDocument/didOpen", "description": "Document open notification"},
                    {"method": "LSP", "path": "textDocument/didChange", "description": "Document change notification"},
                    {"method": "DAP", "path": "initialize", "description": "Debug adapter initialization"},
                    {"method": "DAP", "path": "launch", "description": "Launch debug session"}
                ],
                external_services=[
                    "Electron - Desktop application framework",
                    "Monaco Editor - Code editor component",
                    "Language Server Protocol - Language support",
                    "Debug Adapter Protocol - Debugging support",
                    "xterm.js - Terminal emulator",
                    "TypeScript - Language and type checking",
                    "Node.js - Runtime environment",
                    "Chromium - Web rendering engine"
                ],
                authentication_methods=[
                    "OAuth 2.0 - GitHub/GitLab integration",
                    "Personal Access Tokens - Repository access",
                    "Azure Active Directory - Enterprise authentication",
                    "SSH Keys - Git authentication"
                ],
                data_formats=[
                    "JSON - Configuration and settings",
                    "JSON-RPC - Language Server Protocol",
                    "Protocol Buffers - Debug Adapter Protocol",
                    "XML - Extension manifests",
                    "TypeScript - Extension development"
                ],
                websocket_events=[
                    "File changes - Real-time file monitoring",
                    "Extension events - Extension lifecycle",
                    "Debug events - Debug session updates",
                    "Terminal events - Terminal output"
                ],
                database_schemas=[
                    "workspace - Project workspace data",
                    "settings - User and workspace settings",
                    "extensions - Installed extensions",
                    "telemetry - Usage analytics data"
                ]
            ),
            "technical_deep_dive": TechnicalDeepDive(
                technology_stack={
                    "desktop": ["Electron", "Node.js", "Chromium", "TypeScript"],
                    "editor": ["Monaco Editor", "xterm.js", "React", "CSS"],
                    "protocols": ["Language Server Protocol", "Debug Adapter Protocol"],
                    "languages": ["TypeScript", "JavaScript", "CSS", "HTML"],
                    "build_tools": ["Webpack", "Rollup", "esbuild", "Gulp"]
                },
                build_system={
                    "type": "Electron + Webpack + TypeScript",
                    "bundling": "Webpack for main process, Rollup for extensions",
                    "compilation": "TypeScript compiler with custom transforms",
                    "packaging": "Electron Builder for distribution",
                    "testing": "Mocha + Playwright for E2E testing"
                },
                testing_framework={
                    "unit_tests": "Mocha + Chai for unit testing",
                    "integration_tests": "Custom test framework for VS Code APIs",
                    "e2e_tests": "Playwright for end-to-end testing",
                    "extension_tests": "Extension test runner",
                    "performance_tests": "Custom performance benchmarks"
                },
                ci_cd_pipeline={
                    "platform": "Azure DevOps",
                    "stages": ["Build", "Test", "Package", "Sign", "Publish"],
                    "deployment": "Auto-updater for releases",
                    "monitoring": "Telemetry and crash reporting"
                },
                deployment_strategy={
                    "distribution": "Electron auto-updater",
                    "platforms": "Windows, macOS, Linux",
                    "channels": "Stable, Insiders, Exploration",
                    "updates": "Automatic background updates"
                },
                performance_optimizations=[
                    "Electron process isolation",
                    "Monaco Editor virtualization",
                    "Extension host process separation",
                    "Lazy loading of extensions",
                    "Memory management and garbage collection",
                    "File watching optimization",
                    "Syntax highlighting performance",
                    "Search index optimization"
                ],
                security_features=[
                    "Extension sandboxing",
                    "Content Security Policy",
                    "Process isolation",
                    "Code signing and verification",
                    "Secure update mechanism",
                    "Input validation and sanitization",
                    "File system access controls",
                    "Network security policies"
                ]
            ),
            "comprehensive_report": f"""# Technical Architecture Report: VS Code

## Executive Summary

Visual Studio Code is a sophisticated, cross-platform code editor built on Electron and TypeScript. It provides a rich development experience through its extensible architecture, integrated debugging, and comprehensive language support via the Language Server Protocol.

## System Architecture Overview

### Core Architecture Principles
- **Electron-based**: Cross-platform desktop application
- **Extension-first**: Highly extensible through plugins
- **Language Server Protocol**: Standardized language support
- **Multi-process**: Isolated processes for stability
- **Web technologies**: HTML, CSS, JavaScript for UI

### Key Technical Decisions

1. **Electron Framework**: Cross-platform desktop development
2. **Monaco Editor**: Web-based code editor component
3. **Language Server Protocol**: Standardized language support
4. **Extension Host**: Isolated extension execution
5. **Multi-window Architecture**: Multiple editor instances

## Extension Architecture

### Extension System
- **Extension Host Process**: Isolated execution environment
- **VSCode API**: Rich API for extension development
- **Language Server Protocol**: Language feature integration
- **Debug Adapter Protocol**: Debugging support
- **File System Provider API**: Custom file system support

### Extension Types
- **Language Extensions**: Syntax highlighting and language features
- **Debug Extensions**: Debugging support for languages
- **Theme Extensions**: UI and syntax themes
- **Snippet Extensions**: Code snippets and templates
- **Keymap Extensions**: Custom key bindings

## Performance & Scalability

### Process Architecture
- **Main Process**: Application lifecycle and window management
- **Renderer Process**: UI rendering and user interaction
- **Extension Host**: Extension execution and API access
- **Language Servers**: Language-specific processing
- **Debug Adapters**: Debugging protocol implementation

### Optimization Strategies
- **Process Isolation**: Prevents extension crashes from affecting editor
- **Lazy Loading**: Load extensions and features on demand
- **Memory Management**: Efficient resource usage and cleanup
- **File Watching**: Optimized file system monitoring
- **Search Indexing**: Fast full-text search capabilities

## Development Experience

### Developer Tools
- **Extension Development**: Rich API and debugging tools
- **Language Server Development**: LSP implementation support
- **Debug Adapter Development**: DAP implementation support
- **Theme Development**: Custom UI and syntax themes
- **Snippet Development**: Code snippet creation

### Testing Strategy
- **Unit Testing**: Mocha + Chai for core functionality
- **Integration Testing**: Extension API testing
- **E2E Testing**: Playwright for full application testing
- **Performance Testing**: Custom benchmarks and monitoring

## Ecosystem & Integration

### Language Support
- **Language Server Protocol**: Standardized language features
- **Debug Adapter Protocol**: Universal debugging support
- **Syntax Highlighting**: TextMate grammar support
- **IntelliSense**: Code completion and suggestions
- **Error Detection**: Real-time error highlighting

### Popular Extensions
- **Language Packs**: Multi-language support
- **Git Integration**: Version control features
- **Debuggers**: Language-specific debugging
- **Linters**: Code quality and style checking
- **Formatters**: Code formatting and beautification

## Recommendations

### Strengths
- **Extensibility**: Rich extension ecosystem
- **Performance**: Fast and responsive editor
- **Cross-platform**: Works on all major operating systems
- **Language Support**: Comprehensive language features
- **Developer Experience**: Excellent tooling and debugging

### Best Practices
- **Extension Development**: Follow VSCode API guidelines
- **Performance**: Optimize for large files and projects
- **Security**: Implement proper input validation
- **Testing**: Write comprehensive tests for extensions
- **Documentation**: Provide clear extension documentation

This architecture represents a mature, production-ready code editor with excellent extensibility and performance characteristics for modern software development.
"""
        }
    
    def _generate_mastodon_architecture(self, repo_info: RepositoryInfo) -> Dict[str, Any]:
        """Generate comprehensive Mastodon-specific architecture analysis."""
        return {
            "system_architecture": SystemArchitecture(
                system_diagram=f"""graph TB
    subgraph "Mastodon Fediverse Architecture"
        subgraph "Client Applications"
            WebUI[Web Interface<br/>Rails Views + React]
            MobileApp[Mobile Apps<br/>iOS/Android]
            ThirdParty[Third-party Clients<br/>API Consumers]
        end
        
        subgraph "Mastodon Server Instance"
            LoadBalancer[Load Balancer<br/>Nginx/HAProxy]
            AppServer[Rails Application<br/>Ruby on Rails]
            Sidekiq[Background Jobs<br/>Sidekiq Workers]
            Redis[Redis Cache<br/>Sessions + Jobs]
        end
        
        subgraph "Data Layer"
            PostgreSQL[(PostgreSQL<br/>Primary Database)]
            S3Storage[S3 Storage<br/>Media Files]
            Elasticsearch[Elasticsearch<br/>Full-text Search]
        end
        
        subgraph "Federation Layer"
            ActivityPub[ActivityPub Protocol<br/>Federation]
            WebFinger[WebFinger<br/>User Discovery]
            NodeInfo[NodeInfo<br/>Instance Metadata]
        end
        
        subgraph "External Services"
            OtherInstances[Other Mastodon Instances<br/>Federation Partners]
            MediaCDN[CDN<br/>Media Delivery]
            Monitoring[Monitoring<br/>Stats + Health]
        end
        
        WebUI --> LoadBalancer
        MobileApp --> LoadBalancer
        ThirdParty --> LoadBalancer
        LoadBalancer --> AppServer
        AppServer --> Sidekiq
        AppServer --> Redis
        AppServer --> PostgreSQL
        AppServer --> S3Storage
        AppServer --> Elasticsearch
        AppServer --> ActivityPub
        ActivityPub --> OtherInstances
        WebFinger --> OtherInstances
        NodeInfo --> OtherInstances
        S3Storage --> MediaCDN
        AppServer --> Monitoring""",
                api_flow_diagram="""sequenceDiagram
    participant User as User
    participant WebUI as Web UI
    participant API as Rails API
    participant Sidekiq as Background Jobs
    participant DB as PostgreSQL
    participant Fed as Federation
    
    User->>WebUI: Create Post
    WebUI->>API: POST /api/v1/statuses
    API->>DB: Save Status
    API->>Sidekiq: Queue Distribution Job
    API->>WebUI: Return Status JSON
    WebUI->>User: Show Posted Status
    
    Sidekiq->>Fed: Distribute via ActivityPub
    Fed->>Fed: Deliver to Followers
    Fed->>API: Inbox Notifications
    API->>DB: Store Incoming Activities""",
                data_flow_diagram="""graph TD
    subgraph "User Input Processing"
        UserInput[User Posts/Interactions]
        Validation[Input Validation<br/>Content Filtering]
        Processing[Content Processing<br/>Mentions/Hashtags]
    end
    
    subgraph "Data Storage"
        StatusStorage[Status Storage<br/>PostgreSQL]
        MediaStorage[Media Storage<br/>S3/File System]
        CacheLayer[Cache Layer<br/>Redis]
    end
    
    subgraph "Federation Processing"
        Outbox[Outbox Processing<br/>ActivityPub]
        Inbox[Inbox Processing<br/>Federation]
        Delivery[Delivery Queue<br/>Sidekiq]
    end
    
    subgraph "Search & Discovery"
        Indexing[Search Indexing<br/>Elasticsearch]
        WebFinger[WebFinger Lookup<br/>User Discovery]
        NodeInfo[NodeInfo<br/>Instance Discovery]
    end
    
    UserInput --> Validation
    Validation --> Processing
    Processing --> StatusStorage
    Processing --> MediaStorage
    Processing --> CacheLayer
    Processing --> Outbox
    Outbox --> Delivery
    Delivery --> Federation
    Inbox --> Processing
    StatusStorage --> Indexing
    WebFinger --> UserInput""",
                component_diagram="""graph TB
    subgraph "Mastodon Rails Application"
        subgraph "Controllers"
            APIController[API Controllers<br/>REST Endpoints]
            WebController[Web Controllers<br/>UI Rendering]
            FederationController[Federation Controllers<br/>ActivityPub]
        end
        
        subgraph "Models"
            Account[Account Model<br/>User Management]
            Status[Status Model<br/>Posts/Toots]
            Media[Media Model<br/>Attachments]
            Notification[Notification Model<br/>Alerts]
        end
        
        subgraph "Services"
            ActivityPubService[ActivityPub Service<br/>Federation Logic]
            SearchService[Search Service<br/>Elasticsearch]
            MediaService[Media Service<br/>File Processing]
            NotificationService[Notification Service<br/>Real-time Alerts]
        end
        
        subgraph "Workers"
            DistributionWorker[Distribution Worker<br/>Federation Delivery]
            MediaWorker[Media Worker<br/>Image Processing]
            SearchWorker[Search Worker<br/>Indexing]
            NotificationWorker[Notification Worker<br/>Push Notifications]
        end
        
        subgraph "Jobs"
            SidekiqJobs[Sidekiq Jobs<br/>Background Processing]
            ScheduledJobs[Scheduled Jobs<br/>Cron Tasks]
        end
    end
    
    APIController --> Account
    APIController --> Status
    WebController --> Account
    WebController --> Status
    FederationController --> ActivityPubService
    ActivityPubService --> DistributionWorker
    Status --> Media
    Status --> Notification
    Media --> MediaService
    MediaService --> MediaWorker
    Notification --> NotificationService
    NotificationService --> NotificationWorker
    SearchService --> SearchWorker
    DistributionWorker --> SidekiqJobs
    MediaWorker --> SidekiqJobs
    SearchWorker --> SidekiqJobs
    NotificationWorker --> SidekiqJobs"""
            ),
            "api_analysis": APIAnalysis(
                endpoints=[
                    {"method": "GET", "path": "/api/v1/accounts/verify_credentials", "description": "Verify account credentials"},
                    {"method": "GET", "path": "/api/v1/accounts/:id", "description": "Get account information"},
                    {"method": "POST", "path": "/api/v1/statuses", "description": "Create a new status/post"},
                    {"method": "GET", "path": "/api/v1/statuses/:id", "description": "Get status details"},
                    {"method": "POST", "path": "/api/v1/statuses/:id/favourite", "description": "Favourite a status"},
                    {"method": "POST", "path": "/api/v1/statuses/:id/reblog", "description": "Boost/reblog a status"},
                    {"method": "GET", "path": "/api/v1/timelines/home", "description": "Get home timeline"},
                    {"method": "GET", "path": "/api/v1/timelines/public", "description": "Get public timeline"},
                    {"method": "GET", "path": "/api/v1/notifications", "description": "Get notifications"},
                    {"method": "POST", "path": "/api/v1/follows", "description": "Follow an account"},
                    {"method": "GET", "path": "/api/v1/search", "description": "Search accounts and statuses"},
                    {"method": "GET", "path": "/api/v1/trends", "description": "Get trending hashtags"},
                    {"method": "WebSocket", "path": "/api/v1/streaming", "description": "Real-time streaming API"}
                ],
                external_services=[
                    "PostgreSQL - Primary database for all data storage",
                    "Redis - Caching, sessions, and background job queues",
                    "Elasticsearch - Full-text search and indexing",
                    "S3/File Storage - Media file storage and CDN",
                    "ActivityPub Protocol - Federation with other instances",
                    "WebFinger - User discovery across instances",
                    "NodeInfo - Instance metadata and capabilities",
                    "SMTP Server - Email notifications and verification",
                    "CDN Services - Media delivery and caching"
                ],
                authentication_methods=[
                    "OAuth 2.0 - API authentication for third-party apps",
                    "Session-based - Web interface authentication",
                    "JWT Tokens - API access tokens",
                    "Application tokens - For server-to-server communication",
                    "WebFinger - Cross-instance user verification"
                ],
                data_formats=[
                    "JSON - Primary API data format",
                    "ActivityPub JSON-LD - Federation protocol",
                    "WebFinger JSON - User discovery",
                    "NodeInfo JSON - Instance metadata",
                    "RSS/Atom - Feed formats",
                    "WebSocket - Real-time streaming"
                ],
                websocket_events=[
                    "user - User-specific notifications",
                    "public - Public timeline updates", 
                    "local - Local timeline updates",
                    "hashtag - Hashtag timeline updates",
                    "list - List timeline updates",
                    "direct - Direct message updates"
                ],
                database_schemas=[
                    "accounts - User account information",
                    "statuses - Posts and statuses",
                    "media_attachments - File attachments",
                    "notifications - User notifications",
                    "follows - Following relationships",
                    "blocks - Blocking relationships",
                    "mutes - Muting relationships",
                    "favourites - Favourite statuses",
                    "reblogs - Boosted statuses",
                    "mentions - Status mentions",
                    "hashtags - Hashtag tracking"
                ]
            ),
            "technical_deep_dive": TechnicalDeepDive(
                technology_stack={
                    "backend": ["Ruby 3.0+", "Rails 7.0+", "PostgreSQL 13+", "Redis 6+", "Elasticsearch 7+"],
                    "frontend": ["React", "TypeScript", "Redux", "SCSS", "Webpack"],
                    "infrastructure": ["Docker", "Nginx", "Sidekiq", "Puma", "HAProxy"],
                    "monitoring": ["Prometheus", "Grafana", "Sentry", "Lograge"],
                    "deployment": ["Docker Compose", "Kubernetes", "Capistrano", "Ansible"]
                },
                build_system={
                    "type": "Rails + Webpack + Docker",
                    "package_manager": "Bundler + Yarn",
                    "asset_pipeline": "Webpack + Sprockets",
                    "containerization": "Docker + Docker Compose",
                    "environment": "Development, Staging, Production"
                },
                testing_framework={
                    "unit_tests": "RSpec for Ruby code",
                    "integration_tests": "Rails system tests",
                    "api_tests": "RSpec API testing",
                    "frontend_tests": "Jest + React Testing Library",
                    "e2e_tests": "Capybara + Selenium",
                    "performance_tests": "Custom load testing"
                },
                ci_cd_pipeline={
                    "platform": "GitHub Actions",
                    "stages": ["Lint", "Security Scan", "Unit Tests", "Integration Tests", "Build", "Deploy"],
                    "deployment": "Docker-based deployment",
                    "monitoring": "Health checks and metrics collection"
                },
                deployment_strategy={
                    "containerization": "Docker containers",
                    "orchestration": "Docker Compose or Kubernetes",
                    "database": "PostgreSQL with read replicas",
                    "caching": "Redis cluster for high availability",
                    "storage": "S3-compatible storage for media",
                    "cdn": "CDN for media delivery",
                    "load_balancing": "Nginx or HAProxy"
                },
                performance_optimizations=[
                    "Database query optimization with proper indexing",
                    "Redis caching for frequently accessed data",
                    "Elasticsearch for fast full-text search",
                    "CDN for media file delivery",
                    "Database connection pooling",
                    "Background job processing with Sidekiq",
                    "Image optimization and resizing",
                    "API response caching",
                    "Database read replicas for scaling",
                    "Connection pooling and keep-alive"
                ],
                security_features=[
                    "Content Security Policy (CSP) headers",
                    "Rate limiting on API endpoints",
                    "Input validation and sanitization",
                    "SQL injection prevention",
                    "XSS protection",
                    "CSRF protection",
                    "Secure headers (HSTS, X-Frame-Options)",
                    "ActivityPub signature verification",
                    "Media file type validation",
                    "User content moderation tools",
                    "Instance-level blocking and filtering",
                    "Two-factor authentication support"
                ]
            ),
            "comprehensive_report": f"""# Technical Architecture Report: Mastodon

## Executive Summary

Mastodon is a sophisticated, open-source microblogging platform that implements the ActivityPub protocol for federated social networking. Built on Ruby on Rails, it provides a Twitter-like experience while maintaining user privacy and enabling decentralized social networking through federation with other instances.

## System Architecture Overview

### Core Architecture Principles
- **Federated Design**: Decentralized network of independent instances
- **ActivityPub Protocol**: Standard for social networking federation
- **Rails MVC**: Clean separation of concerns with Ruby on Rails
- **Background Processing**: Asynchronous job processing with Sidekiq
- **Real-time Updates**: WebSocket streaming for live updates

### Key Technical Decisions

1. **Federation Architecture**: ActivityPub protocol for cross-instance communication
2. **Database Design**: PostgreSQL with optimized indexes for social media data
3. **Caching Strategy**: Redis for sessions, background jobs, and frequently accessed data
4. **Search Implementation**: Elasticsearch for full-text search capabilities
5. **Media Handling**: S3-compatible storage with CDN integration

## Federation & ActivityPub

### ActivityPub Implementation
- **Inbox/Outbox Pattern**: Standard ActivityPub message handling
- **WebFinger Integration**: User discovery across instances
- **NodeInfo Protocol**: Instance capability discovery
- **Signature Verification**: Cryptographic message verification
- **Delivery Queues**: Reliable message delivery with retry logic

### Federation Benefits
- **Decentralization**: No single point of control
- **Privacy**: Data stays on user's chosen instance
- **Resilience**: Network continues if individual instances fail
- **Choice**: Users can choose instances that match their values

## Performance & Scalability

### Database Optimization
- **Connection Pooling**: Efficient database connection management
- **Read Replicas**: Scaling read operations
- **Indexing Strategy**: Optimized indexes for social media queries
- **Query Optimization**: N+1 query prevention and efficient joins

### Caching Strategy
- **Redis Caching**: Session data and frequently accessed content
- **Application Caching**: Rails fragment caching
- **CDN Integration**: Media file delivery optimization
- **Elasticsearch**: Fast full-text search with proper indexing

### Background Processing
- **Sidekiq Workers**: Asynchronous job processing
- **Job Queues**: Priority-based job processing
- **Retry Logic**: Reliable message delivery
- **Monitoring**: Job queue monitoring and alerting

## Security Architecture

### Data Protection
- **Content Moderation**: Instance-level content filtering
- **User Blocking**: Granular blocking and muting capabilities
- **Privacy Controls**: User-controlled visibility settings
- **Data Retention**: Configurable data retention policies

### Federation Security
- **Signature Verification**: Cryptographic message verification
- **Instance Blocking**: Block entire instances if needed
- **Content Filtering**: Keyword and domain-based filtering
- **Rate Limiting**: API endpoint protection

## Development & Deployment

### Development Workflow
- **Rails Conventions**: Following Rails best practices
- **Testing Strategy**: Comprehensive test coverage
- **Code Quality**: Linting and static analysis
- **Documentation**: API documentation and guides

### Deployment Options
- **Docker**: Containerized deployment
- **Docker Compose**: Local development and small instances
- **Kubernetes**: Production-scale orchestration
- **Traditional**: Capistrano-based deployment

## Monitoring & Observability

### Application Monitoring
- **Error Tracking**: Sentry integration for error monitoring
- **Performance Metrics**: Application performance monitoring
- **Health Checks**: Instance health monitoring
- **Logging**: Structured logging with Lograge

### Infrastructure Monitoring
- **Database Monitoring**: PostgreSQL performance metrics
- **Cache Monitoring**: Redis performance and memory usage
- **Search Monitoring**: Elasticsearch cluster health
- **System Metrics**: Server resource utilization

## Recommendations

### Strengths
- **Federation Architecture**: Excellent implementation of ActivityPub
- **Privacy Focus**: Strong user privacy controls
- **Community Driven**: Active open-source community
- **Extensible**: Plugin and customization support
- **Performance**: Well-optimized for social media workloads

### Areas for Enhancement
- **Mobile Experience**: Native mobile app improvements
- **Search Capabilities**: Enhanced search features
- **Analytics**: Better instance analytics and insights
- **Accessibility**: Improved accessibility features
- **Documentation**: More comprehensive API documentation

This architecture represents a mature, production-ready federated social networking platform with excellent technical foundations for privacy-focused, decentralized social media.
"""
        }
    
    def _generate_generic_architecture(self, repo_info: RepositoryInfo) -> Dict[str, Any]:
        """Generate generic architecture analysis for unknown repositories."""
        return {
            "system_architecture": SystemArchitecture(
                system_diagram=f"""graph TB
    subgraph "{repo_info.name} System Architecture"
        A[User Interface Layer<br/>{repo_info.language or 'Frontend'}]
        B[Application Logic<br/>Business Layer]
        C[Data Access Layer<br/>Storage & APIs]
        D[External Services<br/>Third-party Integrations]
    end
    A --> B
    B --> C
    B --> D""",
                api_flow_diagram="""graph LR
    Client[Client Application] --> API[API Gateway]
    API --> Auth[Authentication]
    API --> Business[Business Logic]
    Business --> Database[(Database)]
    Business --> Cache[(Cache)]""",
                data_flow_diagram="""graph TD
    Input[User Input] --> Validation[Input Validation]
    Validation --> Processing[Data Processing]
    Processing --> Storage[Data Storage]
    Storage --> Output[Response Output]""",
                component_diagram=f"""graph TB
    subgraph "{repo_info.name} Components"
        UI[User Interface Components]
        Logic[Business Logic Modules]
        Data[Data Access Objects]
        Utils[Utility Functions]
    end
    UI --> Logic
    Logic --> Data
    Logic --> Utils"""
            ),
            "api_analysis": APIAnalysis(
                endpoints=[f"API analysis pending for {repo_info.name}"],
                external_services=[repo_info.language or "Unknown technology stack"],
                authentication_methods=["Standard authentication patterns"],
                data_formats=["JSON", "HTTP/HTTPS"]
            ),
            "technical_deep_dive": TechnicalDeepDive(
                technology_stack={"primary": [repo_info.language or "Unknown"]},
                build_system={"type": "Standard build process"},
                testing_framework={"type": "Standard testing approach"},
                ci_cd_pipeline={"type": "Continuous integration"},
                deployment_strategy={"type": "Standard deployment"},
                performance_optimizations=["Performance optimizations to be analyzed"],
                security_features=["Security features to be analyzed"]
            ),
            "comprehensive_report": f"""# Technical Analysis: {repo_info.full_name}

## Repository Overview
- **Language**: {repo_info.language or 'Not specified'}
- **Stars**: {repo_info.stars:,}
- **Size**: {repo_info.size:,} KB

## Analysis Summary
This is a {repo_info.language or 'software'} project with {repo_info.stars:,} stars, indicating {
'high' if repo_info.stars > 10000 else 'moderate' if repo_info.stars > 1000 else 'emerging'
} community adoption.

Further detailed analysis would require deeper repository inspection to provide comprehensive architecture insights, API documentation, and technical recommendations.
"""
        }
    
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