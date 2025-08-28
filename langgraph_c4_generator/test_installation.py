#!/usr/bin/env python3
"""
Test script to verify the C4 Architecture Diagram Generator installation
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    required_packages = [
        'langgraph',
        'langchain_openai',
        'pandas',
        'streamlit',
        'dotenv',
        'json',
        'os',
        're'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                importlib.import_module('dotenv')
            else:
                importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\nFailed to import: {', '.join(failed_imports)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    else:
        print("\nAll required packages imported successfully!")
        return True

def test_c4_generator_import():
    """Test if the C4 generator can be imported"""
    print("\nTesting C4 generator import...")
    
    try:
        from c4_with_excel_tech_spec import generate_c4_from_spec, C4State
        print("✓ C4 generator imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import C4 generator: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without API calls"""
    print("\nTesting basic functionality...")
    
    try:
        from c4_with_excel_tech_spec import C4State, build_c4_workflow
        
        # Test state creation
        state = C4State({
            "raw_spec": "Test specification",
            "components": None,
            "relationships": None,
            "missing_info": None,
            "summary": None,
            "dsl": None,
            "architecture_level": None
        })
        print("✓ C4State creation successful")
        
        # Test workflow building
        workflow = build_c4_workflow()
        print("✓ Workflow building successful")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_excel_processing():
    """Test Excel processing functionality"""
    print("\nTesting Excel processing...")
    
    try:
        from c4_with_excel_tech_spec import process_excel_file
        
        # Test with a non-existent file (should handle gracefully)
        result = process_excel_file("non_existent_file.xlsx")
        if "error" in result:
            print("✓ Excel error handling works correctly")
        else:
            print("✓ Excel processing function available")
        
        return True
    except Exception as e:
        print(f"✗ Excel processing test failed: {e}")
        return False

def check_environment():
    """Check environment variables and configuration"""
    print("\nChecking environment...")
    
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✓ OpenAI API key found (length: {len(api_key)})")
        return True
    else:
        print("⚠ OpenAI API key not found")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print("   Or create a .env file with: OPENAI_API_KEY=your-key-here")
        return False

def main():
    """Run all tests"""
    print("C4 Architecture Diagram Generator - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("C4 Generator Import", test_c4_generator_import),
        ("Basic Functionality", test_basic_functionality),
        ("Excel Processing", test_excel_processing),
        ("Environment Check", check_environment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The C4 generator is ready to use.")
        print("\nNext steps:")
        print("1. Set your OpenAI API key if not already done")
        print("2. Run examples: python example_usage.py")
        print("3. Start web interface: streamlit run c4_with_excel_tech_spec.py")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check Python version (3.8+ required)")
        print("3. Verify file permissions and paths")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
