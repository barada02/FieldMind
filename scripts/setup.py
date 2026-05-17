#!/usr/bin/env python3
"""
Field Mind Setup Script
Initializes the project structure and validates configuration
"""

import os
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories for the project."""
    directories = [
        "data/sops",
        "data/chromadb",
        "logs",
        "backend/app/api",
        "backend/agent",
        "backend/rag",
        "backend/mcp_server/tools",
        "frontend/css",
        "frontend/js",
        "tests",
        "scripts"
    ]
    
    print("Creating project directories...")
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print("\n✅ Directories created successfully!")


def check_env_file():
    """Check if .env file exists and guide user."""
    env_example = Path("backend/.env.example")
    env_file = Path("backend/.env")
    
    print("\nChecking environment configuration...")
    
    if not env_file.exists():
        if env_example.exists():
            print("  ⚠️  .env file not found")
            print(f"  📝 Please copy {env_example} to {env_file}")
            print("     and update with your credentials:")
            print()
            print("     cp backend/.env.example backend/.env")
            print()
            return False
        else:
            print("  ❌ .env.example file not found!")
            return False
    else:
        print("  ✓ .env file exists")
        return True


def check_python_version():
    """Check if Python version meets requirements."""
    print("\nChecking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"  ❌ Python 3.10+ required (found {version.major}.{version.minor})")
        return False
    else:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True


def check_requirements():
    """Check if requirements.txt exists."""
    print("\nChecking requirements...")
    req_file = Path("backend/requirements.txt")
    
    if not req_file.exists():
        print("  ❌ requirements.txt not found!")
        return False
    else:
        print("  ✓ requirements.txt exists")
        print("\n  To install dependencies, run:")
        print("     pip install -r backend/requirements.txt")
        return True


def create_gitignore():
    """Create .gitignore file if it doesn't exist."""
    gitignore_path = Path(".gitignore")
    
    if gitignore_path.exists():
        print("\n✓ .gitignore already exists")
        return
    
    print("\nCreating .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Data
data/chromadb/
*.db

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Build
dist/
build/
*.egg-info/
"""
    
    gitignore_path.write_text(gitignore_content)
    print("  ✓ .gitignore created")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:\n")
    print("1. Configure your environment:")
    print("   - Edit backend/.env with your credentials")
    print("   - Add OpenAI API key")
    print("   - Add IBM Cloudant credentials")
    print()
    print("2. Install dependencies:")
    print("   pip install -r backend/requirements.txt")
    print()
    print("3. Start the application:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload --port 8000")
    print()
    print("4. Open your browser:")
    print("   http://localhost:8000")
    print()
    print("📚 Documentation:")
    print("   - README.md - Quick start guide")
    print("   - Plandocs/PROJECT_PLAN.md - Full project plan")
    print("   - Plandocs/ARCHITECTURE.md - System architecture")
    print()
    print("="*60)


def main():
    """Main setup function."""
    print("="*60)
    print("Field Mind - Setup Script")
    print("="*60)
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"\nProject root: {project_root}")
    
    # Run setup steps
    checks_passed = True
    
    if not check_python_version():
        checks_passed = False
    
    create_directories()
    create_gitignore()
    
    if not check_requirements():
        checks_passed = False
    
    if not check_env_file():
        checks_passed = False
    
    # Print next steps
    print_next_steps()
    
    if not checks_passed:
        print("\n⚠️  Some checks failed. Please address the issues above.")
        sys.exit(1)
    else:
        print("\n✅ All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

# Made with Bob
