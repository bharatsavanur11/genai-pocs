#!/usr/bin/env python3
"""
Launcher script for the C4 Architecture Generator Chatbot

This script checks dependencies and launches the Streamlit chatbot interface.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'langchain',
        'langchain_openai',
        'openai',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements_chatbot.txt")
        return False
    
    return True

def check_api_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY environment variable not set")
        print("You can set it with: export OPENAI_API_KEY='your-key-here'")
        print("Or create a .env file with: OPENAI_API_KEY=your-key-here")
        return False
    
    print("✅ OPENAI_API_KEY is set")
    return True

def launch_chatbot():
    """Launch the Streamlit chatbot"""
    try:
        print("\n🚀 Launching C4 Architecture Generator Chatbot...")
        print("The chatbot will open in your default web browser")
        print("Press Ctrl+C to stop the chatbot\n")
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "c4_chatbot_ui.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Chatbot stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching chatbot: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🏗️  C4 Architecture Generator Chatbot Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        return 1
    
    print("\n🔑 Checking API key...")
    check_api_key()  # Warning only, don't fail
    
    print("\n" + "=" * 50)
    
    # Launch chatbot
    success = launch_chatbot()
    
    if not success:
        print("\n❌ Failed to launch chatbot")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
