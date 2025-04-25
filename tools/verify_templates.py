"""
Template verification script.
This script parses all templates and checks for syntax errors.
"""
import os
import sys
import re
from jinja2 import Environment, FileSystemLoader, exceptions

def check_template_syntax(template_dir):
    """
    Check all templates in the given directory for syntax errors.
    
    Args:
        template_dir: Path to the directory containing templates
        
    Returns:
        Tuple of (success_count, error_count, error_files)
    """
    env = Environment(loader=FileSystemLoader(template_dir))
    success_count = 0
    error_count = 0
    error_files = []
    
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                template_path = os.path.join(root, file)
                rel_path = os.path.relpath(template_path, template_dir)
                
                try:
                    template_source = open(template_path, 'r', encoding='utf-8').read()
                    env.parse(template_source)
                    print(f"✅ Template syntax OK: {rel_path}")
                    success_count += 1
                except exceptions.TemplateSyntaxError as e:
                    print(f"❌ Syntax error in {rel_path}, line {e.lineno}: {e.message}")
                    error_count += 1
                    error_files.append((rel_path, e.lineno, e.message))
                except UnicodeDecodeError:
                    print(f"❌ Unicode decode error in {rel_path}")
                    error_count += 1
                    error_files.append((rel_path, 0, "Unicode decode error"))
                except Exception as e:
                    print(f"❌ Error checking {rel_path}: {str(e)}")
                    error_count += 1
                    error_files.append((rel_path, 0, str(e)))
    
    return success_count, error_count, error_files

def check_for_common_template_issues(template_dir):
    """
    Check for common template issues like mismatched if/endif, for/endfor, etc.
    
    Args:
        template_dir: Path to the directory containing templates
        
    Returns:
        List of (file_path, line_number, issue_description)
    """
    issues = []
    
    # Define patterns to check
    patterns = [
        (r'{%\s*if\s+.*?="".*?%}', 'Suspicious if condition with "="'),
        (r'{%\s*for\s+.*?="".*?%}', 'Suspicious for loop with "="'),
        (r'{{.*?}}}}', 'Possible unescaped closing braces'),
        (r'{{\s*(\w+)\s*}}.*?{{\s*\1\s*}}', 'Duplicate variable in same line')
    ]
    
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                template_path = os.path.join(root, file)
                rel_path = os.path.relpath(template_path, template_dir)
                
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines, 1):
                            for pattern, description in patterns:
                                if re.search(pattern, line):
                                    issues.append((rel_path, i, f"{description}: {line.strip()}"))
                                    print(f"⚠️ {rel_path}, line {i}: {description}")
                except Exception as e:
                    print(f"❌ Error analyzing {rel_path}: {str(e)}")
    
    return issues

if __name__ == "__main__":
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    
    print(f"Checking template syntax in {template_dir}...")
    success_count, error_count, error_files = check_template_syntax(template_dir)
    
    print("\nChecking for common template issues...")
    issues = check_for_common_template_issues(template_dir)
    
    print("\nResults:")
    print(f"Total templates checked: {success_count + error_count}")
    print(f"Templates with syntax errors: {error_count}")
    print(f"Templates with potential issues: {len(issues)}")
    
    if error_count > 0 or issues:
        print("\nIssues found:")
        
        if error_count > 0:
            print("\nSyntax errors:")
            for file, line, message in error_files:
                print(f"  - {file}, line {line}: {message}")
        
        if issues:
            print("\nPotential issues:")
            for file, line, message in issues:
                print(f"  - {file}, line {line}: {message}")
        
        sys.exit(1)
    else:
        print("\nAll templates look good!")
        sys.exit(0)