#!/usr/bin/env python3
"""
Build Script for Gmail Filter Agent

Creates a standalone executable using PyInstaller that can be distributed
to users without requiring Python installation.

Usage:
    python build.py

Output:
    - dist/gmail-filter-agent (Unix/Mac) or dist/gmail-filter-agent.exe (Windows)
    - Distribution package ready for deployment

Features:
    - Single-file executable
    - All dependencies bundled
    - Platform-specific builds
    - Clean build process
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return os.path.dirname(os.path.abspath(__file__))


def clean_build_artifacts():
    """
    Clean up previous build artifacts.

    Removes:
    - build/ directory
    - dist/ directory
    - *.spec files
    - __pycache__ directories
    """
    project_root = get_project_root()

    artifacts = [
        os.path.join(project_root, 'build'),
        os.path.join(project_root, 'dist'),
        os.path.join(project_root, 'gmail-filter-agent.spec'),
    ]

    print("Cleaning build artifacts...")

    for artifact in artifacts:
        if os.path.exists(artifact):
            try:
                if os.path.isdir(artifact):
                    shutil.rmtree(artifact)
                    print(f"  Removed directory: {artifact}")
                else:
                    os.remove(artifact)
                    print(f"  Removed file: {artifact}")
            except Exception as e:
                print(f"  Warning: Could not remove {artifact}: {e}")

    # Remove __pycache__ directories
    for root, dirs, files in os.walk(project_root):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"  Removed: {pycache_path}")
            except Exception as e:
                print(f"  Warning: Could not remove {pycache_path}: {e}")

    print("Clean complete.\n")


def check_dependencies():
    """
    Check if required dependencies are installed.

    Returns:
        bool: True if all dependencies are installed
    """
    print("Checking dependencies...")

    required_packages = [
        'PyInstaller',
        'google.genai',
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient',
        'pandas',
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_').split('.')[0])
            print(f"  {package}: OK")
        except ImportError:
            print(f"  {package}: MISSING")
            missing_packages.append(package)

    if missing_packages:
        print("\nERROR: Missing dependencies. Please install:")
        print(f"  pip install -r requirements.txt")
        return False

    print("All dependencies installed.\n")
    return True


def build_executable():
    """
    Build the executable using PyInstaller.

    Returns:
        bool: True if build successful
    """
    project_root = get_project_root()
    agent_script = os.path.join(project_root, 'agent.py')

    print("Building executable with PyInstaller...")
    print(f"  Project root: {project_root}")
    print(f"  Script: {agent_script}\n")

    # PyInstaller command
    # --onefile: Create single executable
    # --name: Name of the executable
    # --add-data: Include additional files/directories
    # --hidden-import: Include modules not detected automatically
    # --clean: Clean cache before building

    pyinstaller_args = [
        'pyinstaller',
        '--onefile',
        '--name=gmail-filter-agent',
        '--clean',
        # Add tools directory
        f'--add-data=tools{os.pathsep}tools',
        # Hidden imports for Google libraries
        '--hidden-import=google.genai',
        '--hidden-import=google.auth',
        '--hidden-import=google.oauth2',
        '--hidden-import=google_auth_oauthlib',
        '--hidden-import=googleapiclient',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=dateutil',
        # Additional hidden imports for Gmail API
        '--hidden-import=google.auth.transport.requests',
        '--hidden-import=google_auth_oauthlib.flow',
        '--hidden-import=googleapiclient.discovery',
        '--hidden-import=googleapiclient.errors',
        # Script to build
        agent_script
    ]

    try:
        # Run PyInstaller
        result = subprocess.run(
            pyinstaller_args,
            cwd=project_root,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("ERROR: PyInstaller build failed")
            print("\nSTDOUT:")
            print(result.stdout)
            print("\nSTDERR:")
            print(result.stderr)
            return False

        print("Build successful!\n")
        return True

    except Exception as e:
        print(f"ERROR: Build failed: {e}")
        return False


def create_distribution_package():
    """
    Create distribution package with necessary files.

    Creates dist_package/ directory with:
    - Executable
    - README.txt
    - USER_INSTRUCTIONS.txt
    - csv_files/ directory
    - credentials.json.example
    """
    project_root = get_project_root()
    dist_dir = os.path.join(project_root, 'dist')
    package_dir = os.path.join(project_root, 'dist_package')

    print("Creating distribution package...")

    # Create package directory
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)

    os.makedirs(package_dir, exist_ok=True)

    # Determine executable name based on platform
    if sys.platform == 'win32':
        executable_name = 'gmail-filter-agent.exe'
    else:
        executable_name = 'gmail-filter-agent'

    executable_path = os.path.join(dist_dir, executable_name)

    # Copy executable
    if os.path.exists(executable_path):
        shutil.copy2(executable_path, package_dir)
        print(f"  Copied: {executable_name}")
    else:
        print(f"  Warning: Executable not found at {executable_path}")

    # Copy documentation files
    docs_to_copy = [
        'README.txt',
        'USER_INSTRUCTIONS.txt',
    ]

    for doc in docs_to_copy:
        src = os.path.join(project_root, doc)
        if os.path.exists(src):
            shutil.copy2(src, package_dir)
            print(f"  Copied: {doc}")
        else:
            print(f"  Warning: {doc} not found")

    # Create csv_files directory
    csv_dir = os.path.join(package_dir, 'csv_files')
    os.makedirs(csv_dir, exist_ok=True)
    print(f"  Created: csv_files/")

    # Create credentials.json.example
    credentials_example = os.path.join(package_dir, 'credentials.json.example')
    with open(credentials_example, 'w') as f:
        f.write("""{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
""")
    print(f"  Created: credentials.json.example")

    print(f"\nDistribution package created at: {package_dir}")
    print("\nPackage contents:")

    for root, dirs, files in os.walk(package_dir):
        level = root.replace(package_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{sub_indent}{file}")

    return package_dir


def main():
    """
    Main build process.
    """
    print("=" * 70)
    print("Gmail Filter Agent - Build Script")
    print("=" * 70)
    print()

    # Step 1: Clean previous builds
    clean_build_artifacts()

    # Step 2: Check dependencies
    if not check_dependencies():
        print("\nBuild aborted due to missing dependencies.")
        sys.exit(1)

    # Step 3: Build executable
    if not build_executable():
        print("\nBuild failed.")
        sys.exit(1)

    # Step 4: Create distribution package
    package_dir = create_distribution_package()

    # Success message
    print("\n" + "=" * 70)
    print("BUILD SUCCESSFUL!")
    print("=" * 70)
    print(f"\nExecutable location: dist/gmail-filter-agent")
    print(f"Distribution package: {package_dir}")
    print("\nNext steps:")
    print("1. Test the executable: ./dist/gmail-filter-agent")
    print("2. Distribute the dist_package/ directory to users")
    print("3. Users should follow USER_INSTRUCTIONS.txt for setup")
    print("\nFor more details, see BUILD_INSTRUCTIONS.md")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
