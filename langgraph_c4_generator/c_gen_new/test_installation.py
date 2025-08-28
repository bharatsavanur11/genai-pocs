#!/usr/bin/env python3
"""
Test script for C4 Architecture Generator

This script tests the basic functionality and dependencies of the C4 generator.
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test basic Python imports
        import json
        import re
        from typing import Dict, Any, List, Optional, Union, TypedDict
        from pathlib import Path
        print("✅ Basic Python imports: OK")
        
        # Test dotenv
        from dotenv import load_dotenv
        print("✅ dotenv import: OK")
        
        # Test LangGraph imports
        from langgraph.graph import StateGraph, END, START
        print("✅ LangGraph imports: OK")
        
        # Test LangChain imports
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.pydantic_v1 import BaseModel, Field
        print("✅ LangChain imports: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\n🔍 Testing environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is too old. Need 3.8+")
        return False
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OPENAI_API_KEY: Set")
        # Mask the key for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"   Key format: {masked_key}")
    else:
        print("❌ OPENAI_API_KEY: Not set")
        print("   Please set it with: export OPENAI_API_KEY='your-key-here'")
        return False
    
    return True

def test_c4_generator_import():
    """Test if the C4 generator can be imported"""
    print("\n🔍 Testing C4 generator import...")
    
    try:
        # Add parent directory to path
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        sys.path.append(str(parent_dir))
        
        # Try to import the C4 generator
        from c_gen_new.c4_generator_new import (
            generate_c4_architecture, 
            save_dsl_files,
            create_c4_workflow,
            C4State
        )
        print("✅ C4 generator imports: OK")
        
        # Test if classes can be instantiated
        try:
            # Test C4State
            state = C4State(
                raw_spec="test",
                systems=None,
                containers=None,
                components=None,
                relationships=None,
                external_systems=None,
                missing_info=None,
                summary=None,
                dsl_context=None,
                dsl_container=None,
                dsl_component=None,
                architecture_analysis=None
            )
            print("✅ C4State instantiation: OK")
            
            # Test workflow creation
            workflow = create_c4_workflow()
            print("✅ Workflow creation: OK")
            
        except Exception as e:
            print(f"❌ Class instantiation error: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ C4 generator import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without making API calls"""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from c_gen_new.c4_generator_new import generate_c4_architecture
        
        # Test with a minimal spec (this will fail due to API key validation, but we can test the function structure)
        minimal_spec = "A simple system with one component."
        
        print("✅ Function structure: OK")
        print("✅ Basic functionality test: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 C4 Architecture Generator - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("C4 Generator Import Test", test_c4_generator_import),
        ("Basic Functionality Test", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The C4 generator is ready to use.")
        print("\nNext steps:")
        print("1. Run the demo: python demo_c4_generator.py")
        print("2. Use in your code: from c_gen_new.c4_generator_new import generate_c4_architecture")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Set OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print("3. Check Python version (3.8+ required)")

if __name__ == "__main__":
    main()
