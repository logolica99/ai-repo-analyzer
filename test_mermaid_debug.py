#!/usr/bin/env python3
"""
Debug script to test Mermaid validation integration.
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from github_repo_analyzer.mermaid_validator import MermaidValidator
from github_repo_analyzer.enhanced_analyzer import EnhancedClaudeAnalyzer
from github_repo_analyzer.types import RepositoryInfo, ClaudeConfig

def test_diagram_validation():
    """Test diagram validation with various scenarios."""
    print("🧪 Testing Mermaid Diagram Validation...")
    
    validator = MermaidValidator()
    
    # Test case 1: Diagram missing end statement
    print("\n📋 Test 1: Diagram missing end statement")
    diagram1 = """graph TB
    subgraph "Client Layer"
        A[Client]
    end
    A --> B"""
    
    print("Original:")
    print(diagram1)
    print()
    
    fixed1, issues1 = validator.validate_and_fix_diagram(diagram1)
    print("Fixed:")
    print(fixed1)
    print("Issues:", issues1)
    print()
    
    # Test case 2: Diagram with proper end statement
    print("📋 Test 2: Diagram with proper end statement")
    diagram2 = """graph TB
    subgraph "Client Layer"
        A[Client]
    end
    A --> B
    end"""
    
    print("Original:")
    print(diagram2)
    print()
    
    fixed2, issues2 = validator.validate_and_fix_diagram(diagram2)
    print("Fixed:")
    print(fixed2)
    print("Issues:", issues2)
    print()
    
    # Test case 3: Sequence diagram with unnecessary end
    print("📋 Test 3: Sequence diagram with unnecessary end")
    diagram3 = """sequenceDiagram
    participant A
    participant B
    A->>B: Hello
    end"""
    
    print("Original:")
    print(diagram3)
    print()
    
    fixed3, issues3 = validator.validate_and_fix_diagram(diagram3)
    print("Fixed:")
    print(fixed3)
    print("Issues:", issues3)
    print()

def test_enhanced_analyzer():
    """Test the enhanced analyzer with Mermaid validation."""
    print("\n🔧 Testing Enhanced Analyzer with Mermaid Validation...")
    
    # Create analyzer with default config
    config = ClaudeConfig()
    analyzer = EnhancedClaudeAnalyzer(config)
    
    # Test the Mermaid validator directly
    print("Testing Mermaid validator integration...")
    
    # Test a diagram that should be fixed
    test_diagram = """graph TB
    subgraph "Client Layer"
        A[Client]
    end
    A --> B"""
    
    print("Original diagram:")
    print(test_diagram)
    print()
    
    # Use the analyzer's validator
    fixed_diagram, issues = analyzer.mermaid_validator.validate_and_fix_diagram(test_diagram)
    
    print("Fixed diagram:")
    print(fixed_diagram)
    print()
    print("Issues fixed:", issues)
    print()
    
    # Check if the validator is working correctly
    if "end" in fixed_diagram and fixed_diagram.count("end") > test_diagram.count("end"):
        print("✅ Mermaid validator is working correctly in EnhancedClaudeAnalyzer")
    else:
        print("❌ Mermaid validator is not working correctly in EnhancedClaudeAnalyzer")

def main():
    """Run all tests."""
    print("🚀 Starting Mermaid Validation Debug Tests\n")
    
    try:
        test_diagram_validation()
        test_enhanced_analyzer()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
