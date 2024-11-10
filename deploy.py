#!/usr/bin/env python3
"""
Deployment script for Mobile Price Predictor application.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("❌ Python 3.7+ is required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if pip is available
    try:
        import pip
        print("✅ pip is available")
    except ImportError:
        print("❌ pip is not available")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    result = run_command("pip install -r requirements.txt", "Installing Python packages")
    return result is not None

def setup_environment():
    """Set up environment variables."""
    print("🌍 Setting up environment...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        if os.path.exists("env_example.txt"):
            with open("env_example.txt", "r") as f:
                content = f.read()
            with open(".env", "w") as f:
                f.write(content)
            print("✅ .env file created")
        else:
            print("⚠️  env_example.txt not found, creating basic .env file...")
            with open(".env", "w") as f:
                f.write("FLASK_DEBUG=False\nSECRET_KEY=dev-secret-key\n")
            print("✅ Basic .env file created")
    else:
        print("✅ .env file already exists")

def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    
    if os.path.exists("test_app.py"):
        result = run_command("python -m pytest test_app.py -v", "Running test suite")
        return result is not None
    else:
        print("⚠️  No test files found, skipping tests")
        return True

def start_application():
    """Start the Flask application."""
    print("🚀 Starting application...")
    print("📱 Mobile Price Predictor will be available at: http://localhost:80")
    print("⏹️  Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main deployment function."""
    print("🚀 Mobile Price Predictor - Deployment Script")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install required dependencies.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies.")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed. Please fix issues before deployment.")
        sys.exit(1)
    
    # Start application
    start_application()

if __name__ == "__main__":
    main() 