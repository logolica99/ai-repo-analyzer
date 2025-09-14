"""
Mermaid diagram validator and auto-fixer.

This module provides tools to validate and automatically fix Mermaid diagram syntax,
ensuring diagrams render correctly across different diagram types.
"""

import re
from typing import List, Tuple, Optional


class MermaidValidator:
    """Validates and fixes Mermaid diagram syntax."""
    
    def __init__(self):
        # Diagram types that use 'end' statements for subgraphs (only graph/flowchart)
        self.diagrams_requiring_end = {
            'graph', 'flowchart'
        }
        
        # Diagram types that don't use 'end' statements
        self.diagrams_not_requiring_end = {
            'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram',
            'userJourney', 'mindmap', 'timeline', 'quadrantChart', 'gitgraph', 
            'gantt', 'pie', 'journey'
        }
    
    def validate_and_fix_diagram(self, diagram: str) -> Tuple[str, List[str]]:
        """
        Validate and fix a Mermaid diagram.
        
        Args:
            diagram: The Mermaid diagram code as a string
            
        Returns:
            Tuple of (fixed_diagram, list_of_issues_fixed)
        """
        if not diagram or not diagram.strip():
            return diagram, []
        
        issues_fixed = []
        fixed_diagram = diagram.strip()
        
        # Detect diagram type
        diagram_type = self._detect_diagram_type(fixed_diagram)
        
        if not diagram_type:
            return fixed_diagram, ["Could not detect diagram type"]
        
        # Fix based on diagram type
        if diagram_type in self.diagrams_requiring_end:
            fixed_diagram, end_issues = self._fix_graph_diagram(fixed_diagram)
            issues_fixed.extend(end_issues)
        elif diagram_type in self.diagrams_not_requiring_end:
            fixed_diagram, syntax_issues = self._fix_sequence_diagram(fixed_diagram)
            issues_fixed.extend(syntax_issues)
        
        # General fixes that apply to all diagrams
        fixed_diagram, general_issues = self._apply_general_fixes(fixed_diagram)
        issues_fixed.extend(general_issues)
        
        return fixed_diagram, issues_fixed
    
    def _detect_diagram_type(self, diagram: str) -> Optional[str]:
        """Detect the type of Mermaid diagram."""
        lines = diagram.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('graph ') or line.startswith('flowchart '):
                return 'graph'
            elif line.startswith('sequenceDiagram'):
                return 'sequenceDiagram'
            elif line.startswith('classDiagram'):
                return 'classDiagram'
            elif line.startswith('stateDiagram'):
                return 'stateDiagram'
            elif line.startswith('erDiagram'):
                return 'erDiagram'
            elif line.startswith('gitgraph'):
                return 'gitgraph'
            elif line.startswith('gantt'):
                return 'gantt'
            elif line.startswith('pie'):
                return 'pie'
            elif line.startswith('journey'):
                return 'journey'
            elif line.startswith('userJourney'):
                return 'userJourney'
            elif line.startswith('mindmap'):
                return 'mindmap'
            elif line.startswith('timeline'):
                return 'timeline'
            elif line.startswith('quadrantChart'):
                return 'quadrantChart'
        
        return None
    
    def _fix_graph_diagram(self, diagram: str) -> Tuple[str, List[str]]:
        """Fix graph/flowchart diagrams that require 'end' statements."""
        issues_fixed = []
        lines = diagram.split('\n')
        fixed_lines = []
        subgraph_stack = []
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # Skip empty lines
            if not line:
                fixed_lines.append(original_line)
                continue
            
            # Skip comments
            if line.startswith('%%'):
                fixed_lines.append(original_line)
                continue
            
            # Check for subgraph start (more robust pattern)
            if re.match(r'subgraph\s+', line):
                subgraph_stack.append(line)
                fixed_lines.append(original_line)
            # Check for subgraph end
            elif line == 'end':
                if subgraph_stack:
                    subgraph_stack.pop()
                    fixed_lines.append(original_line)
                else:
                    # Remove unnecessary 'end' statement
                    issues_fixed.append("Removed unnecessary 'end' statement")
            else:
                fixed_lines.append(original_line)
        
        # Add missing 'end' statements for unclosed subgraphs
        while subgraph_stack:
            fixed_lines.append('    end')
            subgraph_stack.pop()
            issues_fixed.append("Added missing 'end' statement for subgraph")
        
        return '\n'.join(fixed_lines), issues_fixed
    
    def _fix_sequence_diagram(self, diagram: str) -> Tuple[str, List[str]]:
        """Fix sequence diagrams - they need 'end' for control blocks (alt/opt/loop/par)."""
        issues_fixed = []
        lines = diagram.split('\n')
        fixed_lines = []
        control_block_stack = []
        
        # Control structures in sequence diagrams that need 'end'
        control_keywords = ['alt', 'opt', 'loop', 'par', 'critical', 'break', 'rect']
        
        for line in lines:
            original_line = line
            stripped_line = line.strip()
            
            # Skip empty lines and comments
            if not stripped_line or stripped_line.startswith('%%'):
                fixed_lines.append(original_line)
                continue
            
            # Check for control block start (but not participant, note, etc.)
            if any(stripped_line.startswith(keyword + ' ') or stripped_line == keyword for keyword in control_keywords):
                control_block_stack.append(stripped_line)
                fixed_lines.append(original_line)
            # Check for else (part of alt block, doesn't close it)
            elif stripped_line.startswith('else'):
                fixed_lines.append(original_line)
            # Check for end statement
            elif stripped_line == 'end':
                if control_block_stack:
                    control_block_stack.pop()
                    fixed_lines.append(original_line)
                else:
                    # Remove unnecessary 'end' statement (not in a control block)
                    issues_fixed.append("Removed unnecessary 'end' statement outside control block")
                    # Don't add this line to fixed_lines - this removes the extra 'end'!
            else:
                fixed_lines.append(original_line)
        
        # Add missing 'end' statements for unclosed control blocks
        while control_block_stack:
            fixed_lines.append('    end')
            control_block_stack.pop()
            issues_fixed.append("Added missing 'end' statement for control block")
        
        return '\n'.join(fixed_lines), issues_fixed
    
    def _apply_general_fixes(self, diagram: str) -> Tuple[str, List[str]]:
        """Apply general fixes that work for all diagram types."""
        issues_fixed = []
        fixed_diagram = diagram
        
        # Fix common syntax issues with more careful patterns
        fixes = [
            # Fix malformed arrows (but preserve sequence diagram arrows)
            (r'(\w+)\s*-->>\s*(\w+)', r'\1 --> \2'),  # -->> to -->
            (r'(\w+)\s*-+>\s*(\w+)', r'\1 --> \2'),   # Multiple dashes to single -->
            
            # Fix missing spaces around arrows (but be more conservative)
            (r'(\w+)-->(\w+)', r'\1 --> \2'),
            (r'(\w+)-->(\w+)', r'\1 --> \2'),
            
            # Fix basic spacing issues
            (r'\s+-->\s+', ' --> '),  # Normalize spacing around arrows
            (r'\s+->\s+', ' -> '),    # Normalize spacing around single arrows
            
            # Fix node definitions (more conservative)
            (r'(\w+)\s*\[\s*([^\]]*)\s*\]', r'\1[\2]'),  # Clean up node brackets
            (r'(\w+)\s*\(\s*([^)]*)\s*\)', r'\1(\2)'),   # Clean up node parentheses
        ]
        
        for pattern, replacement in fixes:
            original_diagram = fixed_diagram
            fixed_diagram = re.sub(pattern, replacement, fixed_diagram)
            if fixed_diagram != original_diagram:
                issues_fixed.append(f"Fixed spacing/syntax pattern")
        
        # Clean up excessive whitespace but preserve structure
        lines = fixed_diagram.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Preserve indentation but clean trailing spaces
            cleaned_line = line.rstrip()
            cleaned_lines.append(cleaned_line)
        
        # Remove excessive empty lines at the end
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        fixed_diagram = '\n'.join(cleaned_lines)
        
        # Don't force a final newline - let the original formatting decide
        if diagram.endswith('\n') and not fixed_diagram.endswith('\n'):
            fixed_diagram += '\n'
        
        return fixed_diagram, issues_fixed
    
    def validate_diagram_syntax(self, diagram: str) -> Tuple[bool, List[str]]:
        """
        Validate Mermaid diagram syntax without fixing.
        
        Args:
            diagram: The Mermaid diagram code as a string
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        if not diagram or not diagram.strip():
            return False, ["Empty diagram"]
        
        issues = []
        lines = diagram.split('\n')
        diagram_type = self._detect_diagram_type(diagram)
        
        if not diagram_type:
            issues.append("Could not detect diagram type")
            return False, issues
        
        # Check for basic syntax issues based on diagram type
        if diagram_type in self.diagrams_requiring_end:
            # Only graph and flowchart need proper subgraph/end matching
            subgraph_count = 0
            end_count = 0
            
            for line in lines:
                stripped_line = line.strip()
                if re.match(r'subgraph\s+', stripped_line):
                    subgraph_count += 1
                elif stripped_line == 'end':
                    end_count += 1
            
            if subgraph_count != end_count:
                if subgraph_count > end_count:
                    issues.append(f"Missing {subgraph_count - end_count} 'end' statement(s) for subgraphs")
                else:
                    issues.append(f"Extra {end_count - subgraph_count} 'end' statement(s)")
        
        elif diagram_type in self.diagrams_not_requiring_end:
            # Special case for sequence diagrams - they need 'end' for control blocks
            if diagram_type == 'sequenceDiagram':
                control_keywords = ['alt', 'opt', 'loop', 'par', 'critical', 'break', 'rect']
                control_block_count = 0
                end_count = 0
                
                for line in lines:
                    stripped_line = line.strip()
                    if any(stripped_line.startswith(keyword + ' ') or stripped_line == keyword for keyword in control_keywords):
                        control_block_count += 1
                    elif stripped_line == 'end':
                        end_count += 1
                
                if control_block_count != end_count:
                    if control_block_count > end_count:
                        issues.append(f"Missing {control_block_count - end_count} 'end' statement(s) for control blocks")
                    else:
                        issues.append(f"Extra {end_count - control_block_count} 'end' statement(s)")
            else:
                # Other diagrams should not have 'end' statements at all
                for line in lines:
                    if line.strip() == 'end':
                        issues.append(f"Unnecessary 'end' statement in {diagram_type}")
        
        # Check for malformed syntax (more conservative)
        malformed_patterns = [
            (r'(\w+)\s*-->>\s*(\w+)', "Double arrow -->> should be -->"),
            (r'(\w+)\s*-{3,}>\s*(\w+)', "Multiple dash arrows should be -->"),
            (r'(\w+)-->(\w+)', "Missing spaces around arrow"),
        ]
        
        for pattern, message in malformed_patterns:
            if re.search(pattern, diagram):
                issues.append(message)
        
        return len(issues) == 0, issues
    
    def get_diagram_preview(self, diagram: str, max_lines: int = 10) -> str:
        """
        Get a preview of the diagram for debugging.
        
        Args:
            diagram: The Mermaid diagram code
            max_lines: Maximum number of lines to show
            
        Returns:
            Preview string
        """
        lines = diagram.split('\n')
        preview_lines = lines[:max_lines]
        
        if len(lines) > max_lines:
            preview_lines.append(f"... ({len(lines) - max_lines} more lines)")
        
        return '\n'.join(preview_lines)


def validate_mermaid_diagram(diagram: str) -> Tuple[str, List[str]]:
    """
    Convenience function to validate and fix a Mermaid diagram.
    
    Args:
        diagram: The Mermaid diagram code as a string
        
    Returns:
        Tuple of (fixed_diagram, list_of_issues_fixed)
    """
    validator = MermaidValidator()
    return validator.validate_and_fix_diagram(diagram)


def quick_validate(diagram: str) -> bool:
    """
    Quick validation without fixing.
    
    Args:
        diagram: The Mermaid diagram code as a string
        
    Returns:
        True if valid, False otherwise
    """
    validator = MermaidValidator()
    is_valid, _ = validator.validate_diagram_syntax(diagram)
    return is_valid
