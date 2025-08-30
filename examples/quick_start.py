#!/usr/bin/env python3
"""
Quick start example for the GitHub Repository Analyzer.

This script demonstrates how to use the analyzer programmatically.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from github_repo_analyzer import analyze_repository_simple
from github_repo_analyzer.types import OutputFormat


async def main():
    """Main function demonstrating the analyzer."""
    
    print("🚀 GitHub Repository Analyzer - Quick Start Example")
    print("=" * 60)
    
    # Example 1: Basic analysis
    print("\n📋 Example 1: Basic Repository Analysis")
    print("-" * 40)
    
    try:
        result = await analyze_repository_simple(
            repo_owner="facebook",
            repo_name="react",
            max_stories=3,
            output_format=OutputFormat.TEXT
        )
        
        print(f"✅ Successfully analyzed {result.repository.full_name}")
        print(f"📊 Generated {len(result.user_stories)} user stories")
        print(f"🔧 Technology stack: {', '.join(result.tech_stack)}")
        
        # Display first user story
        if result.user_stories:
            story = result.user_stories[0]
            print(f"\n🎯 Sample User Story:")
            print(f"   Title: {story.title}")
            print(f"   Description: {story.description}")
            print(f"   Priority: {story.priority.value}")
            print(f"   Effort: {story.effort.value}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
    
    # Example 2: Focused analysis
    print("\n\n📋 Example 2: Focused Analysis")
    print("-" * 40)
    
    try:
        result = await analyze_repository_simple(
            repo_owner="microsoft",
            repo_name="vscode",
            focus_area="developer productivity",
            max_stories=2,
            output_format=OutputFormat.JSON
        )
        
        print(f"✅ Successfully analyzed {result.repository.full_name}")
        print(f"📊 Generated {len(result.user_stories)} user stories")
        print(f"🎯 Focus area: {result.focus_area}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
    
    # Example 3: Markdown output
    print("\n\n📋 Example 3: Markdown Output")
    print("-" * 40)
    
    try:
        result = await analyze_repository_simple(
            repo_owner="django",
            repo_name="django",
            max_stories=2,
            output_format=OutputFormat.MARKDOWN
        )
        
        print(f"✅ Successfully analyzed {result.repository.full_name}")
        print(f"📊 Generated {len(result.user_stories)} user stories")
        print(f"📝 Output format: {result.output_format}")
        
        # Save to file
        output_file = Path("django-user-stories.md")
        from github_repo_analyzer.output_formatter import OutputFormatter
        formatter = OutputFormatter(OutputFormat.MARKDOWN)
        formatter.save_to_file(result, output_file)
        print(f"💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
    
    print("\n🎉 Quick start examples completed!")
    print("\n💡 Tips:")
    print("   • Use a GitHub token for higher rate limits")
    print("   • Try different focus areas for varied results")
    print("   • Use different output formats for different use cases")


if __name__ == "__main__":
    asyncio.run(main())
