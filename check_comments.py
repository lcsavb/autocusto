#!/usr/bin/env python3
"""
Script to check for # comments above classes, functions, and variables
in Python files to identify where English translations might be needed.
"""

import os
import ast

class CommentChecker(ast.NodeVisitor):
    def __init__(self, source_lines, filename):
        self.source_lines = source_lines
        self.filename = filename
        self.missing_comments = []
        
    def has_comment_above(self, lineno):
        """Check if there's a # comment on the line above the given line number"""
        if lineno <= 1:
            return False
        
        # Check the line above (lineno-2 because lines are 0-indexed)
        prev_line = self.source_lines[lineno - 2].strip()
        return prev_line.startswith('#') and not prev_line.startswith('##')
    
    def visit_ClassDef(self, node):
        """Check classes for comments above"""
        if not self.has_comment_above(node.lineno):
            self.missing_comments.append({
                'type': 'class',
                'name': node.name,
                'line': node.lineno,
                'code': self.source_lines[node.lineno - 1].strip()
            })
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Check functions for comments above"""
        # Skip magic methods and private methods starting with _
        if not node.name.startswith('_'):
            if not self.has_comment_above(node.lineno):
                self.missing_comments.append({
                    'type': 'function',
                    'name': node.name,
                    'line': node.lineno,
                    'code': self.source_lines[node.lineno - 1].strip()
                })
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Check async functions for comments above"""
        if not node.name.startswith('_'):
            if not self.has_comment_above(node.lineno):
                self.missing_comments.append({
                    'type': 'async function',
                    'name': node.name,
                    'line': node.lineno,
                    'code': self.source_lines[node.lineno - 1].strip()
                })
        self.generic_visit(node)

def check_python_file(file_path):
    """Check a single Python file for missing comments"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
            source_lines = source.splitlines()
        
        tree = ast.parse(source)
        checker = CommentChecker(source_lines, file_path)
        checker.visit(tree)
        
        return checker.missing_comments
    
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def find_python_files(directory):
    """Find all Python files in the directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip common directories we don't want to check
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env', 'node_modules', 'migrations', 'static', 'static_root']]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """Main function to check all Python files"""
    base_dir = '/home/lucas/code/autocusto'
    
    print("🔍 Checking Python files for missing # comments above classes/functions...")
    print("="*80)
    
    python_files = find_python_files(base_dir)
    total_missing = 0
    
    for file_path in sorted(python_files):
        relative_path = os.path.relpath(file_path, base_dir)
        missing_comments = check_python_file(file_path)
        
        if missing_comments:
            print(f"\n📁 {relative_path}")
            print("-" * len(relative_path))
            
            for item in missing_comments:
                total_missing += 1
                print(f"  Line {item['line']:3d}: {item['type']} '{item['name']}'")
    
    # Summary
    print("="*80)
    print(f"📊 SUMMARY: Found {total_missing} items without # comments above them")
    print("Now I'll review each one and add English translations where needed...")

if __name__ == "__main__":
    main()