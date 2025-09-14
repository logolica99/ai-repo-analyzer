#!/usr/bin/env python3
"""
Simple test for Mermaid validator functionality.
"""

from mermaid_validator import MermaidValidator

def test_mermaid_validator():
    """Test the Mermaid validator with various diagram types."""
    print("🧪 Testing Mermaid Validator...")
    
    validator = MermaidValidator()
    
    # Test case 1: Graph diagram missing end
    print("\n📋 Test 1: Graph diagram missing end")
    diagram1 = """graph TB
    subgraph "Client Layer"
        A[Client]
    end
    subgraph "Server Layer"
        B[Server]
    end
    A --> B"""
    
    fixed_diagram1, issues1 = validator.validate_and_fix_diagram(diagram1)
    print(f"   Issues fixed: {issues1}")
    print(f"   Fixed diagram:\n{fixed_diagram1}")
    
    # Test case 2: Sequence diagram with unnecessary end
    print("\n📋 Test 2: Sequence diagram with unnecessary end")
    diagram2 = """sequenceDiagram
    participant A
    participant B
    A->>B: Hello
    end"""
    
    fixed_diagram2, issues2 = validator.validate_and_fix_diagram(diagram2)
    print(f"   Issues fixed: {issues2}")
    print(f"   Fixed diagram:\n{fixed_diagram2}")
    
    # Test case 3: Valid graph diagram
    print("\n📋 Test 3: Valid graph diagram")
    diagram3 = """graph TB
    subgraph "Client Layer"
        A[Client]
    end
    subgraph "Server Layer"
        B[Server]
    end
    A --> B
    end"""
    
    fixed_diagram3, issues3 = validator.validate_and_fix_diagram(diagram3)
    print(f"   Issues fixed: {issues3}")
    print(f"   Fixed diagram:\n{fixed_diagram3}")
    
    print("\n✅ Mermaid validator test completed!")

if __name__ == "__main__":
    test_mermaid_validator()
