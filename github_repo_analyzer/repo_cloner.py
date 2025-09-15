"""
Repository cloner and file analyzer for deep code analysis.
"""

import os
import tempfile
import shutil
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import asyncio
import aiofiles

from .types import RepositoryInfo


class RepositoryCloner:
    """Handles cloning and analyzing repository files."""
    
    def __init__(self):
        self.temp_dirs = []  # Track temp directories for cleanup
    
    async def clone_and_analyze_repository(
        self, 
        repo_info: RepositoryInfo, 
        github_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Clone repository and analyze its files."""
        
        # Create temporary directory for cloning
        temp_dir = tempfile.mkdtemp(prefix=f"repo_analysis_{repo_info.name}_")
        self.temp_dirs.append(temp_dir)
        
        try:
            # Clone the repository
            repo_path = await self._clone_repository(repo_info, temp_dir, github_token)
            
            if not repo_path:
                return {"error": "Failed to clone repository"}
            
            # Analyze the cloned repository
            analysis = await self._analyze_repository_files(repo_path, repo_info)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def _clone_repository(
        self, 
        repo_info: RepositoryInfo, 
        temp_dir: str, 
        github_token: Optional[str] = None
    ) -> Optional[str]:
        """Clone the repository to a temporary directory."""
        
        try:
            # Construct clone URL
            if github_token:
                clone_url = f"https://{github_token}@github.com/{repo_info.full_name}.git"
            else:
                clone_url = f"https://github.com/{repo_info.full_name}.git"
            
            # Clone the repository
            repo_path = os.path.join(temp_dir, repo_info.name)
            
            # Use git clone command
            cmd = [
                "git", "clone", 
                "--depth", "1",  # Shallow clone for faster download
                clone_url, 
                repo_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return repo_path
            else:
                print(f"Git clone failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("Git clone timed out")
            return None
        except Exception as e:
            print(f"Git clone error: {e}")
            return None
    
    async def _analyze_repository_files(self, repo_path: str, repo_info: RepositoryInfo) -> Dict[str, Any]:
        """Analyze the files in the cloned repository."""
        
        analysis = {
            "repository_path": repo_path,
            "files": [],
            "file_types": {},
            "total_files": 0,
            "total_size": 0,
            "languages": {},
            "code_files": [],
            "config_files": [],
            "test_files": [],
            "documentation_files": [],
            "dependencies": [],
            "structure": {}
        }
        
        try:
            # Walk through the repository directory
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'build', 'dist']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    # Skip hidden files and common ignore patterns
                    if file.startswith('.') or file in ['package-lock.json', 'yarn.lock', 'poetry.lock']:
                        continue
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        file_info = {
                            "path": relative_path,
                            "size": file_size,
                            "extension": file_ext,
                            "is_binary": self._is_binary_file(file_path)
                        }
                        
                        analysis["files"].append(file_info)
                        analysis["total_files"] += 1
                        analysis["total_size"] += file_size
                        
                        # Categorize files
                        self._categorize_file(file_info, analysis)
                        
                        # Analyze file content if it's a text file
                        if not file_info["is_binary"] and file_size < 1024 * 1024:  # Less than 1MB
                            content = await self._read_file_content(file_path)
                            if content:
                                file_info["content"] = content
                                file_info["lines"] = len(content.split('\n'))
                                file_info["language"] = self._detect_language(file_ext, content)
                                
                                # Update language statistics
                                lang = file_info["language"]
                                if lang not in analysis["languages"]:
                                    analysis["languages"][lang] = {"files": 0, "lines": 0}
                                analysis["languages"][lang]["files"] += 1
                                analysis["languages"][lang]["lines"] += file_info["lines"]
                        
                    except Exception as e:
                        print(f"Error analyzing file {file_path}: {e}")
                        continue
            
            # Analyze repository structure
            analysis["structure"] = self._analyze_repository_structure(repo_path)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing repository: {e}")
            return analysis
    
    def _categorize_file(self, file_info: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Categorize files by type and purpose."""
        
        path = file_info["path"].lower()
        ext = file_info["extension"]
        
        # Code files
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.cpp', '.c', '.cs', '.php', '.rb', '.swift', '.kt', '.scala'}
        if ext in code_extensions:
            analysis["code_files"].append(file_info)
        
        # Test files
        if any(test_indicator in path for test_indicator in ['test', 'spec', '__test__', 'tests']):
            analysis["test_files"].append(file_info)
        
        # Documentation files
        doc_extensions = {'.md', '.rst', '.txt', '.adoc'}
        doc_names = {'readme', 'changelog', 'contributing', 'license', 'authors', 'news'}
        if ext in doc_extensions or any(doc_name in path for doc_name in doc_names):
            analysis["documentation_files"].append(file_info)
        
        # Config files
        config_files = {
            'package.json', 'requirements.txt', 'pyproject.toml', 'setup.py', 'pom.xml',
            'build.gradle', 'cargo.toml', 'composer.json', 'gemfile', 'go.mod',
            'dockerfile', 'docker-compose.yml', '.gitignore', '.env', 'config.json'
        }
        if file_info["path"].split('/')[-1].lower() in config_files:
            analysis["config_files"].append(file_info)
    
    def _is_binary_file(self, file_path: str) -> bool:
        """Check if a file is binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except:
            return True
    
    async def _read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content safely."""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                    return await f.read()
            except:
                return None
        except Exception:
            return None
    
    def _detect_language(self, extension: str, content: str) -> str:
        """Detect programming language from file extension and content."""
        
        # Extension-based detection
        ext_lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.less': 'Less',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.md': 'Markdown',
            '.rst': 'reStructuredText',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.zsh': 'Zsh',
            '.fish': 'Fish',
            '.sql': 'SQL',
            '.dockerfile': 'Dockerfile',
            '.makefile': 'Makefile'
        }
        
        if extension in ext_lang_map:
            return ext_lang_map[extension]
        
        # Content-based detection for ambiguous cases
        content_lower = content.lower()
        
        if '#!/bin/bash' in content_lower or '#!/usr/bin/env bash' in content_lower:
            return 'Bash'
        elif '#!/bin/sh' in content_lower:
            return 'Shell'
        elif '#!/usr/bin/env python' in content_lower:
            return 'Python'
        elif '#!/usr/bin/env node' in content_lower:
            return 'JavaScript'
        
        return 'Unknown'
    
    def _analyze_repository_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze the overall repository structure."""
        
        structure = {
            "has_src": False,
            "has_tests": False,
            "has_docs": False,
            "has_config": False,
            "has_scripts": False,
            "has_examples": False,
            "has_docker": False,
            "has_ci": False,
            "main_directories": [],
            "depth": 0
        }
        
        try:
            # Check for common directory patterns
            for root, dirs, files in os.walk(repo_path):
                relative_root = os.path.relpath(root, repo_path)
                
                if relative_root == '.':
                    structure["main_directories"] = [d for d in dirs if not d.startswith('.')]
                
                # Check for specific patterns
                dir_name = os.path.basename(root).lower()
                if any(pattern in dir_name for pattern in ['src', 'source', 'lib', 'app']):
                    structure["has_src"] = True
                elif any(pattern in dir_name for pattern in ['test', 'tests', 'spec', 'specs']):
                    structure["has_tests"] = True
                elif any(pattern in dir_name for pattern in ['doc', 'docs', 'documentation']):
                    structure["has_docs"] = True
                elif any(pattern in dir_name for pattern in ['config', 'conf', 'settings']):
                    structure["has_config"] = True
                elif any(pattern in dir_name for pattern in ['script', 'scripts', 'bin']):
                    structure["has_scripts"] = True
                elif any(pattern in dir_name for pattern in ['example', 'examples', 'demo', 'demos']):
                    structure["has_examples"] = True
                elif any(pattern in dir_name for pattern in ['docker', 'container']):
                    structure["has_docker"] = True
                elif any(pattern in dir_name for pattern in ['ci', 'cd', '.github', '.gitlab-ci']):
                    structure["has_ci"] = True
                
                # Calculate depth
                depth = len(relative_root.split(os.sep)) - 1
                structure["depth"] = max(structure["depth"], depth)
        
        except Exception as e:
            print(f"Error analyzing structure: {e}")
        
        return structure
    
    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Error cleaning up {temp_dir}: {e}")
        self.temp_dirs.clear()
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()
