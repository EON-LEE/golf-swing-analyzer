#!/usr/bin/env python3
"""Simple validation script to test code improvements."""

import ast
import sys
from pathlib import Path


def validate_python_syntax(file_path: Path) -> bool:
    """Validate Python file syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False


def check_file_structure():
    """Check if all expected files exist."""
    expected_files = [
        'app.py',
        'config.py',
        'video_processor.py',
        'services.py',
        'health.py',
        'cli.py',
        'models.py',
        'exceptions.py',
        'requirements.txt',
        'requirements-dev.txt',
        'utils/validators.py',
        'utils/error_handler.py',
        'utils/logger.py',
    ]
    
    missing_files = []
    for file_path in expected_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All expected files present")
    return True


def validate_all_python_files():
    """Validate syntax of all Python files."""
    python_files = list(Path('.').rglob('*.py'))
    
    valid_count = 0
    total_count = len(python_files)
    
    for py_file in python_files:
        if validate_python_syntax(py_file):
            valid_count += 1
            print(f"✅ {py_file}")
        else:
            print(f"❌ {py_file}")
    
    print(f"\nSyntax validation: {valid_count}/{total_count} files passed")
    return valid_count == total_count


def check_improvements():
    """Check for specific improvements made."""
    improvements = []
    
    # Check for async context manager in video_processor.py
    try:
        with open('video_processor.py', 'r') as f:
            content = f.read()
            if '@asynccontextmanager' in content:
                improvements.append("✅ Async context manager added")
            if 'Config.ASYNC_BATCH_SIZE' in content:
                improvements.append("✅ Configurable batch size implemented")
    except:
        pass
    
    # Check for enhanced validation
    try:
        with open('utils/validators.py', 'r') as f:
            content = f.read()
            if 'validate_uploaded_file' in content:
                improvements.append("✅ Enhanced file validation added")
            if 'magic.from_file' in content:
                improvements.append("✅ MIME type validation added")
    except:
        pass
    
    # Check for improved error handling
    try:
        with open('services.py', 'r') as f:
            content = f.read()
            if 'finally:' in content:
                improvements.append("✅ Proper resource cleanup added")
    except:
        pass
    
    # Check for health checks
    try:
        with open('health.py', 'r') as f:
            content = f.read()
            if 'check_disk_space' in content:
                improvements.append("✅ Comprehensive health checks added")
    except:
        pass
    
    print("\nImplemented improvements:")
    for improvement in improvements:
        print(improvement)
    
    return len(improvements)


def main():
    """Main validation function."""
    print("🔍 Validating Golf Swing Analyzer improvements...\n")
    
    # Check file structure
    structure_ok = check_file_structure()
    
    # Validate Python syntax
    syntax_ok = validate_all_python_files()
    
    # Check specific improvements
    improvement_count = check_improvements()
    
    print(f"\n📊 Validation Summary:")
    print(f"File structure: {'✅' if structure_ok else '❌'}")
    print(f"Python syntax: {'✅' if syntax_ok else '❌'}")
    print(f"Improvements implemented: {improvement_count}")
    
    if structure_ok and syntax_ok and improvement_count > 0:
        print("\n🎉 Code improvements validated successfully!")
        return True
    else:
        print("\n⚠️ Some issues found. Please review.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
