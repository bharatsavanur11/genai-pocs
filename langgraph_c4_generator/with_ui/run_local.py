#!/usr/bin/env python3
"""
Local testing script for C4 Architecture Generator Chatbot.

This script helps you test the chatbot locally before deploying to Streamlit Cloud.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up"""
    print("🔍 Checking local environment...")
    
    # Check if we're in the right directory
    if not os.path.exists("c4_chatbot_ui.py"):
        print("❌ c4_chatbot_ui.py not found. Make sure you're in the with_ui directory.")
        return False
    
    # Check if requirements are installed
    try:
        import streamlit
        import langchain
        import openai
        print("✅ Required packages are installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("💡 Install requirements: pip install -r requirements.txt")
        return False
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OpenAI API key found in environment")
    else:
        print("⚠️  OpenAI API key not found in environment")
        print("💡 Set it with: export OPENAI_API_KEY='your-key-here'")
        print("💡 Or create a .env file with: OPENAI_API_KEY=your-key-here")
    
    return True

def run_streamlit():
    """Run the Streamlit app locally"""
    print("🚀 Starting Streamlit app...")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "c4_chatbot_ui.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")

def main():
    """Main function"""
    print("🏠 C4 Chatbot Local Testing")
    print("="*40)
    
    if check_environment():
        print("\n✅ Environment check passed")
        print("🌐 Starting local Streamlit server...")
        print("📱 Your app will be available at: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 40)
        
        run_streamlit()
    else:
        print("\n❌ Environment check failed")
        print("💡 Please fix the issues above before running locally")

if __name__ == "__main__":
    main()
