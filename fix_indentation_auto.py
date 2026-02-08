import ast
import sys

def fix_indentation(file_path):
    """Fix indentation issues in Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse and format the AST
        tree = ast.parse(content)
        
        # Write back with proper indentation
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(ast.unparse(tree))
        
        print(f"Fixed indentation in {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

if __name__ == "__main__":
    file_path = "browser.py"
    if fix_indentation(file_path):
        print("Indentation fixed successfully!")
    else:
        print("Failed to fix indentation")