"""
Command-line interface for the GitHub Repository Analyzer.
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from .analyzer import GitHubRepoAnalyzer, AnalyzerFactory
from .enhanced_analyzer import EnhancedClaudeAnalyzer
from .test_generator import TestGenerator
from .types import OutputFormat, AnalyzerConfig, TestGenerationConfig
from .exceptions import (
    GitHubRepoAnalyzerError, RepositoryNotFoundError, ClaudeAnalysisError,
    ConfigurationError
)

console = Console()


def validate_repo_format(ctx, param, value):
    """Validate repository format (owner/repo-name)."""
    if value and '/' not in value:
        raise click.BadParameter('Repository must be in format "owner/repo-name"')
    return value


def validate_output_format(ctx, param, value):
    """Validate output format."""
    if value:
        try:
            return OutputFormat(value.lower())
        except ValueError:
            raise click.BadParameter(f'Invalid output format. Choose from: {", ".join([f.value for f in OutputFormat])}')
    return OutputFormat.TEXT


@click.group()
@click.version_option(version="0.1.0", prog_name="GitHub Repository Analyzer")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """GitHub Repository Analyzer - Generate user stories from GitHub repositories using Claude Code SDK."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('repo', callback=validate_repo_format, required=True)
@click.option('--token', '-t', help='GitHub personal access token')
@click.option('--focus', '-f', help='Focus area for user stories (e.g., "security", "performance")')
@click.option('--max-stories', '-m', type=int, default=5, help='Maximum number of user stories to generate')
@click.option('--format', 'output_format', callback=validate_output_format, default='text', help='Output format (text, json, markdown)')
@click.option('--output-file', '-o', type=click.Path(path_type=Path), help='Save output to file')
@click.option('--system-prompt', help='Custom system prompt for Claude')
@click.option('--config-file', type=click.Path(exists=True, path_type=Path), help='Configuration file path')
@click.option('--comprehensive', '-c', is_flag=True, help='Enable comprehensive analysis with architecture diagrams')
@click.option('--include-api-analysis', is_flag=True, default=True, help='Include API endpoint analysis')
@click.option('--include-architecture', is_flag=True, default=True, help='Include system architecture diagrams')
@click.pass_context
def analyze(ctx, repo, token, focus, max_stories, output_format, output_file, system_prompt, config_file, comprehensive, include_api_analysis, include_architecture):
    """Analyze a GitHub repository and generate user stories."""
    
    try:
        # Parse repository owner and name
        owner, repo_name = repo.split('/', 1)
        
        # Create configuration
        if config_file:
            config = AnalyzerFactory.create_from_file(config_file)
        else:
            config = AnalyzerFactory.create_from_env()
        
        # Override with command line options
        if token:
            config.github.token = token
        if focus:
            config.focus_area = focus
        if max_stories:
            config.max_stories = max_stories
        if output_format:
            config.output_format = output_format
        if output_file:
            config.output_file = output_file
        if system_prompt:
            config.claude.system_prompt = system_prompt
        if ctx.obj.get('verbose'):
            config.verbose = True
        
        # Store comprehensive analysis flags in config metadata
        config.metadata = getattr(config, 'metadata', {})
        config.metadata['comprehensive'] = comprehensive
        config.metadata['include_api_analysis'] = include_api_analysis
        config.metadata['include_architecture'] = include_architecture
        
        # Run analysis (comprehensive or basic)
        if comprehensive:
            asyncio.run(_run_comprehensive_analysis(owner, repo_name, config))
        else:
            asyncio.run(_run_analysis(owner, repo_name, config))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('repo', callback=validate_repo_format, required=True)
@click.option('--token', '-t', help='GitHub personal access token')
@click.option('--focus', '-f', help='Focus area for user stories')
@click.option('--max-stories', '-m', type=int, default=5, help='Maximum number of user stories')
@click.option('--format', 'output_format', callback=validate_output_format, default='markdown', help='Output format')
@click.option('--output-file', '-o', type=click.Path(path_type=Path), help='Output file path')
@click.pass_context
def quick(ctx, repo, token, focus, max_stories, output_format, output_file):
    """Quick analysis with default settings."""
    
    try:
        owner, repo_name = repo.split('/', 1)
        
        # Use default configuration
        config = AnalyzerFactory.create_default()
        config.github.token = token
        config.focus_area = focus
        config.max_stories = max_stories
        config.output_format = output_format
        
        if output_file:
            config.output_file = output_file
        else:
            # Generate default filename
            default_filename = f"{owner}-{repo_name}-user-stories{config.output_format.get_file_extension()}"
            config.output_file = Path(default_filename)
        
        # Run analysis
        asyncio.run(_run_analysis(owner, repo_name, config))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('repo', callback=validate_repo_format, required=True)
