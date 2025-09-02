#!/usr/bin/env python3
"""
Deployment script for C4 Architecture Generator Chatbot to Streamlit Cloud.

This script helps prepare your repository for Streamlit Cloud deployment by:
1. Checking repository structure
2. Validating configuration files
3. Providing deployment instructions
4. Testing local setup
"""

import os
import sys
from pathlib import Path
import subprocess
import json

def check_repository_structure():
    """Check if repository has the correct structure for deployment"""
    print("🔍 Checking repository structure...")
    
    required_files = [
        "c4_chatbot_ui.py",
        "c4_generator_new.py",
        "requirements.txt",
        ".gitignore"
    ]
    
    required_dirs = [
        ".streamlit"
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    for dir in required_dirs:
        if not os.path.exists(dir):
            missing_dirs.append(dir)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ Repository structure is correct")
    return True

def check_requirements_file():
    """Check if requirements.txt has all necessary dependencies"""
    print("📦 Checking requirements.txt...")
    
    required_packages = [
        "streamlit",
        "langchain",
        "langchain-openai",
        "python-dotenv",
        "pydantic"
    ]
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    missing_packages = []
    for package in required_packages:
        if package not in content:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages in requirements.txt: {missing_packages}")
        return False
    
    print("✅ requirements.txt is complete")
    return True

def check_gitignore():
    """Check if .gitignore includes necessary exclusions"""
    print("🔒 Checking .gitignore...")
    
    required_exclusions = [
        ".env",
        ".streamlit/secrets.toml",
        "*.pkl",
        "*.json"
    ]
    
    if not os.path.exists(".gitignore"):
        print("❌ .gitignore not found")
        return False
    
    with open(".gitignore", "r") as f:
        content = f.read()
    
    missing_exclusions = []
    for exclusion in required_exclusions:
        if exclusion not in content:
            missing_exclusions.append(exclusion)
    
    if missing_exclusions:
        print(f"❌ Missing exclusions in .gitignore: {missing_exclusions}")
        return False
    
    print("✅ .gitignore is properly configured")
    return True

def check_secrets_template():
    """Check if secrets template exists"""
    print("🔑 Checking secrets template...")
    
    secrets_file = ".streamlit/secrets.toml"
    if not os.path.exists(secrets_file):
        print("❌ .streamlit/secrets.toml not found")
        return False
    
    with open(secrets_file, "r") as f:
        content = f.read()
    
    if "your-openai-api-key-here" in content:
        print("⚠️  Secrets template found - remember to update with real API key")
        return True
    elif "OPENAI_API_KEY" in content:
        print("✅ Secrets file configured")
        return True
    else:
        print("❌ Secrets file missing OPENAI_API_KEY")
        return False

def check_git_status():
    """Check git status and provide guidance"""
    print("📋 Checking git status...")
    
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Not a git repository or git not available")
            return False
        
        if result.stdout.strip():
            print("⚠️  Uncommitted changes detected:")
            print(result.stdout)
            print("💡 Consider committing changes before deployment")
        else:
            print("✅ Working directory is clean")
        
        return True
        
    except FileNotFoundError:
        print("❌ Git not found - please install git")
        return False

def test_local_setup():
    """Test if the app can run locally"""
    print("🧪 Testing local setup...")
    
    try:
        # Check if we can import the main module
        sys.path.insert(0, ".")
        import c4_chatbot_ui
        print("✅ Main module imports successfully")
        
        # Check if API key manager works
        api_manager = c4_chatbot_ui.api_key_manager
        status = api_manager.get_api_key_status()
        print(f"✅ API key manager working - Status: {status['available']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def generate_deployment_instructions():
    """Generate step-by-step deployment instructions"""
    print("\n" + "="*60)
    print("🚀 STREAMLIT CLOUD DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    instructions = """
1. 📁 PREPARE YOUR REPOSITORY:
   - Ensure all files are committed and pushed to GitHub
   - Verify your repository is public (for free Streamlit Cloud)
   - Check that .streamlit/secrets.toml is NOT committed (should be in .gitignore)

2. 🔑 SET UP YOUR API KEY:
   - Get your OpenAI API key from: https://platform.openai.com/api-keys
   - Update .streamlit/secrets.toml with your real API key
   - Test locally to ensure it works

3. 🌐 DEPLOY TO STREAMLIT CLOUD:
   - Go to: https://share.streamlit.io/
   - Click "New app"
   - Select your GitHub repository
   - Set main file path to: with_ui/c4_chatbot_ui.py
   - Choose a custom URL (optional)
   - Click "Deploy!"

4. ⚙️ CONFIGURE SECRETS:
   - After deployment, go to your app's settings
   - Navigate to "Secrets" section
   - Add your OpenAI API key:
     OPENAI_API_KEY = "your-actual-api-key-here"
   - Save the secrets

5. ✅ VERIFY DEPLOYMENT:
   - Check deployment logs for errors
   - Test the app by visiting your Streamlit Cloud URL
   - Verify API key status in the sidebar

6. 🎉 SHARE YOUR APP:
   - Your app will be available at: https://your-app-name.streamlit.app
   - Share the URL with users
   - Monitor performance and usage
"""
    
    print(instructions)
    
    # Get current directory info
    current_dir = os.getcwd()
    repo_name = os.path.basename(current_dir)
    
    print(f"\n📊 DEPLOYMENT SUMMARY:")
    print(f"   Repository: {repo_name}")
    print(f"   Main file: with_ui/c4_chatbot_ui.py")
    print(f"   Current directory: {current_dir}")
    
    return True

def main():
    """Main deployment preparation function"""
    print("🚀 C4 Chatbot Streamlit Cloud Deployment Preparation")
    print("="*60)
    
    # Change to the with_ui directory if we're in the parent directory
    if os.path.exists("with_ui") and not os.path.exists("c4_chatbot_ui.py"):
        os.chdir("with_ui")
        print("📁 Changed to with_ui directory")
    
    # Run all checks
    checks = [
        ("Repository Structure", check_repository_structure),
        ("Requirements File", check_requirements_file),
        ("Gitignore Configuration", check_gitignore),
        ("Secrets Template", check_secrets_template),
        ("Git Status", check_git_status),
        ("Local Setup", test_local_setup)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📋 DEPLOYMENT READINESS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Your repository is ready for Streamlit Cloud deployment!")
        generate_deployment_instructions()
    else:
        print("⚠️  Please fix the failing checks before deploying")
        print("💡 Refer to the deployment guide for detailed instructions")
    
    print("\n📚 For detailed instructions, see: streamlit_deployment_guide.md")

if __name__ == "__main__":
    main()
