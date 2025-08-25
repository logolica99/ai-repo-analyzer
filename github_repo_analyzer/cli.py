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
from .types import OutputFormat, AnalyzerConfig
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
@click.pass_context
def analyze(ctx, repo, token, focus, max_stories, output_format, output_file, system_prompt, config_file):
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