@click.option('--token', '-t', help='GitHub personal access token')
@click.option('--output-file', '-o', type=click.Path(path_type=Path), help='Save architecture diagrams to file')
@click.option('--focus', '-f', help='Focus area for architecture analysis')
@click.pass_context
def architecture(ctx, repo, token, output_file, focus):
    """Generate system architecture diagrams and API analysis for a repository."""
    
    try:
        owner, repo_name = repo.split('/', 1)
        
        config = AnalyzerFactory.create_default()
        if token:
            config.github.token = token
        config.focus_area = focus
        config.max_stories = 0  # Skip user stories for architecture-only analysis
        config.output_format = OutputFormat.MARKDOWN
        
        if output_file:
            config.output_file = output_file
        else:
            # Generate default filename for architecture analysis
            default_filename = f"{owner}-{repo_name}-architecture.md"
            config.output_file = Path(default_filename)
        
        # Store flags for architecture-only analysis
        config.metadata = getattr(config, 'metadata', {})
        config.metadata['comprehensive'] = True
        config.metadata['include_api_analysis'] = True
        config.metadata['include_architecture'] = True
        config.metadata['architecture_only'] = True
        
        # Run architecture analysis
        asyncio.run(_run_architecture_analysis(owner, repo_name, config))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--token', '-t', help='GitHub personal access token')
@click.pass_context
def rate_limit(ctx, token):
    """Check GitHub API rate limit status."""
    
    try:
        config = AnalyzerFactory.create_default()
        if token:
            config.github.token = token
        
        asyncio.run(_check_rate_limit(config))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('repo', callback=validate_repo_format, required=True)
@click.option('--token', '-t', help='GitHub personal access token')
@click.pass_context
def info(ctx, repo, token):
    """Get basic information about a repository without generating user stories."""
    
    try:
        owner, repo_name = repo.split('/', 1)
        
        config = AnalyzerFactory.create_default()
        if token:
            config.github.token = token
        
        asyncio.run(_get_repo_info(owner, repo_name, config))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('repo', callback=validate_repo_format, required=True)
@click.option('--token', '-t', help='GitHub personal access token')
@click.option('--focus', '-f', help='Focus area for test generation')
@click.option('--max-tests', '-m', type=int, default=5, help='Maximum tests per user story')
@click.option('--include-unit', is_flag=True, default=True, help='Include unit tests')
@click.option('--include-integration', is_flag=True, default=True, help='Include integration tests')
@click.option('--include-e2e', is_flag=True, default=True, help='Include end-to-end tests')
@click.option('--include-api', is_flag=True, default=True, help='Include API tests')
@click.option('--format', 'output_format', callback=validate_output_format, default='markdown', help='Output format')
@click.option('--output-file', '-o', type=click.Path(path_type=Path), help='Save test documentation to file')
@click.pass_context
def tests(ctx, repo, token, focus, max_tests, include_unit, include_integration, include_e2e, include_api, output_format, output_file):
    """Generate comprehensive test cases and documentation from user stories."""
    
    try:
        owner, repo_name = repo.split('/', 1)
        
        config = AnalyzerFactory.create_default()
        if token:
            config.github.token = token
        config.focus_area = focus
        config.output_format = output_format
        
        if output_file:
            config.output_file = output_file
        else:
            # Generate default filename for test documentation
            default_filename = f"{owner}-{repo_name}-tests{output_format.get_file_extension()}"
            config.output_file = Path(default_filename)
        
        # Run test generation
        asyncio.run(_run_test_generation(owner, repo_name, config, max_tests, include_unit, include_integration, include_e2e, include_api))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


