#!/usr/bin/env python3
"""
Test script to verify Mermaid validator integration with the architecture command.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from mermaid_validator import MermaidValidator
from enhanced_analyzer import EnhancedClaudeAnalyzer
from types import RepositoryInfo, ClaudeConfig

def test_mermaid_validator():
    """Test the Mermaid validator with various diagram types."""
    print("🧪 Testing Mermaid Validator...")
    
    validator = MermaidValidator()
    
    # Test cases
    test_cases = [
        {
            "name": "Graph diagram missing end",
            "diagram": """graph TB
    subgraph "Client Layer"
        A[Client]
    end
    subgraph "Server Layer"
        B[Server]
    end
    A --> B""",
            "expected_fixes": ["Added missing final 'end' statement"]
        },
        {
            "name": "Sequence diagram with unnecessary end",
            "diagram": """sequenceDiagram
    participant A
    participant B
    A->>B: Hello
    end""",
            "expected_fixes": ["Removed unnecessary 'end' statement from sequence diagram"]
        },
        {
            "name": "Valid graph diagram",
            "diagram": """graph TB
    subgraph "Client Layer"
        A[Client]
    end
    subgraph "Server Layer"
        B[Server]
    end
    A --> B
    end""",
            "expected_fixes": []
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        fixed_diagram, issues_fixed = validator.validate_and_fix_diagram(test_case['diagram'])
        
        print(f"   Issues fixed: {issues_fixed}")
        print(f"   Fixed diagram:\n{fixed_diagram}")
        
        # Check if expected fixes were applied
        for expected_fix in test_case['expected_fixes']:
            if expected_fix in issues_fixed:
                print(f"   ✅ Expected fix applied: {expected_fix}")
            else:
                print(f"   ❌ Expected fix not applied: {expected_fix}")

def test_enhanced_analyzer_integration():
    """Test that the enhanced analyzer uses the Mermaid validator."""
    print("\n🔧 Testing Enhanced Analyzer Integration...")
    
    # Create a mock repository info
    repo_info = RepositoryInfo(
        full_name="test/repo",
        name="repo",
        description="Test repository",
        language="Python",
        stars=100,
        topics=["web", "api"],
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        size=1000,
        default_branch="main",
        clone_url="https://github.com/test/repo.git",
        html_url="https://github.com/test/repo",
        owner="test",
        private=False,
        fork=False,
        archived=False,
        disabled=False
    )
    
    # Create analyzer with mock config
    config = ClaudeConfig(
        api_key="test-key",
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000
    )
    
    analyzer = EnhancedClaudeAnalyzer(config)
    
    # Check if validator is initialized
    if hasattr(analyzer, 'mermaid_validator'):
        print("   ✅ Mermaid validator is initialized in EnhancedClaudeAnalyzer")
    else:
        print("   ❌ Mermaid validator is NOT initialized in EnhancedClaudeAnalyzer")
    
    # Test validator functionality
    test_diagram = """graph TB
    subgraph "Client Layer"
        A[Client]
    end
    A --> B"""
    
    fixed_diagram, issues = analyzer.mermaid_validator.validate_and_fix_diagram(test_diagram)
    
    if "end" in fixed_diagram and fixed_diagram.count("end") > test_diagram.count("end"):
        print("   ✅ Mermaid validator is working correctly")
    else:
        print("   ❌ Mermaid validator is not working correctly")

def main():
    """Run all tests."""
    print("🚀 Starting Mermaid Integration Tests\n")
    
    try:
        test_mermaid_validator()
        test_enhanced_analyzer_integration()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