async def _run_comprehensive_analysis(owner: str, repo_name: str, config: AnalyzerConfig):
    """Run comprehensive repository analysis with architecture diagrams."""
    
    console.print(Panel(f"🔍 Comprehensive Analysis: [bold blue]{owner}/{repo_name}[/bold blue]", style="blue"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task1 = progress.add_task("Fetching repository information...", total=None)
        
        async with GitHubRepoAnalyzer(config) as analyzer:
            try:
                # Fetch repository info
                repo_info = await analyzer._fetch_repository_info(owner, repo_name)
                progress.update(task1, completed=True, description="✅ Repository information fetched")
                
                # Task 2: Conduct web research
                task2 = progress.add_task("Conducting web research...", total=None)
                web_results = await analyzer._conduct_web_research(repo_info)
                progress.update(task2, completed=True, description="✅ Web research completed")
                
                # Task 3: Enhanced analysis with Claude
                task3 = progress.add_task("Performing comprehensive technical analysis...", total=None)
                
                enhanced_analyzer = EnhancedClaudeAnalyzer(config.claude)
                analysis_result = await enhanced_analyzer.analyze_repository_comprehensive(
                    repo_info=repo_info,
                    web_results=web_results,
                    focus_area=config.focus_area,
                    max_stories=config.max_stories,
                    include_architecture=config.metadata.get('include_architecture', True),
                    include_api_analysis=config.metadata.get('include_api_analysis', True)
                )
                
                progress.update(task3, completed=True, description="✅ Comprehensive analysis completed")
                
                # Task 4: Format and display results
                task4 = progress.add_task("Formatting comprehensive results...", total=None)
                
                # Display comprehensive results
                _display_comprehensive_results(analysis_result, config)
                
                # Save to file if specified
                if config.output_file:
                    analyzer.output_formatter.save_to_file(analysis_result, config.output_file)
                    console.print(f"\n💾 Results saved to: [bold green]{config.output_file}[/bold green]")
                
                progress.update(task4, completed=True, description="✅ Comprehensive analysis complete")
                
            except RepositoryNotFoundError:
                console.print(f"[red]❌ Repository {owner}/{repo_name} not found[/red]")
                sys.exit(1)
            except ClaudeAnalysisError as e:
                console.print(f"[red]❌ Enhanced analysis failed: {e}[/red]")
                sys.exit(1)
            except Exception as e:
                console.print(f"[red]❌ Comprehensive analysis failed: {e}[/red]")
                sys.exit(1)


async def _run_architecture_analysis(owner: str, repo_name: str, config: AnalyzerConfig):
    """Run architecture-focused analysis of a repository."""
    
    console.print(Panel(f"🏗️ Architecture Analysis: [bold blue]{owner}/{repo_name}[/bold blue]", style="blue"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task1 = progress.add_task("Fetching repository information...", total=None)
        
        async with GitHubRepoAnalyzer(config) as analyzer:
            try:
                # Fetch repository info
                repo_info = await analyzer._fetch_repository_info(owner, repo_name)
                progress.update(task1, completed=True, description="✅ Repository information fetched")
                
                # Task 2: Architecture analysis with Claude
                task2 = progress.add_task("Analyzing system architecture...", total=None)
                
                enhanced_analyzer = EnhancedClaudeAnalyzer(config.claude)
                analysis_result = await enhanced_analyzer.analyze_repository_comprehensive(
                    repo_info=repo_info,
                    web_results=[],  # Skip web research for architecture focus
                    focus_area=config.focus_area,
                    max_stories=0,  # No user stories for architecture analysis
                    include_architecture=True,
                    include_api_analysis=True
                )
                
                progress.update(task2, completed=True, description="✅ Architecture analysis completed")
                
                # Task 3: Display architecture results
                task3 = progress.add_task("Generating architecture report...", total=None)
                
                # Display architecture-focused results
                _display_architecture_results(analysis_result, config)
                
                # Save to file
                if config.output_file:
                    analyzer.output_formatter.save_to_file(analysis_result, config.output_file)
                    console.print(f"\n💾 Architecture report saved to: [bold green]{config.output_file}[/bold green]")
                
                progress.update(task3, completed=True, description="✅ Architecture report generated")
                
            except RepositoryNotFoundError:
                console.print(f"[red]❌ Repository {owner}/{repo_name} not found[/red]")
                sys.exit(1)
            except Exception as e:
                console.print(f"[red]❌ Architecture analysis failed: {e}[/red]")
                sys.exit(1)


async def _run_analysis(owner: str, repo_name: str, config: AnalyzerConfig):
    """Run the repository analysis."""
    
    console.print(Panel(f"🔍 Analyzing repository: [bold blue]{owner}/{repo_name}[/bold blue]", style="blue"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Task 1: Fetch repository information
        task1 = progress.add_task("Fetching repository information...", total=None)
        
        async with GitHubRepoAnalyzer(config) as analyzer:
            try:
                # Fetch repository info
                repo_info = await analyzer._fetch_repository_info(owner, repo_name)
                progress.update(task1, completed=True, description="✅ Repository information fetched")
                
                # Task 2: Conduct web research
                task2 = progress.add_task("Conducting web research...", total=None)
                web_results = await analyzer._conduct_web_research(repo_info)
                progress.update(task2, completed=True, description="✅ Web research completed")
                
                # Task 3: Analyze with Claude
                task3 = progress.add_task("Generating user stories with Claude...", total=None)
                analysis_result = await analyzer._analyze_with_claude(repo_info, web_results)
                progress.update(task3, completed=True, description="✅ User stories generated")
                
                # Task 4: Format and display results
                task4 = progress.add_task("Formatting results...", total=None)
                
                # Display results
                _display_analysis_results(analysis_result, config)
                
                # Save to file if specified
                if config.output_file:
                    await analyzer._save_output(analysis_result)
                    console.print(f"\n💾 Results saved to: [bold green]{config.output_file}[/bold green]")
                
                progress.update(task4, completed=True, description="✅ Analysis complete")
                
            except RepositoryNotFoundError:
                console.print(f"[red]❌ Repository {owner}/{repo_name} not found[/red]")
                sys.exit(1)
            except ClaudeAnalysisError as e:
                console.print(f"[red]❌ Claude analysis failed: {e}[/red]")
                sys.exit(1)
            except Exception as e:
                console.print(f"[red]❌ Analysis failed: {e}[/red]")
                sys.exit(1)


async def _check_rate_limit(config: AnalyzerConfig):
    """Check GitHub API rate limit status."""
    
    console.print(Panel("📊 Checking GitHub API rate limit status", style="blue"))
    
    try:
        async with GitHubRepoAnalyzer(config) as analyzer:
            rate_limit_info = analyzer.github_client.get_rate_limit_info()
            
            if rate_limit_info and 'resources' in rate_limit_info:
                core = rate_limit_info['resources'].get('core', {})
                search = rate_limit_info['resources'].get('search', {})
                
                table = Table(title="GitHub API Rate Limits")
                table.add_column("Resource", style="cyan")
                table.add_column("Limit", style="green")
                table.add_column("Remaining", style="yellow")
                table.add_column("Reset Time", style="blue")
                
                # Core API
                if core:
                    reset_time = core.get('reset')
                    if reset_time:
                        from datetime import datetime
                        reset_datetime = datetime.fromtimestamp(reset_time)
                        table.add_row(
                            "Core API",
                            str(core.get('limit', 'N/A')),
                            str(core.get('remaining', 'N/A')),
                            reset_datetime.strftime('%Y-%m-%d %H:%M:%S')
                        )
                
                # Search API
                if search:
                    reset_time = search.get('reset')
                    if reset_time:
                        from datetime import datetime
                        reset_datetime = datetime.fromtimestamp(reset_time)
                        table.add_row(
                            "Search API",
                            str(search.get('limit', 'N/A')),
                            str(search.get('remaining', 'N/A')),
                            reset_datetime.strftime('%Y-%m-%d %H:%M:%S')
                        )
                
                console.print(table)
                
                # Show authentication status
                if config.github.token:
                    console.print("🔐 [green]Authenticated with GitHub token[/green]")
                else:
                    console.print("⚠️  [yellow]No GitHub token provided (limited rate limit)[/yellow]")
                    
            else:
                console.print("[red]❌ Failed to fetch rate limit information[/red]")
                
    except Exception as e:
        console.print(f"[red]❌ Error checking rate limit: {e}[/red]")


async def _get_repo_info(owner: str, repo_name: str, config: AnalyzerConfig):
    """Get basic repository information."""
    
    console.print(Panel(f"📋 Repository Information: [bold blue]{owner}/{repo_name}[/bold blue]", style="blue"))
    
    try:
        async with GitHubRepoAnalyzer(config) as analyzer:
            repo_info = await analyzer._fetch_repository_info(owner, repo_name)
            
            # Display repository information
            table = Table(title="Repository Details")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Full Name", repo_info.full_name)
            table.add_row("Description", repo_info.description or "No description")
            table.add_row("Language", repo_info.language or "Not specified")
            table.add_row("Stars", str(repo_info.stars))
            table.add_row("Forks", str(repo_info.forks))
            table.add_row("Topics", ", ".join(repo_info.topics) if repo_info.topics else "None")
            table.add_row("License", repo_info.license or "Not specified")
            table.add_row("Created", repo_info.created_at.strftime('%Y-%m-%d'))
            table.add_row("Updated", repo_info.updated_at.strftime('%Y-%m-%d'))
            table.add_row("Size", f"{repo_info.size:,} KB")
            table.add_row("Default Branch", repo_info.default_branch)
            
            console.print(table)
            
            # Show README preview if available
            if repo_info.readme_content:
                console.print("\n📖 README Preview:")
                preview = repo_info.readme_content[:500] + "..." if len(repo_info.readme_content) > 500 else repo_info.readme_content
                console.print(Panel(preview, title="README", style="green"))
                
    except RepositoryNotFoundError:
        console.print(f"[red]❌ Repository {owner}/{repo_name} not found[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error fetching repository information: {e}[/red]")


def _display_comprehensive_results(analysis_result, config: AnalyzerConfig):
    """Display comprehensive analysis results with architecture diagrams."""
    
    console.print("\n" + "="*100)
    console.print(Panel(f"🏗️ Comprehensive Analysis: [bold blue]{analysis_result.repository.full_name}[/bold blue]", style="green"))
    console.print("="*100)
    
    # Repository summary
    console.print(f"\n📊 [bold]Repository Summary:[/bold]")
    console.print(f"   Description: {analysis_result.repository.description or 'No description available'}")
    console.print(f"   Language: {analysis_result.repository.language or 'Not specified'}")
    console.print(f"   Stars: {analysis_result.repository.stars}")
    console.print(f"   Topics: {', '.join(analysis_result.repository.topics) if analysis_result.repository.topics else 'None'}")
    
    # System Architecture Diagrams
    if analysis_result.system_architecture:
        console.print(f"\n🏗️ [bold]System Architecture:[/bold]")
        
        if analysis_result.system_architecture.system_diagram:
            console.print("\n📐 [bold cyan]System Architecture Diagram:[/bold cyan]")
            console.print("```mermaid")
            console.print(analysis_result.system_architecture.system_diagram)
            console.print("```")
        
        if analysis_result.system_architecture.api_flow_diagram:
            console.print("\n🔄 [bold cyan]API Flow Diagram:[/bold cyan]")
            console.print("```mermaid")
            console.print(analysis_result.system_architecture.api_flow_diagram)
            console.print("```")
        
        if analysis_result.system_architecture.data_flow_diagram:
            console.print("\n💾 [bold cyan]Data Flow Diagram:[/bold cyan]")
            console.print("```mermaid")
            console.print(analysis_result.system_architecture.data_flow_diagram)
            console.print("```")
        
        if analysis_result.system_architecture.component_diagram:
            console.print("\n🧩 [bold cyan]Component Architecture:[/bold cyan]")
            console.print("```mermaid")
            console.print(analysis_result.system_architecture.component_diagram)
            console.print("```")
    
    # API Analysis
    if analysis_result.api_analysis:
        console.print(f"\n🌐 [bold]API & Integration Analysis:[/bold]")
        
        if analysis_result.api_analysis.endpoints:
            console.print("   [bold]API Endpoints:[/bold]")
            for endpoint in analysis_result.api_analysis.endpoints[:5]:
                if isinstance(endpoint, dict):
                    console.print(f"   • {endpoint.get('method', 'GET')} {endpoint.get('path', endpoint.get('name', str(endpoint)))}")
                else:
                    console.print(f"   • {endpoint}")
        
        if analysis_result.api_analysis.external_services:
            console.print("   [bold]External Services:[/bold]")
            for service in analysis_result.api_analysis.external_services:
                console.print(f"   • {service}")
        
        if analysis_result.api_analysis.websocket_events:
            console.print("   [bold]WebSocket Events:[/bold]")
            for event in analysis_result.api_analysis.websocket_events:
                console.print(f"   • {event}")
    
    # Technical Deep Dive
    if analysis_result.technical_deep_dive:
        console.print(f"\n🔧 [bold]Technology Stack:[/bold]")
        
        tech_stack = analysis_result.technical_deep_dive.technology_stack
        for category, technologies in tech_stack.items():
            if technologies:
                console.print(f"   [bold]{category.title()}:[/bold]")
                for tech in technologies:
                    console.print(f"   • {tech}")
    
    # User Stories Section
    console.print(f"\n📝 [bold]User Stories ({len(analysis_result.user_stories)}):[/bold]")
    
    for i, story in enumerate(analysis_result.user_stories, 1):
        console.print(f"\n🎯 [bold]Story {i}: {story.title}[/bold]")
        console.print(f"   {story.description}")
        
        if story.acceptance_criteria:
            console.print(f"   [bold]Acceptance Criteria:[/bold]")
            for criterion in story.acceptance_criteria:
                console.print(f"   • {criterion.description}")
        
        console.print(f"   [bold]Priority:[/bold] {story.priority.value} | [bold]Effort:[/bold] {story.effort.value}")
        
        if story.tags:
            console.print(f"   [bold]Tags:[/bold] {', '.join(story.tags)}")
        
        console.print("   " + "-"*80)
    
    # Comprehensive Report
    if analysis_result.comprehensive_report:
        console.print(f"\n📋 [bold]Technical Report Summary:[/bold]")
        # Show first few lines of the report
        report_lines = analysis_result.comprehensive_report.split('\n')[:10]
        for line in report_lines:
            console.print(f"   {line}")
        if len(analysis_result.comprehensive_report.split('\n')) > 10:
            console.print("   [italic]... (truncated, see full report in output file)[/italic]")


def _display_architecture_results(analysis_result, config: AnalyzerConfig):
    """Display architecture-focused analysis results."""
    
    console.print("\n" + "="*100)
    console.print(Panel(f"🏗️ Architecture Analysis: [bold blue]{analysis_result.repository.full_name}[/bold blue]", style="cyan"))
    console.print("="*100)
    
    # Repository summary
    console.print(f"\n📊 [bold]Repository Overview:[/bold]")
    console.print(f"   • Description: {analysis_result.repository.description or 'No description available'}")
    console.print(f"   • Primary Language: {analysis_result.repository.language or 'Not specified'}")
    console.print(f"   • Stars: {analysis_result.repository.stars:,}")
    console.print(f"   • Size: {analysis_result.repository.size:,} KB")
    
    # System Architecture Diagrams - Main Focus
    if analysis_result.system_architecture:
        console.print(f"\n🏗️ [bold yellow]SYSTEM ARCHITECTURE DIAGRAMS[/bold yellow]")
        console.print("=" * 60)
        
        if analysis_result.system_architecture.system_diagram:
            console.print("\n📐 [bold cyan]Overall System Architecture:[/bold cyan]")
            console.print("[dim]Copy this Mermaid code to visualize the diagram:[/dim]")
            console.print("```mermaid")
            console.print(analysis_result.system_architecture.system_diagram)
            console.print("```")
        
        if analysis_result.system_architecture.api_flow_diagram:
            console.print("\n🔄 [bold cyan]API & Data Flow:[/bold cyan]")
            console.print("[dim]API request/response flow and data processing:[/dim]")
            console.print("```mermaid")
            console.print(analysis_result.system_architecture.api_flow_diagram)
            console.print("```")
        
        if analysis_result.system_architecture.component_diagram:
            console.print("\n🧩 [bold cyan]Component Architecture:[/bold cyan]")
            console.print("[dim]Internal component structure and relationships:[/dim]")
            console.print("```mermaid")
            console.print(analysis_result.system_architecture.component_diagram)
            console.print("```")
        
        if analysis_result.system_architecture.data_flow_diagram:
            console.print("\n💾 [bold cyan]Data Flow Architecture:[/bold cyan]")
            console.print("[dim]How data moves through the system:[/dim]")
            console.print("```mermaid")
            console.print(analysis_result.system_architecture.data_flow_diagram)
            console.print("```")
    
    # API & Integration Analysis
    if analysis_result.api_analysis:
        console.print(f"\n🌐 [bold yellow]API & INTEGRATION ANALYSIS[/bold yellow]")
        console.print("=" * 60)
        
        if analysis_result.api_analysis.endpoints:
            console.print("\n📡 [bold]API Endpoints:[/bold]")
            for i, endpoint in enumerate(analysis_result.api_analysis.endpoints[:10], 1):
                if isinstance(endpoint, dict):
                    method = endpoint.get('method', 'GET')
                    path = endpoint.get('path', endpoint.get('name', 'Unknown'))
                    desc = endpoint.get('description', '')
                    console.print(f"   {i:2d}. [bold]{method}[/bold] {path}")
                    if desc:
                        console.print(f"       {desc}")
                else:
                    console.print(f"   {i:2d}. {endpoint}")
        
        if analysis_result.api_analysis.external_services:
            console.print("\n🔗 [bold]External Services & Integrations:[/bold]")
            for i, service in enumerate(analysis_result.api_analysis.external_services, 1):
                console.print(f"   {i:2d}. {service}")
        
        if analysis_result.api_analysis.authentication_methods:
            console.print("\n🔐 [bold]Authentication Methods:[/bold]")
            for auth in analysis_result.api_analysis.authentication_methods:
                console.print(f"   • {auth}")
        
        if analysis_result.api_analysis.websocket_events:
            console.print("\n⚡ [bold]Real-time Events:[/bold]")
            for event in analysis_result.api_analysis.websocket_events:
                console.print(f"   • {event}")
    
    # Technology Stack Deep Dive
    if analysis_result.technical_deep_dive:
        console.print(f"\n🔧 [bold yellow]TECHNICAL DEEP DIVE[/bold yellow]")
        console.print("=" * 60)
        
        tech_stack = analysis_result.technical_deep_dive.technology_stack
        if tech_stack:
            for category, technologies in tech_stack.items():
                if technologies:
                    console.print(f"\n🏷️ [bold]{category.replace('_', ' ').title()}:[/bold]")
                    for tech in technologies:
                        console.print(f"   • {tech}")
        
        # Build system info
        if analysis_result.technical_deep_dive.build_system:
            console.print(f"\n🏗️ [bold]Build System:[/bold]")
            build_info = analysis_result.technical_deep_dive.build_system
            for key, value in build_info.items():
                if value:
                    console.print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        # Performance optimizations
        if analysis_result.technical_deep_dive.performance_optimizations:
            console.print(f"\n⚡ [bold]Performance Optimizations:[/bold]")
            for opt in analysis_result.technical_deep_dive.performance_optimizations:
                console.print(f"   • {opt}")
        
        # Security features
        if analysis_result.technical_deep_dive.security_features:
            console.print(f"\n🛡️ [bold]Security Features:[/bold]")
            for security in analysis_result.technical_deep_dive.security_features:
                console.print(f"   • {security}")
    
    # Technical Report Summary
    if analysis_result.comprehensive_report:
        console.print(f"\n📋 [bold yellow]TECHNICAL INSIGHTS[/bold yellow]")
        console.print("=" * 60)
        # Show key insights from the technical report
        report_lines = analysis_result.comprehensive_report.split('\n')
        key_sections = []
        current_section = []
        
        for line in report_lines:
            if line.startswith('#') and current_section:
                key_sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            key_sections.append('\n'.join(current_section))
        
        # Show first 2-3 sections
        for section in key_sections[:3]:
            lines = section.split('\n')[:5]  # First 5 lines of each section
            for line in lines:
                if line.strip():
                    console.print(f"   {line}")
            console.print()
        
        if len(key_sections) > 3:
            console.print("   [italic]... (Full technical report saved to output file)[/italic]")
    
    console.print(f"\n[bold green]✅ Architecture Analysis Complete![/bold green]")
    console.print("[dim]Tip: Copy the Mermaid diagram codes above to visualize them at https://mermaid.live[/dim]")


async def _run_test_generation(
    owner: str, 
    repo_name: str, 
    config: AnalyzerConfig,
    max_tests: int,
    include_unit: bool,
    include_integration: bool,
    include_e2e: bool,
    include_api: bool
):
    """Run test generation for a repository."""
    
    console.print(Panel(f"🧪 Test Generation: [bold blue]{owner}/{repo_name}[/bold blue]", style="green"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task1 = progress.add_task("Fetching repository information...", total=None)
        
        async with GitHubRepoAnalyzer(config) as analyzer:
            try:
                # Fetch repository info
                repo_info = await analyzer._fetch_repository_info(owner, repo_name)
                progress.update(task1, completed=True, description="✅ Repository information fetched")
                
                # Task 2: Conduct web research
                task2 = progress.add_task("Conducting web research...", total=None)
                web_results = await analyzer._conduct_web_research(repo_info)
                progress.update(task2, completed=True, description="✅ Web research completed")
                
                # Task 3: Generate user stories first
                task3 = progress.add_task("Generating user stories for test generation...", total=None)
                
                enhanced_analyzer = EnhancedClaudeAnalyzer(config.claude)
                analysis_result = await enhanced_analyzer.analyze_repository_comprehensive(
                    repo_info=repo_info,
                    web_results=web_results,
                    focus_area=config.focus_area,
                    max_stories=5,  # Generate a few stories for testing
                    include_architecture=False,  # Skip architecture for test generation
                    include_api_analysis=False
                )
                
                progress.update(task3, completed=True, description="✅ User stories generated")
                
                # Task 4: Generate tests from user stories
                task4 = progress.add_task("Generating comprehensive test cases...", total=None)
                
                # Create test generation configuration
                test_config = TestGenerationConfig(
                    include_unit_tests=include_unit,
                    include_integration_tests=include_integration,
                    include_e2e_tests=include_e2e,
                    include_api_tests=include_api,
                    max_tests_per_story=max_tests,
                    focus_area=config.focus_area,
                    output_format=config.output_format
                )
                
                test_generator = TestGenerator(test_config)
                test_documentation = await test_generator.generate_tests_from_analysis(
                    analysis_result, repo_info
                )
                
                progress.update(task4, completed=True, description="✅ Test cases generated")
                
                # Task 5: Display and save results
                task5 = progress.add_task("Formatting and saving test documentation...", total=None)
                
                # Display test generation results
                _display_test_generation_results(test_documentation, config)
                
                # Save to file if specified
                if config.output_file:
                    # Create a test output formatter
                    from .output_formatter import OutputFormatter
                    test_formatter = OutputFormatter(config.output_format)
                    test_formatter.save_test_documentation_to_file(test_documentation, config.output_file)
                    console.print(f"\n💾 Test documentation saved to: [bold green]{config.output_file}[/bold green]")
                
                progress.update(task5, completed=True, description="✅ Test generation complete")
                
            except RepositoryNotFoundError:
                console.print(f"[red]❌ Repository {owner}/{repo_name} not found[/red]")
                sys.exit(1)
            except Exception as e:
                console.print(f"[red]❌ Test generation failed: {e}[/red]")
                if config.verbose:
                    console.print_exception()
                sys.exit(1)


def _display_test_generation_results(test_documentation, config: AnalyzerConfig):
    """Display the test generation results."""
    
    console.print("\n" + "="*80)
    console.print(Panel(f"🧪 Test Documentation for [bold blue]{test_documentation.repository_name}[/bold blue]", style="green"))
    console.print("="*80)
    
    # Test summary
    console.print(f"\n📊 [bold]Test Summary:[/bold]")
    console.print(f"   Total Test Cases: {test_documentation.total_test_cases}")
    console.print(f"   Total Test Suites: {len(test_documentation.test_suites)}")
    console.print(f"   Analysis Date: {test_documentation.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test coverage
    if test_documentation.test_coverage:
        console.print(f"\n📈 [bold]Test Coverage by Type:[/bold]")
        for test_type, coverage in test_documentation.test_coverage.items():
            console.print(f"   • {test_type.title()}: {coverage:.1f}%")
    
    # Test suites
    console.print(f"\n🧪 [bold]Test Suites ({len(test_documentation.test_suites)}):[/bold]")
    
    for i, suite in enumerate(test_documentation.test_suites, 1):
        console.print(f"\n📋 [bold]Suite {i}: {suite.name}[/bold]")
        console.print(f"   Description: {suite.description}")
        console.print(f"   Test Type: {suite.test_type.value.title()}")
        console.print(f"   Total Tests: {suite.total_tests}")
        console.print(f"   User Stories: {', '.join(map(str, suite.user_story_ids))}")
        
        # Show first few test cases
        console.print(f"   [bold]Test Cases:[/bold]")
        for j, test_case in enumerate(suite.test_cases[:3], 1):  # Show first 3
            console.print(f"     {j}. {test_case.title} ({test_case.priority.value})")
        
        if len(suite.test_cases) > 3:
            console.print(f"     ... and {len(suite.test_cases) - 3} more tests")
        
        console.print("   " + "-"*60)
    
    # Testing strategy
    if test_documentation.testing_strategy:
        console.print(f"\n📋 [bold]Testing Strategy:[/bold]")
        strategy_lines = test_documentation.testing_strategy.split('\n')[:10]  # First 10 lines
        for line in strategy_lines:
            if line.strip():
                console.print(f"   {line}")
        
        if len(test_documentation.testing_strategy.split('\n')) > 10:
            console.print("   [italic]... (Full testing strategy saved to output file)[/italic]")
    
    # Environment requirements
    if test_documentation.test_environment_requirements:
        console.print(f"\n🔧 [bold]Test Environment Requirements:[/bold]")
        for req in test_documentation.test_environment_requirements[:8]:  # Show first 8
            console.print(f"   • {req}")
        
        if len(test_documentation.test_environment_requirements) > 8:
            console.print(f"   ... and {len(test_documentation.test_environment_requirements) - 8} more requirements")
    
    console.print(f"\n[bold green]✅ Test Generation Complete![/bold green]")
    console.print("[dim]Tip: Review the generated tests and customize them for your specific testing needs[/dim]")


def _display_analysis_results(analysis_result, config: AnalyzerConfig):
    """Display the analysis results."""
    
    console.print("\n" + "="*80)
    console.print(Panel(f"📋 Analysis Results for [bold blue]{analysis_result.repository.full_name}[/bold blue]", style="green"))
    console.print("="*80)
    
    # Repository summary
    console.print(f"\n📊 [bold]Repository Summary:[/bold]")
    console.print(f"   Description: {analysis_result.repository.description or 'No description available'}")
    console.print(f"   Language: {analysis_result.repository.language or 'Not specified'}")
    console.print(f"   Stars: {analysis_result.repository.stars}")
    console.print(f"   Forks: {analysis_result.repository.forks}")
    console.print(f"   Topics: {', '.join(analysis_result.repository.topics) if analysis_result.repository.topics else 'None'}")
    
    if analysis_result.focus_area:
        console.print(f"   Focus Area: {analysis_result.focus_area}")
    
    # Technology stack
    if analysis_result.tech_stack:
        console.print(f"\n🔧 [bold]Technology Stack:[/bold]")
        for tech in analysis_result.tech_stack:
            console.print(f"   • {tech}")
    
    # Key features
    if analysis_result.key_features:
        console.print(f"\n🎯 [bold]Key Features Identified:[/bold]")
        for feature in analysis_result.key_features[:5]:
            console.print(f"   • {feature}")
    
    # Target users
    if analysis_result.target_users:
        console.print(f"\n👥 [bold]Target Users:[/bold]")
        for user in analysis_result.target_users:
            console.print(f"   • {user}")
    
    # User stories
    console.print(f"\n📝 [bold]User Stories ({len(analysis_result.user_stories)}):[/bold]")
    
    for i, story in enumerate(analysis_result.user_stories, 1):
        console.print(f"\n🎯 [bold]Story {i}: {story.title}[/bold]")
        console.print(f"   {story.description}")
        
        if story.acceptance_criteria:
            console.print(f"   [bold]Acceptance Criteria:[/bold]")
            for criterion in story.acceptance_criteria:
                console.print(f"   • {criterion.description}")
        
        console.print(f"   [bold]Priority:[/bold] {story.priority.value}")
        console.print(f"   [bold]Effort:[/bold] {story.effort.value}")
        
        if story.tags:
            console.print(f"   [bold]Tags:[/bold] {', '.join(story.tags)}")
        
        console.print("   " + "-"*60)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
